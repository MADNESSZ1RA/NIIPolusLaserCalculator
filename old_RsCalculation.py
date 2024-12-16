import os
import math
import itertools


class Heterostructure:
    def __init__(self, HS_file_path, DP_file_path, near_field_file_path, charge_carriers_file_path):
        self.HS_file_path = HS_file_path
        self.HS = self.load_HS(HS_file_path)
        self.thickness_HS = round(sum([i[1] for i in self.HS]), 3)
        """
        Название файла /_in_HS.txt

        Пример содержимого файла /_in_HS.txt
        
        p-contact 0.3  0.0  200 bulk
        p-emitter 0.8  0.6  800 bulk
        p-wave    0.3  0.4  400 bulk
        QW        0.01 0.04 100 qw
        n-wave    0.5  0.4  400 bulk
        n-emitter 1.0  0.6  800 bulk
        n-contact 0.3  0.0  200 bulk
        """
        self.DP_file_path = DP_file_path
        self.DP = self.load_DP(DP_file_path)
        self.thickness_DP = round(sum([i[0] for i in self.DP]), 3)
        """
        Название файла /_in_DP.txt
        
        Пример содержимого файла /_in_DP.txt
        
        0.3   5e19    a
        0.8   1.5e18  a
        0.3   1e17    a
        0.01  2e16    d
        0.5   1e17    d
        1.0   2e18    d
        0.3   2e18    d
        """
        if not math.isclose(self.thickness_HS, self.thickness_DP):
            print(self.thickness_HS, self.thickness_DP)
            raise ValueError("Проверь толщины в _in_HS.txt и _in_DP.txt")

        self.carriers_conc = self.load_carriers_conc(charge_carriers_file_path)
        self.near_field = self.load_near_field(near_field_file_path)
        self.teta_e = 3e-18
        self.teta_p = 7e-18
        self.a_i = self.calculate_ai()
        self.ro_i = self.calculate_ros()

    def load_HS(self, HS_file_path):
        HS = []
        with open(HS_file_path, 'r', encoding="utf-8") as file:
            for line in file:
                s = line.split()
                HS.append((s[0], round(float(s[1]), 3), round(float(s[2]), 2), int(s[3]), s[4]))
        for i in HS:
            print(i)
        print()
        return tuple(HS)

    def load_DP(self, DP_file_path):
        DP = []
        with open(DP_file_path, 'r', encoding="utf-8") as file:
            for line in file:
                s = line.split()
                DP.append((round(float(s[0]), 3), float(s[1]), s[2]))
        for i in DP:
            print(i)
        print()
        return tuple(DP)

    def load_near_field(self, near_field_file_path):
        near_field = []
        near_field.append((0.0, 0.0))
        with open(near_field_file_path, 'r', encoding='utf-8') as file:
            for line in file:
                ans = tuple((float(i) for i in line.split()))
                if ans[0] > 0:
                    near_field.append(ans)

        ans = []
        count = 1
        a = (near_field[1][1] - near_field[0][1]) / (near_field[1][0] - near_field[0][0])
        b = near_field[0][1] - a * near_field[0][0]
        y = 0.0
        x = 0.0
        for i in range(len(self.carriers_conc)):
            for j in itertools.count(count):
                if near_field[j][0] >= self.carriers_conc[i][0]:
                    x = self.carriers_conc[i][0]
                    y = a * x + b
                    ans.append((x, y))
                    break
                else:
                    count = j + 1
                    a = (near_field[j + 1][1] - near_field[j][1]) / (near_field[j + 1][0] - near_field[j][0])
                    b = near_field[j][1] - a * near_field[j][0]
        """
        file_path = os.path.split(self.HS_file_path)[0] + "\\out_n_f.txt"
        with open(file_path, 'w', encoding='utf-8') as file:
            for i in ans:
                file.write(str(i[0]) + ' ' + str(i[1]) + '\n')
        """
        # print(len(ans), len(self.carriers_conc))
        # print(ans[-1], self.carriers_conc[-1])
        return tuple(ans)

    def load_carriers_conc(self, charge_carriers_file_path):
        # x, n, p
        charge_carriers = []
        with open(charge_carriers_file_path, 'r', encoding='utf-8') as file:
            file.readline()
            for line in file:
                charge_carriers.append(tuple((float(i) for i in line.split(','))))
        return tuple(charge_carriers)

    def calculate_ai(self):
        a_ik = []
        for i in self.carriers_conc:
            a_ik.append((i[0], self.teta_e * i[1], self.teta_e * i[2]))
        """
        file_path = os.path.split(self.HS_file_path)[0] + "\\out_alpha_i.txt"
        with open(file_path, 'w', encoding='utf-8') as file:
            for i in a_ik:
                file.write(str(i[0]) + ' ' + str(i[1]) + ' ' + str(i[2]) + '\n')
        """
        Gk = []
        for i in range(len(self.near_field) - 1):
            Gk.append((self.near_field[i][0],
                       (self.near_field[i][1] + self.near_field[i + 1][1]) * (
                                   self.near_field[i + 1][0] - self.near_field[i][0]) / 2))
        Gk.append(Gk[-1])

        main_G = sum(map(lambda x: x[1], Gk))
        Gk = tuple(map(lambda x: (x[0], x[1] / main_G), Gk))
        # print(len(a_ik), len(Gk), len(self.carriers_conc))
        """
        file_path = os.path.split(self.HS_file_path)[0] + "\\out_Gk.txt"
        with open(file_path, 'w', encoding='utf-8') as file:
            for i in Gk:
                file.write(str(i[0]) + ' ' + str(i[1]) + '\n')
        """
        a_i = []
        for i in range(len(self.near_field)):
            a_i.append((Gk[i][0], Gk[i][1] * a_ik[i][1], Gk[i][1] * a_ik[i][2]))
        """
        file_path = os.path.split(self.HS_file_path)[0] + "\\out_a_i.txt"
        with open(file_path, 'w', encoding='utf-8') as file:
            for i in a_i:
                file.write(str(i[0]) + ' ' + str(i[1]) + ' ' + str(i[2]) + '\n')
        """
        return tuple(a_i)

    def print_ai(self):
        print('_______________________ai_______________________')
        alpha_i_n = sum(map(lambda x: x[1], self.a_i))
        alpha_i_p = sum(map(lambda x: x[2], self.a_i))
        print('alpha_i_n = ', round(alpha_i_n, 5))
        print('alpha_i_p = ', round(alpha_i_p, 5))
        print('alpha_i =   ', round(alpha_i_p + alpha_i_n, 5))
        print()

        ai_n = []
        ai_p = []
        ans_n = 0.0
        ans_p = 0.0
        counts = 0
        d = 0.0
        for j in range(len(self.HS)):
            d += self.HS[j][1]
            # print(d)
            for i in itertools.count(counts):
                # print(i)
                if (self.a_i[i][0] <= d) and (i < len(self.a_i) - 1):
                    ans_n += self.a_i[i][1]
                    ans_p += self.a_i[i][2]
                else:
                    counts = i
                    # print(i)
                    ai_n.append(ans_n)
                    ai_p.append(ans_p)
                    # print(self.HS[j][0], round(ans_n, 5) , round(ans_p, 5))
                    print('{:10}  {:5}  {:5}'.format(self.HS[j][0], round(ans_n, 5), round(ans_p, 5)))
                    ans_n = 0.0
                    ans_p = 0.0
                    break

        print()
        for i in range(len(ai_n)):
            print('{:10} {:5}'.format(self.HS[i][0], round(ai_n[i] + ai_p[i], 5)))
        print('______________________________________________')

    def calculate_mun(self, x, N, T=300.0):
        if x > 1.0:
            raise ValueError("0 <= x <= 1")

        N_ref_GaAs = 6e16
        N_ref_AlAs = 5.46e17
        Nref = math.pow(N_ref_GaAs, 1 - x) * math.pow(N_ref_AlAs, x)

        teta1_GaAs = 2.1
        teta1_AlAs = 2.1
        m = 1.0
        teta1 = ((1 - x) * teta1_GaAs + x * teta1_AlAs) / (1 + m * (1 - x))

        # teta2_GaAs = 3.0
        # teta2_AlAs = 3.0
        # m = 1.0
        # teta2 = ((1 - x) * teta2_GaAs + x * teta2_AlAs) / (1 + m * (1 - x))
        teta2 = 3.0

        mu_max = 0.0
        if x < 0.45:
            mu_max = 8000.0 - 22000.0 * x + 10000.0 * x * x
        else:
            mu_max = -255.0 + 1160.0 * x - 720.0 * x * x

        wam_GaAs = 0.394
        wam_AlAs = 1.000
        wam = wam_GaAs * (1 - x) + x * wam_AlAs
        # print(wam)

        mu_min = 0.0
        if x < 0.45:
            mu_min = (8000.0 - 22000.0 * x + 10000.0 * x * x) * 0.0625
        else:
            mu_min = (-255.0 + 1160.0 * x - 720.0 * x * x) * 0.0625
        # print(mu_max, mu_min)

        ans = mu_min + (mu_max * math.pow(300.0 / T, teta1) - mu_min) / (
                    1 + math.pow(N / (Nref * math.pow(T / 300, teta2)), wam))
        return ans

    def calculate_mup(self, x, N, T=300.0):
        if x > 1.0:
            raise ValueError("0 <= x <= 1")

        N_ref_GaAs = 1.48e17
        N_ref_AlAs = 3.84e17
        Nref = math.pow(N_ref_GaAs, 1 - x) * math.pow(N_ref_AlAs, x)

        teta1_GaAs = 2.2
        teta1_AlAs = 2.24
        m = 1.0
        teta1 = ((1 - x) * teta1_GaAs + x * teta1_AlAs) / (1 + m * (1 - x))

        # teta2_GaAs = 3.0
        # teta2_AlAs = 3.0
        # m = 1.0
        # teta2 = ((1 - x) * teta2_GaAs + x * teta2_AlAs) / (1 + m * (1 - x))
        teta2 = 3.0

        mu_max = 370 - 970.0 * x + 740.0 * x * x

        wam_GaAs = 0.394
        wam_AlAs = 1.000
        wam = wam_GaAs * (1 - x) + x * wam_AlAs
        # print(wam)

        mu_min = (mu_max) * 0.053
        # print(mu_max, mu_min)

        ans = mu_min + (mu_max * math.pow(300.0 / T, teta1) - mu_min) / (
                    1 + math.pow(N / (Nref * math.pow(T / 300, teta2)), wam))
        return ans

    def calculate_ros(self):
        q = 1.6022e-19
        ro_i = []
        ans = 0.0
        d_HS = self.HS[0][1]
        j = 0
        d_DP = 0.0
        x = 0.0
        for i in range(len(self.DP)):
            d_DP += self.DP[i][0]
            # print(i, j)
            # print(d_DP, d_HS)
            if math.isclose(d_DP, d_HS) or (d_DP < d_HS):
                x = self.HS[j][2]
            else:
                j += 1
                x = self.HS[j][2]
                d_HS += self.HS[j][1]

            if self.DP[i][2] == 'a':
                ro_i.append((self.DP[i][0], 1e4 * self.DP[i][0] / (
                            150000 * q * self.DP[i][1] * self.calculate_mup(self.HS[j][2], self.DP[i][1]))))
            else:
                ro_i.append((self.DP[i][0], 1e4 * self.DP[i][0] / (
                            150000 * q * self.DP[i][1] * self.calculate_mun(self.HS[j][2], self.DP[i][1]))))

            # ro_i = tuple(map(lambda g: (g[0], g[1] * main_G), ro_i))
            # print(i, j)
            # print(d_DP, d_HS)
        return tuple(ro_i)

    def print_ros(self):
        print('_____________________Rs_________________________')
        for i in range(len(self.ro_i)):
            print('{:5}  {:5}'.format(self.ro_i[i][0], round(self.ro_i[i][1], 6)))
        print()
        print('Rs = ', sum(map(lambda x: x[1], self.ro_i)))
        print('______________________________________________')


if __name__ == '__main__':
    try:
        # __file__ = "E:\\SimWindows+Wave\\_HS.txt"
        HS_file_path = os.path.split(__file__)[0] + '\\_HS.txt'
        DP_file_path = os.path.split(__file__)[0] + '\\_simple_DP.txt'
        NF_file_path = os.path.split(__file__)[0] + '\\NearField.dat'
        CC_file_path = os.path.split(__file__)[0] + '\\2.0.dat'
        HS = Heterostructure(HS_file_path, DP_file_path, NF_file_path, CC_file_path)
        # HS = Heterostructure("G:\\SimWindows+Wave\\_HS.txt",
        #             "G:\\SimWindows+Wave\\_simple_DP.txt", 
        #             "G:\\SimWindows+Wave\\NearField.dat", 
        #             "G:\\SimWindows+Wave\\2.0.dat")
        HS.print_ai()
        HS.print_ros()
        print('Success')
        input()
    except BaseException as err:
        print(err)
        input()
