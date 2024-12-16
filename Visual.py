import os
import tkinter
import tkinter.messagebox
import customtkinter as Ctk
from customtkinter import *
from SimWindows import Heterostructure as SimHS
from SimWindowsWithHistogr import RsCalculatorWithGist as RsWithGist
from RsCalculation import Heterostructure as RsHs
from pathlib import Path


class WindowSettings():
    textbox_settings = {
        'bg_color': "white",
        'fg_color': "white",
        'border_color': "black",
        'border_width': 2,
        'text_color': 'black'}
    button_settings = {
        'width': 150,
        'height': 30,
        'bg_color': 'white',
        'fg_color': 'black',
        'text_color': 'white',
        'hover': True,
        'hover_color': 'gray',
    }


class App(Ctk.CTk):
    def __init__(self):
        super().__init__()

        # Настройка окна
        self.title('Simgen')
        self.geometry(f'{549}x{700}')
        self.resizable(False, False)

        # Левая и правая рамки
        self.left_frame = Ctk.CTkFrame(self, width=550, height=700, bg_color='white', fg_color='white',
                                       border_color='black', border_width=2).place(x=0, y=0)
        self.right_frame = Ctk.CTkFrame(self, width=550, height=700, bg_color='white', fg_color='white',
                                        border_color='black', border_width=2).place(x=550, y=0)

        self.thirst_header = Ctk.CTkLabel(self.left_frame, text='Генерация файлов', bg_color='white',
                                          text_color='black',
                                          width=540, height=30)
        self.thirst_header.place(x=5, y=3)
        self.open_btn = Ctk.CTkButton(self.left_frame, **WindowSettings.button_settings, text='Открыть',
                                      command=self.GetFilePath).place(
            x=25, y=50)
        self.save_btn = Ctk.CTkButton(self.left_frame, **WindowSettings.button_settings, text='Сохранить',
                                      command=self.SaveHSFile).place(
            x=375, y=50)
        self.file_name_label = Ctk.CTkLabel(self.left_frame, bg_color='white', anchor='w', text='Название файла',
                                            width=500,
                                            height=30, text_color='black')
        self.file_name_label.place(x=25, y=100)
        self.file_path_textbox = Ctk.CTkTextbox(self.left_frame, **WindowSettings.textbox_settings, width=500,
                                                height=30)
        self.file_path_textbox.place(x=25, y=150)
        self.file_path_textbox.insert(0.0, 'Путь к файлу')
        self.file_content_label = Ctk.CTkLabel(self.left_frame, bg_color='white', text='Содержимое файла',
                                               text_color='black')
        self.file_content_label.place(x=25, y=200)
        self.file_content_label.configure(text='Выберите файл для просмотра содержимого')
        self.file_content_textbox = Ctk.CTkTextbox(self.left_frame, **WindowSettings.textbox_settings, width=500,
                                                   height=350)
        self.file_content_textbox.place(x=25, y=250)
        self.generate_btn = Ctk.CTkButton(self.left_frame, **WindowSettings.button_settings,
                                          text='Сгенерировать файл для SimWindows Wave',
                                          command=self.SimGenerator).place(x=25, y=600)

        self.second_header = Ctk.CTkLabel(self.right_frame, text='Обработка', bg_color='white', text_color='black',
                                          corner_radius=2,
                                          width=530, height=30)
        self.second_header.place(x=5, y=600)
        self.upload_btn = Ctk.CTkButton(self.right_frame, **WindowSettings.button_settings,
                                        text='Подгрузить Carriers.dat и NearField.dat',
                                        command=self.RsCalculator).place(x=25, y=650)

        self.generate_gist_btn = Ctk.CTkButton(self.right_frame, **WindowSettings.button_settings,
                                               text="Создать гистограмму", command=self.RsCalculatorWithGist).place(
            x=375, y=650)

    def GetFilePath(self):
        self.path_to_file = filedialog.askopenfilename(
            filetypes=[('Txt files', '*.txt')],
            initialdir=Path.home() / 'Desktop',
            title='Выберите текстовый файл'
        )
        if self.path_to_file:
            with open(self.path_to_file, 'r', encoding='utf-8') as f:
                self.filename = os.path.basename(self.path_to_file)
                self.file_name_label.configure(text=f'Название файла: {self.filename}')
                self.file_content_label.configure(text=f'Содержимое файла {self.filename}:')
                self.file_path_textbox.delete('1.0', 'end')
                self.file_path_textbox.insert('1.0', f'Выбранный файл: {self.path_to_file}')

                file_content = f.read()
                self.file_content_textbox.delete('1.0', 'end')
                self.file_content_textbox.insert('1.0', file_content)

    def SaveHSFile(self):
        file_path = self.file_path_textbox.get('1.0', 'end').strip().replace('Выбранный файл: ', '')

        if not os.path.exists(file_path):
            tkinter.messagebox.showerror("Ошибка", f"Файл не найден: {file_path}")
            return

        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file_content = self.file_content_textbox.get("1.0", "end").strip()
                file.write(file_content)
            tkinter.messagebox.showinfo("Успех", "Файл успешно сохранён.")
        except Exception as e:
            tkinter.messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")

    def SimGenerator(self):
        HS_file_path = self.file_path_textbox.get('1.0', 'end').strip().replace('Выбранный файл: ', '')

        HS = RsHs(HS_file_path)
        HS.create_files_for_Wave()
        HS.create_file_for_SimWindows()
        HS.creat_Material_file()

    def RsCalculator(self):
        HS = SimHS(os.path.split(__file__)[0] + '\\_HS.txt')
        HS.load_carriers_conc()
        HS.load_near_field()
        HS.calculate_ai()
        HS.print_ai()

        HS.calculate_ros()
        HS.print_ros()
        HS.load_carriers_conc()
        HS.load_near_field()
        HS.calculate_ai()
        HS.print_ai()

        HS.calculate_ros()
        HS.print_ros()

    def RsCalculatorWithGist(self):
        HS = SimHS(os.path.split(__file__)[0] + '\\_HS.txt')
        calculator = RsWithGist(HS)
        calculator.generate_histograms()


if __name__ == '__main__':
    app = App()
    app.mainloop()
