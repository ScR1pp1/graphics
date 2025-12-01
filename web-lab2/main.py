import os
import sys
import threading
from datetime import datetime
from pathlib import Path
from tkinter import *
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from PIL.ExifTags import TAGS
import struct
import csv


class ImageAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image File Analyzer v1.0")
        self.root.geometry("1200x700")

        self.files = []
        self.current_folder = ""
        self.processing = False

        self.create_widgets()

    def create_widgets(self):
        control_frame = Frame(self.root, bg='#333333', height=60)
        control_frame.pack(fill=X, padx=5, pady=5)
        control_frame.pack_propagate(False)

        Button(control_frame, text="Выбрать папку", command=self.select_folder,
               bg='#4CAF50', fg='black', font=('Arial', 10, 'bold'),
               width=15, height=1, relief=RAISED, bd=2).place(x=10, y=15)

        self.folder_label = Label(control_frame, text="Папка не выбрана",
                                  bg='#333333', fg='white', font=('Arial', 10))
        self.folder_label.place(x=150, y=20)

        self.status_label = Label(control_frame, text="Готов",
                                  bg='#333333', fg='white', font=('Arial', 10))
        self.status_label.place(x=900, y=20)

        self.progress = ttk.Progressbar(control_frame, mode='determinate', length=200)
        self.progress.place(x=950, y=20)

        main_frame = Frame(self.root, bg='#444444')
        main_frame.pack(fill=BOTH, expand=True, padx=10, pady=5)

        left_frame = Frame(main_frame, bg='#444444')
        left_frame.pack(side=LEFT, fill=BOTH, expand=True)

        columns = ('filename', 'format', 'size', 'resolution', 'color_depth', 'compression')
        self.tree = ttk.Treeview(left_frame, columns=columns, show='headings', height=20)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#f0f0f0", fieldbackground="#f0f0f0", foreground="black")
        style.configure("Treeview.Heading", background="#4CAF50", foreground="black", font=('Arial', 10, 'bold'))

        self.tree.heading('filename', text='Имя файла')
        self.tree.heading('format', text='Формат')
        self.tree.heading('size', text='Размер (пиксели)')
        self.tree.heading('resolution', text='Разрешение (DPI)')
        self.tree.heading('color_depth', text='Глубина цвета')
        self.tree.heading('compression', text='Сжатие')

        self.tree.column('filename', width=200)
        self.tree.column('format', width=80)
        self.tree.column('size', width=120)
        self.tree.column('resolution', width=120)
        self.tree.column('color_depth', width=100)
        self.tree.column('compression', width=120)

        tree_scroll = Scrollbar(left_frame, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)

        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        tree_scroll.pack(side=RIGHT, fill=Y)

        right_frame = Frame(main_frame, width=350, bg='#555555')
        right_frame.pack(side=RIGHT, fill=Y, padx=(10, 0))
        right_frame.pack_propagate(False)

        Label(right_frame, text="Детальная информация", font=('Arial', 12, 'bold'),
              bg='#555555', fg='white').pack(pady=(10, 5))

        self.detail_text = Text(right_frame, height=25, width=40, font=('Courier', 9),
                                wrap=WORD, bg='#222222', fg='white', insertbackground='white')
        self.detail_scroll = Scrollbar(right_frame, command=self.detail_text.yview)
        self.detail_text.configure(yscrollcommand=self.detail_scroll.set)

        self.detail_text.pack(side=LEFT, fill=BOTH, expand=True, padx=(5, 0))
        self.detail_scroll.pack(side=RIGHT, fill=Y)

        self.tree.bind('<<TreeviewSelect>>', self.show_details)

        bottom_frame = Frame(self.root, bg='#333333', height=60)
        bottom_frame.pack(fill=X, padx=5, pady=5)
        bottom_frame.pack_propagate(False)

        Button(bottom_frame, text="Экспорт в CSV", command=self.export_csv,
               bg='#2196F3', fg='black', width=15, height=1, relief=RAISED, bd=2).place(x=10, y=15)
        Button(bottom_frame, text="Очистить", command=self.clear_results,
               bg='#ff9800', fg='black', width=15, height=1, relief=RAISED, bd=2).place(x=150, y=15)
        Button(bottom_frame, text="Справка", command=self.show_help,
               bg='#9C27B0', fg='black', width=15, height=1, relief=RAISED, bd=2).place(x=290, y=15)

        self.stats_label = Label(bottom_frame, text="Файлов: 0",
                                 bg='#333333', fg='white', font=('Arial', 10))
        self.stats_label.place(x=900, y=20)

    def select_folder(self):
        if self.processing:
            messagebox.showwarning("Внимание", "Дождитесь завершения обработки текущих файлов")
            return

        folder = filedialog.askdirectory(title="Выберите папку с изображениями")
        if folder:
            self.current_folder = folder
            self.folder_label.config(text=f"Папка: {os.path.basename(folder)}")
            self.scan_folder(folder)

    def scan_folder(self, folder):
        self.files = []
        supported_extensions = {'.jpg', '.jpeg', '.gif', '.tif', '.tiff', '.bmp', '.png', '.pcx'}

        for root, dirs, files in os.walk(folder):
            for file in files:
                if Path(file).suffix.lower() in supported_extensions:
                    self.files.append(os.path.join(root, file))

            if len(self.files) >= 100000:
                messagebox.showwarning("Внимание", "Обработано максимальное количество файлов (100000)")
                break

        if not self.files:
            messagebox.showinfo("Информация", "В выбранной папке не найдены графические файлы")
            return

        self.processing = True
        self.status_label.config(text="Обработка...")
        self.progress['maximum'] = len(self.files)
        self.progress['value'] = 0

        thread = threading.Thread(target=self.process_files)
        thread.daemon = True
        thread.start()

    def process_files(self):
        self.tree.delete(*self.tree.get_children())

        for i, file_path in enumerate(self.files):
            if not self.processing:
                break

            try:
                info = self.get_image_info(file_path)
                self.root.after(0, self.add_to_tree, file_path, info)
                self.root.after(0, self.update_progress, i + 1)
            except Exception as e:
                print(f"Ошибка обработки файла {file_path}: {e}")

        self.root.after(0, self.finish_processing)

    def get_image_info(self, file_path):
        info = {
            'filename': os.path.basename(file_path),
            'format': Path(file_path).suffix.upper()[1:],
            'size': '',
            'resolution': '',
            'color_depth': '',
            'compression': '',
            'details': {}
        }

        try:
            with Image.open(file_path) as img:
                info['size'] = f"{img.width} × {img.height}"

                if 'dpi' in img.info:
                    dpi = img.info['dpi']
                    if isinstance(dpi, tuple) and len(dpi) >= 2:
                        info['resolution'] = f"{dpi[0]} × {dpi[1]}"

                info['color_depth'] = self.get_color_depth(img)
                info['compression'] = self.get_compression_info(img, file_path)
                info['details'] = self.get_additional_info(img, file_path)

        except Exception as e:
            info['details']['error'] = f"Ошибка чтения: {str(e)}"

        return info

    def get_color_depth(self, img):
        mode_to_depth = {
            '1': 1, 'L': 8, 'P': 8, 'RGB': 24, 'RGBA': 32,
            'CMYK': 32, 'YCbCr': 24, 'I': 32, 'F': 32
        }

        depth = mode_to_depth.get(img.mode, 'Неизвестно')
        if depth != 'Неизвестно':
            return f"{depth} бит"
        return depth

    def get_compression_info(self, img, file_path):
        ext = Path(file_path).suffix.lower()

        if ext in ['.jpg', '.jpeg']:
            try:
                with open(file_path, 'rb') as f:
                    data = f.read(2)
                    if data == b'\xff\xd8':
                        f.seek(0)
                        while True:
                            marker = f.read(2)
                            if not marker:
                                break
                            if marker[0] != 0xFF:
                                break
                            if marker[1] == 0xC0 or marker[1] == 0xC2:
                                length_bytes = f.read(2)
                                length = struct.unpack('>H', length_bytes)[0]
                                f.seek(length - 2, 1)

                                if marker[1] == 0xC0:
                                    return "Baseline DCT"
                                elif marker[1] == 0xC2:
                                    return "Progressive DCT"
                return "JPEG"
            except:
                return "JPEG"

        elif ext == '.png':
            return "Deflate"
        elif ext == '.gif':
            return "LZW"
        elif ext == '.tif' or ext == '.tiff':
            return "LZW/Deflate/JPEG" if 'compression' in img.info else "Без сжатия"
        elif ext == '.bmp':
            return "Без сжатия/RLE"
        elif ext == '.pcx':
            return "RLE"

        return "Неизвестно"

    def get_additional_info(self, img, file_path):
        details = {}
        ext = Path(file_path).suffix.lower()

        try:
            details['Режим'] = img.mode
            details['Формат'] = img.format
            details['Количество кадров'] = getattr(img, 'n_frames', 1)

            if img.palette:
                details['Палитра'] = "Да"
                details['Цвета в палитре'] = len(img.palette.palette) // 3
            else:
                details['Палитра'] = "Нет"

            if ext in ['.jpg', '.jpeg']:
                exif = img._getexif()
                if exif:
                    details['EXIF данные'] = "Да"
                    for tag_id, value in exif.items():
                        tag = TAGS.get(tag_id, tag_id)
                        if tag in ['Make', 'Model', 'DateTime', 'Software', 'ExifImageWidth', 'ExifImageHeight']:
                            details[str(tag)] = str(value)
                else:
                    details['EXIF данные'] = "Нет"

                try:
                    with open(file_path, 'rb') as f:
                        data = f.read()
                        pos = 0
                        quantization_tables = 0
                        while pos < len(data) - 1:
                            if data[pos] == 0xFF and data[pos + 1] == 0xDB:
                                quantization_tables += 1
                            pos += 1
                        if quantization_tables > 0:
                            details['Таблицы квантования'] = quantization_tables
                except:
                    pass

            elif ext == '.gif':
                details['Прозрачность'] = "Да" if img.info.get('transparency') is not None else "Нет"
                details['Версия GIF'] = img.info.get('version', 'Неизвестно')

            elif ext in ['.tif', '.tiff']:
                details['Страниц в файле'] = getattr(img, 'n_frames', 1)

            elif ext == '.png':
                details['Прозрачность'] = "Да" if img.mode in ['RGBA', 'LA', 'PA'] else "Нет"
                details['Числовая модель'] = img.info.get('gamma', 'Не указана')

        except Exception as e:
            details['Ошибка деталей'] = str(e)

        return details

    def add_to_tree(self, file_path, info):
        self.tree.insert('', 'end', values=(
            info['filename'],
            info['format'],
            info['size'],
            info['resolution'],
            info['color_depth'],
            info['compression']
        ), tags=(file_path,))

    def update_progress(self, value):
        self.progress['value'] = value
        self.stats_label.config(text=f"Файлов: {value}/{len(self.files)}")

    def finish_processing(self):
        self.processing = False
        self.status_label.config(text="Готов")
        messagebox.showinfo("Завершено", f"Обработано {len(self.files)} файлов")

    def show_details(self, event):
        selection = self.tree.selection()
        if not selection:
            return

        item = self.tree.item(selection[0])
        file_path = item['tags'][0] if item['tags'] else ""

        if not os.path.exists(file_path):
            self.detail_text.delete(1.0, END)
            self.detail_text.insert(END, "Файл не найден")
            return

        try:
            info = self.get_image_info(file_path)

            self.detail_text.delete(1.0, END)
            self.detail_text.insert(END, "=== ОСНОВНАЯ ИНФОРМАЦИЯ ===\n\n")
            self.detail_text.insert(END, f"Файл: {info['filename']}\n")
            self.detail_text.insert(END, f"Формат: {info['format']}\n")
            self.detail_text.insert(END, f"Размер: {info['size']}\n")
            self.detail_text.insert(END, f"Разрешение: {info['resolution']}\n")
            self.detail_text.insert(END, f"Глубина цвета: {info['color_depth']}\n")
            self.detail_text.insert(END, f"Сжатие: {info['compression']}\n")

            self.detail_text.insert(END, "\n=== ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ ===\n\n")
            for key, value in info['details'].items():
                self.detail_text.insert(END, f"{key}: {value}\n")

            self.detail_text.insert(END, "\n=== ИНФОРМАЦИЯ О ФАЙЛЕ ===\n\n")
            try:
                stat = os.stat(file_path)
                self.detail_text.insert(END, f"Размер: {stat.st_size:,} байт\n")
                self.detail_text.insert(END, f"Дата создания: {datetime.fromtimestamp(stat.st_ctime)}\n")
                self.detail_text.insert(END, f"Дата изменения: {datetime.fromtimestamp(stat.st_mtime)}\n")
            except:
                self.detail_text.insert(END, "Не удалось получить информацию о файле\n")

        except Exception as e:
            self.detail_text.delete(1.0, END)
            self.detail_text.insert(END, f"Ошибка: {str(e)}")

    def export_csv(self):
        if not self.files:
            messagebox.showwarning("Внимание", "Нет данных для экспорта")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8-sig', newline='') as f:
                    writer = csv.writer(f, delimiter=';')
                    writer.writerow(
                        ["Имя файла", "Формат", "Размер (пиксели)", "Разрешение (DPI)", "Глубина цвета", "Сжатие"])

                    for child in self.tree.get_children():
                        values = self.tree.item(child)['values']
                        writer.writerow(values)

                messagebox.showinfo("Успех", f"Данные экспортированы в {file_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось экспортировать: {str(e)}")

    def clear_results(self):
        if self.processing:
            messagebox.showwarning("Внимание", "Дождитесь завершения обработки")
            return

        if messagebox.askyesno("Подтверждение", "Очистить все результаты?"):
            self.tree.delete(*self.tree.get_children())
            self.detail_text.delete(1.0, END)
            self.files = []
            self.stats_label.config(text="Файлов: 0")
            self.folder_label.config(text="Папка не выбрана")
            self.progress['value'] = 0

    def show_help(self):
        help_text = """ПРИЛОЖЕНИЕ ДЛЯ АНАЛИЗА ГРАФИЧЕСКИХ ФАЙЛОВ

Возможности:
1. Анализ графических файлов (JPG, GIF, TIF, BMP, PNG, PCX)
2. Отображение основной информации:
   - Имя файла
   - Размер в пикселях
   - Разрешение (DPI)
   - Глубина цвета
   - Тип сжатия
3. Дополнительная информация:
   - EXIF данные для JPEG
   - Палитра для GIF
   - Информация о сжатии
4. Обработка до 100000 файлов
5. Экспорт результатов в CSV

Инструкция:
1. Нажмите "Выбрать папку"
2. Выберите папку с изображениями
3. Дождитесь завершения обработки
4. Выберите файл в таблице для просмотра деталей

Для выполнения лабораторной работы №2"""

        messagebox.showinfo("Справка", help_text)


def main():
    root = Tk()
    app = ImageAnalyzerApp(root)

    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')

    root.mainloop()


if __name__ == "__main__":
    main()