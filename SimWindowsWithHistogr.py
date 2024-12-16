import matplotlib.pyplot as plt
import openpyxl
from openpyxl.drawing.image import Image


class HistogramGenerator:
    def __init__(self, heterostructure):
        self.heterostructure = heterostructure

    def extract_data_from_ai(self):
        alpha_i_data = {}
        alpha_i_n = sum(map(lambda x: x[1], self.heterostructure.a_i))
        alpha_i_p = sum(map(lambda x: x[2], self.heterostructure.a_i))
        total_alpha_i = alpha_i_n + alpha_i_p

        alpha_i_data["alpha_i_n"] = alpha_i_n
        alpha_i_data["alpha_i_p"] = alpha_i_p
        alpha_i_data["alpha_i_total"] = total_alpha_i

        for layer in self.heterostructure.HS:
            layer_name = layer[0]
            n_sum = sum(ai[1] for ai in self.heterostructure.a_i if ai[0] <= layer[1])
            p_sum = sum(ai[2] for ai in self.heterostructure.a_i if ai[0] <= layer[1])
            alpha_i_data[layer_name] = n_sum + p_sum

        return alpha_i_data

    def extract_data_from_ros(self):
        """
        Извлекает данные из функции print_ros для создания гистограммы.
        """
        ros_data = {}
        total_resistance = sum(self.heterostructure.ro_i)
        ros_data["Rs_total"] = total_resistance

        for i, layer in enumerate(self.heterostructure.HS):
            ros_data[layer[0]] = self.heterostructure.ro_i[i]

        return ros_data

    def save_histogram_to_excel(self, data, sheet_name, output_excel):
        # Создание гистограммы
        labels = data.keys()
        values = data.values()

        plt.figure(figsize=(10, 6))
        plt.bar(labels, values, color='blue')
        plt.xlabel('Элементы', fontsize=12)
        plt.ylabel('Значения', fontsize=12)
        plt.title(f'Гистограмма {sheet_name}', fontsize=14)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        # Сохранение гистограммы как изображения
        histogram_path = f"{sheet_name}.png"
        plt.savefig(histogram_path)
        plt.close()

        # Создание Excel файла и добавление изображения
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = sheet_name

        # Добавление изображения на лист
        img = Image(histogram_path)
        img.anchor = 'A1'
        ws.add_image(img)

        # Сохранение Excel файла
        wb.save(output_excel)
        print(f"Гистограмма сохранена в файл: {output_excel}")


class RsCalculatorWithGist:
    def __init__(self, sim_hs):
        self.sim_hs = sim_hs
        self.histogram_generator = HistogramGenerator(self.sim_hs)

    def generate_histograms(self):
        self.sim_hs.load_carriers_conc()
        self.sim_hs.load_near_field()
        self.sim_hs.calculate_ai()
        self.sim_hs.calculate_ros()

        ai_data = self.histogram_generator.extract_data_from_ai()
        ros_data = self.histogram_generator.extract_data_from_ros()

        self.histogram_generator.save_histogram_to_excel(ai_data, "AI Гистограмма", "ai_histogram_output.xlsx")
        self.histogram_generator.save_histogram_to_excel(ros_data, "ROS Гистограмма", "ros_histogram_output.xlsx")

