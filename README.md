# NIIPolusLaserCalculator

### Установка
1. Создать виртуальное окружение командой

    ```python -m venv .venv```

2. Активировать окружение командой:

    ```.venv\Scripts\activate.bat``` для cmd

    ```.venv\Scripts\Activate.ps1``` для PowerShell

3. При необходимости, перезапустить среду разработки
4. Установить все библиотеки командой

    ```pip install -r requirements.txt```

5. Запустить файл visual.py командой

    ```python visual.py```

### Компиляция
1. В терминале выполнить команду

   ```auto-py-to-exe```
2. В ```Script Location``` указать путь до файла visual.py
3. После открытия окна компилятора, нажать кнопку ```One File```
3. При необходимости можно скрыть консоль кнопкой ```Window Based (hide the console)```
4. Раскрыть ```Icon``` и указать путь до иконки проложения (в Корневой папке проекта images/favicon.ico)
5. Раскрыть ```Additional Files``` и нажать кнопку ```Add Files```
6. Добавить отдельно файлы ```RsCalculation.py```,```SimWindows.py``` и ```SimWindowsWithHistogr.py```
7. Добавить папку ```.venv``` для подгрузки используемых библиотек
8. Нажать кнопку ```CONVERT .PY TO EXE```
9. После компиляции, нажать кнопку ```OPEN OUTPUT FOLDER```