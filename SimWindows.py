import os
import math
import itertools

class Heterostructure:
    def __init__(self, HS_file_path):
        self.HS_file_path = HS_file_path
        self.charge_carriers_file_path = os.path.split(HS_file_path)[0] + '\\Carriers.dat'
        self.near_field_file_path = os.path.split(HS_file_path)[0] + '\\NearField.dat'
        self.HS = self.load_HS(HS_file_path)
        self.near_field = ()
        self.carriers_conc = ()
        self.teta_e = 3e-18
        self.teta_p = 7e-18
        self.a_i = ()
        self.ro_i = ()
        self.thickness_HS = round(sum([i[1] for i in self.HS]), 6)
        """
        Название файла /_in_HS.txt

        Пример содержимого файла /_in_HS.txt
        
        p-contact 0.3   0.0  5e19   a 200 bulk
        p-emitter 0.7   0.6  1.5e18 a 800 bulk
        p-emitter 0.1   0.6  1e17   a 200 bulk
        p-wave    0.2   0.37 1e17   a 200 bulk
        p-wave    0.1   0.37 3e16   a 200 bulk
        barrier   0.019 0.20 2e16   a 150 bulk
        QW        0.01  0.04 2e16   d 100 qw
        barrier   0.019 0.20 2e16   d 150 bulk
        n-wave    0.5   0.37 1e17   d 400 bulk
        n-emitter 1.0   0.5  2e18   d 800 bulk
        n-contact 0.3   0.0  2e18   d 800 bulk
        """

    # Load files
    def load_HS(self, HS_file_path):
        HS = []
        with open(HS_file_path, 'r', encoding="utf-8") as file:
            for line in file:
                s = line.split()
                HS.append((s[0], round(float(s[1]), 4), round(float(s[2]), 3), float(s[3]), s[4], int(s[5]), s[6]))
        return tuple(HS)

    def load_near_field(self):
        near_field = []
        near_field.append((0.0, 0.0))
        with open(self.near_field_file_path, 'r', encoding='utf-8') as file:
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
                    a = (near_field[j+1][1] - near_field[j][1]) / (near_field[j+1][0] - near_field[j][0])
                    b = near_field[j][1] - a * near_field[j][0]
        """
        file_path = os.path.split(self.HS_file_path)[0] + "\\out_n_f.txt"
        with open(file_path, 'w', encoding='utf-8') as file:
            for i in ans:
                file.write(str(i[0]) + ' ' + str(i[1]) + '\n')
        """
        #print(len(ans), len(self.carriers_conc))
        #print(ans[-1], self.carriers_conc[-1])
        self.near_field = tuple(ans)

    def load_carriers_conc(self):
        # x, n, p
        charge_carriers = []
        with open(self.charge_carriers_file_path, 'r', encoding='utf-8') as file:
            file.readline()
            for line in file:
                charge_carriers.append(tuple((float(i) for i in line.split(','))))
        self.carriers_conc = tuple(charge_carriers)

    # создание файла для Wave
    def calc_refr_index(self, wavelength, x):
        """
        Sadao Adachi J.Appl.Phys., Vol.58, No.3, (1985)
        """
        A = 6.3 + 19.0 * x
        B = 9.4 - 10.2 * x
        Eg = 1.425 + 1.155 * x + 0.37 * x * x
        Eg_so = 1.765 + 1.115 * x + 0.37 * x * x
        
        xi = 1.2398 / (wavelength * Eg)
        xi_so = 1.2398 / (wavelength * Eg_so)
        
        f = (2 - pow(1 + xi, 0.5) - pow(1 - xi, 0.5)) / (xi * xi)
        f_so = (2 - pow(1 + xi_so, 0.5) - pow(1 - xi_so, 0.5)) / (xi_so * xi_so)
        
        n = pow(A * (f + f_so * pow(Eg / Eg_so, 1.5) / 2) + B, 0.5)
        if n.imag:
            n = n.real
        return n

    def create_files_for_Wave(self, file_name1='\\_code_for_Wave.wg', file_name2='\\_code_for_Wave.wgs'):
        file_path_wave1 = os.path.split(self.HS_file_path)[0] + file_name1
        file_path_wave2 = os.path.split(self.HS_file_path)[0] + file_name2
            
        with open(file_path_wave1, 'w', encoding="utf-8") as file:
            file.write('Waveguide structure\n')
            file.write('0.808 0 2.0\n')
            file.write('0.1' + ' ' + str(self.calc_refr_index(0.808, 0.0)) + ' ' + '1' + ' ' + '0\n')
            for i in self.HS:
                if i[-1] == 'qw':
                    file.write(str(i[1]) + ' ' + str(self.calc_refr_index(0.808, i[2])) + ' ' + '-1000' + ' ' + '1\n')
                else:
                    file.write(str(i[1]) + ' ' + str(self.calc_refr_index(0.808, i[2])) + ' ' + '1' + ' ' + '0\n')
            file.write('0.1' + ' ' + str(self.calc_refr_index(0.808, 0.0)) + ' ' + '1' + ' ' + '0\n')
                
        with open(file_path_wave2, 'w', encoding="utf-8") as file:
            file.write('1500 0.10 0.95\n')
            file.write('0.5 0.5\n')
            file.write('-90 90\n')
            file.write('-30.0 30.0\n')
            file.write('200.00 20.00\n')
            file.write('200.00 0.95 2000.00\n')

    # создание файла для SimWindows
    def write_heterostructure(self):
        """Создает краткое описание исследуемой гетероструктуры"""
        ans = ''
        for layer in self.HS:
            ans += '# {:10}  d={:<7}  x={:<6} doping={:<8} {:<2} points={:<4}  {}\n'.format(*layer)
        ans += '# d_HS=' + str(self.thickness_HS) + '\n'
        return ans + '\n'

    def create_grid(self):
        """Создает сетку"""
        ans = ''
        for layer in self.HS:
            ans += 'grid length={0} points={1}\n'.format(layer[1], layer[5])
        return ans + '\n'

    def create_material(self):
        """Содает слои ГС с заданным мольным составом"""
        ans = ''
        d = 0.0
        for i, layer in enumerate(self.HS):
            ans += 'structure material=M' + str(i+1) + ' length={0}\n'.format(layer[1])
            d += layer[1]
            if (i + 1) != len(self.HS) and self.HS[i + 1][-1] == 'qw':
                ans += 'region bulk length={}\n'.format(round(d, 5))
                d = 0.0
            elif (i + 1) != len(self.HS) and self.HS[i][-1] == 'qw' and self.HS[i + 1][-1] == 'bulk':
                ans += 'region qw length={}\n'.format(round(d, 5))
                d = 0.0
            elif (i + 1) == len(self.HS):
                ans += 'region bulk length={}\n'.format(round(d, 5))
        return ans + '\n'

    def create_simple_doping_profile(self):
        ans = ''
        for layer in self.HS:
            ans += 'doping length={0} N{1}={2}\n'.format(layer[1], layer[4], layer[3])
        return ans + '\n'
    
    def create_file_for_SimWindows(self, file_name='\\_code_for_SimWindows.dev'):
        file_path = os.path.split(self.HS_file_path)[0] + file_name
        with open(file_path, 'w', encoding="utf-8") as file:
            file.write(self.write_heterostructure())
            file.write(self.create_grid())
            file.write(self.create_material())
            file.write(self.create_simple_doping_profile())

    # создание файла MATERIAL.PRM
    def calculate_mun(self, x, N, T=300.0):
        if x > 1.0:
            raise ValueError("0 <= x <= 1 def calculate_mun")
        
        N_ref_GaAs = 6e16
        N_ref_AlAs = 5.46e17
        Nref = math.pow( N_ref_GaAs, 1-x)*math.pow( N_ref_AlAs, x)

        teta1_GaAs = 2.1
        teta1_AlAs = 2.1
        m = 1.0
        teta1 = ((1 - x) * teta1_GaAs + x * teta1_AlAs) / (1 + m * (1 - x))

        #teta2_GaAs = 3.0
        #teta2_AlAs = 3.0
        #m = 1.0
        #teta2 = ((1 - x) * teta2_GaAs + x * teta2_AlAs) / (1 + m * (1 - x))
        teta2 = 3.0

        mu_max = 0.0
        if x < 0.45:
            mu_max = 8000.0 - 22000.0 * x + 10000.0 * x * x
        else:
            mu_max = -255.0 + 1160.0 * x - 720.0 * x * x

        wam_GaAs = 0.394
        wam_AlAs = 1.000
        wam = wam_GaAs * (1 - x) + x * wam_AlAs
        #print(wam)

        mu_min = 0.0
        if x < 0.45:
            mu_min = (8000.0 - 22000.0 * x + 10000.0 * x * x) * 0.0625
        else:
            mu_min = (-255.0 + 1160.0 * x - 720.0 * x * x) * 0.0625
        #print(mu_max, mu_min)

        ans = mu_min + (mu_max * math.pow(300.0 / T, teta1) - mu_min) / (1 + math.pow(N / (Nref * math.pow(T/300, teta2)), wam))
        return ans

    def calculate_mup(self, x, N, T=300.0):
        if x > 1.0:
            raise ValueError("0 <= x <= 1 def calculate_mun")
        
        N_ref_GaAs = 1.48e17
        N_ref_AlAs = 3.84e17
        Nref = math.pow( N_ref_GaAs, 1-x)*math.pow( N_ref_AlAs, x)

        teta1_GaAs = 2.2
        teta1_AlAs = 2.24
        m = 1.0
        teta1 = ((1 - x) * teta1_GaAs + x * teta1_AlAs) / (1 + m * (1 - x))

        #teta2_GaAs = 3.0
        #teta2_AlAs = 3.0
        #m = 1.0
        #teta2 = ((1 - x) * teta2_GaAs + x * teta2_AlAs) / (1 + m * (1 - x))
        teta2 = 3.0

        mu_max = 370 - 970.0 * x + 740.0 * x * x

        wam_GaAs = 0.394
        wam_AlAs = 1.000
        wam = wam_GaAs * (1 - x) + x * wam_AlAs
        #print(wam)

        mu_min = (mu_max) * 0.053
        #print(mu_max, mu_min)

        ans = mu_min + (mu_max * math.pow(300.0 / T, teta1) - mu_min) / (1 + math.pow(N / (Nref * math.pow(T/300, teta2)), wam))
        return ans
    
    def creat_Material_file(self, file_name='\\MATERIAL.PRM'):
        file_path = os.path.split(self.HS_file_path)[0] + file_name
        with open (file_path, 'w', encoding="utf-8") as file:
            for i in range(len(self.HS)):
                x = self.HS[i][2]
    
                file.write('Material=M' + str(i+1) + '\n')
                file.write('Alloy=Default\n\n')
                file.write('BAND_GAP Value=' + \
                            str(1.424+1.247*x if x < 0.45 else 1.9+0.125*x+0.143*x*x) + \
                            '\n')
                file.write('ELECTRON_AFFINITY Value=' + \
                            str(4.07-0.7482*x if x < 0.45 else 3.594+0.3738*x-0.143*x*x) + \
                            '\n')
                file.write('STATIC_PERMITIVITY Value=' + str(13.18 - 3.12*x) + '\n\n')
                file.write('REFRACTIVE_INDEX Value=' + str(self.calc_refr_index(0.808, x)) + '\n')
                file.write('ABSORPTION Segments=6\n')
                file.write('start_e=0 end_e=g value=0\n')
                file.write('start_e=g end_e=g+1 value=2.698e3+8.047e4*(e-g)-6.241e4*(e-g)^2+7.326e4*(e-g)^3\n')
                file.write('start_e=g+1 end_e=g+1.4 value=-3.218e6+9.060e6*(e-g)-8.428e6*(e-g)^2+2.681e6*(e-g)^3\n')
                file.write('start_e=g+1.4 end_e=g+1.9 value=-1.615e7+2.600e7*(e-g)-1.338e7*(e-g)^2+2.303e6*(e-g)^3\n')
                file.write('start_e=g+1.9 end_e=g+2.6 value=8.383e5+2.442e5*(e-g)-3.226e5*(e-g)^2+8.482e4*(e-g)^3\n')
                file.write('start_e=g+2.6 end_e=g+4.0 value=7.83e5\n\n')
                file.write('THERMAL_CONDUCTIVITY Value=' + str(0.55-2.12*x+2.48*x*x) + '\n')
                file.write('DERIV_THERMAL_CONDUCT Value=1\n\n')               
                file.write('ELECTRON_MOBILITY Value=' + str(self.calculate_mun(x, self.HS[i][1])) + '\n')
                file.write('HOLE_MOBILITY Value=' + str(self.calculate_mup(x, self.HS[i][1])) + '\n')
                file.write('ELECTRON_DOS_MASS Value=' + \
                           str(0.067+0.083*x if x < 0.45 else 0.85-0.14*x) + '\n')
                file.write('HOLE_DOS_MASS Value=' + \
                           str(0.62+0.14*x) + '\n')
                file.write('ELECTRON_COND_MASS Value=' + \
                           str(0.067+0.083*x if x < 0.45 else 0.32-0.06*x) + '\n')
                file.write('HOLE_COND_MASS Value=' + \
                           str(0.62+0.14*x) + '\n\n')
                file.write('ELECTRON_SHR_LIFETIME Value=1e-8\n')
                file.write('HOLE_SHR_LIFETIME Value=1e-8\n')
                file.write('ELECTRON_AUGER_COEFFICIENT Value=1.5e-31\n')
                file.write('QW_ELECTRON_AUGER_COEFFICIENT Value=1.5e-19\n')
                file.write('HOLE_AUGER_COEFFICIENT Value=1.5e-31\n')
                file.write('QW_HOLE_AUGER_COEFFICIENT Value=1.5e-19\n')
                file.write('RAD_RECOMB_CONST Value=1.5e-10\n')
                file.write('ELECTRON_ENERGY_LIFETIME Value=1.e-12\n')
                file.write('HOLE_ENERGY_LIFETIME Value=1.e-12\n')
                file.write('QW_RAD_RECOMB_CONST Value=1.54e-4\n')
                file.write('ELECTRON_COLLISION_FACTOR Value=0.5\n')
                file.write('HOLE_COLLISION_FACTOR Value=0.5\n\n')
                
                file.write('#___________________________________________________________________\n')

    # расчет поглощения на свободных носителях заряда
    def calculate_ai(self):
        a_ik = []
        for i in self.carriers_conc:
            a_ik.append((i[0], self.teta_e*i[1], self.teta_p*i[2]))
        """
        file_path = os.path.split(self.HS_file_path)[0] + "\\out_alpha_i.txt"
        with open(file_path, 'w', encoding='utf-8') as file:
            for i in a_ik:
                file.write(str(i[0]) + ' ' + str(i[1]) + ' ' + str(i[2]) + '\n')
        """
        Gk = []
        for i in range(len(self.near_field) - 1):
            Gk.append((self.near_field[i][0], 
                      (self.near_field[i][1] + self.near_field[i + 1][1]) * (self.near_field[i + 1][0] - self.near_field[i][0]) / 2))
        Gk.append(Gk[-1])
        
        main_G = sum(map(lambda x: x[1], Gk))
        Gk = tuple(map(lambda x: (x[0], x[1] / main_G), Gk))
        #print(len(a_ik), len(Gk), len(self.carriers_conc))
        """
        file_path = os.path.split(self.HS_file_path)[0] + "\\out_Gk.txt"
        with open(file_path, 'w', encoding='utf-8') as file:
            for i in Gk:
                file.write(str(i[0]) + ' ' + str(i[1]) + '\n')
        """
        a_i = []
        for i in range(len(self.near_field)):
            a_i.append((Gk[i][0], Gk[i][1]*a_ik[i][1], Gk[i][1]*a_ik[i][2]))
        """
        file_path = os.path.split(self.HS_file_path)[0] + "\\out_a_i.txt"
        with open(file_path, 'w', encoding='utf-8') as file:
            for i in a_i:
                file.write(str(i[0]) + ' ' + str(i[1]) + ' ' + str(i[2]) + '\n')
        """ 
        self.a_i = tuple(a_i)

    def print_ai(self):
        print('_______________________ai_______________________')
        alpha_i_n = sum(map(lambda x: x[1], self.a_i))
        alpha_i_p = sum(map(lambda x: x[2], self.a_i))
        print('alpha_i_n = ', round(alpha_i_n, 5), 'cm-1')
        print('alpha_i_p = ', round(alpha_i_p, 5), 'cm-1')
        print('alpha_i =   ', round(alpha_i_p + alpha_i_n, 5), 'cm-1')
        print()

        print('              n       p       n+p')
        #ai_n = []
        #ai_p = []
        ans_n = 0.0
        ans_p = 0.0
        counts = 0
        d = 0.0
        for j in range(len(self.HS)):
            d += self.HS[j][1]
            #print(d)
            for i in itertools.count(counts):
                #print(i)
                if (self.a_i[i][0] <= d) and (i < len(self.a_i)-1):
                    ans_n += self.a_i[i][1]
                    ans_p += self.a_i[i][2]
                else:
                    counts = i
                    #print(i)
                    #ai_n.append(ans_n)
                    #ai_p.append(ans_p)
                    print('{:10}  {:5}  {:5}  {:5}'.format(self.HS[j][0], round(ans_n, 5), round(ans_p, 5), round(ans_n + ans_n, 5)))
                    ans_n = 0.0
                    ans_p = 0.0
                    break
        print('______________________________________________')

    # расчет последовательного сопротивления
    def calculate_ros(self):
        q = 1.6022e-19
        ro_i = []
        ans = 0.0

        for i in range(len(self.HS)):
            if self.HS[i][4] == 'a':
                ro_i.append(1e4 * self.HS[i][1] / (150000 * q * self.HS[i][3] * self.calculate_mup(self.HS[i][2], self.HS[i][3])))
            else:
                ro_i.append(1e4 * self.HS[i][1] / (150000 * q * self.HS[i][3] * self.calculate_mun(self.HS[i][2], self.HS[i][3])))

        self.ro_i = tuple(ro_i)

    def print_ros(self):
        print('_____________________Rs_________________________')
        print('Rs = ', round(sum(self.ro_i), 8), 'Om')
        print()
        for i in range(len(self.ro_i)):
            print('{:10}  {:5}'.format(self.HS[i][0], round(self.ro_i[i], 6)))
        print('______________________________________________')


if __name__ == '__main__':
    try:
        #__file__ = "E:\\SimWindows+Wave\\_HS.txt"
        HS_file_path = os.path.split(__file__)[0] + '\\_HS.txt'
        HS = Heterostructure(HS_file_path)
        HS.create_files_for_Wave()
        HS.create_file_for_SimWindows()
        HS.creat_Material_file()
        print('Success')
        input()
    except BaseException as err:
        print(err)
        input()
"""

if __name__ == '__main__':
    #try:
        __file__ = "E:\\SimWindows+Wave\\_HS.txt"
        HS_file_path = os.path.split(__file__)[0] + '\\_HS.txt'
        HS = Heterostructure(HS_file_path)
        HS.load_carriers_conc()
        HS.load_near_field()
        HS.calculate_ai()
        HS.print_ai()
    
        HS.calculate_ros()
        HS.print_ros()
        print('Success')
        #input()
    #except BaseException as err:
        #print(err)
        #input()
"""