import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os


class ImageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Processor - Вариант 5")
        self.root.geometry("1400x800")

        self.setup_styles()

        self.original_image = None
        self.processed_image = None
        self.image_path = None

        self.create_widgets()
        self.create_test_images_folder()

    def setup_styles(self):
        """Настройка стилей для улучшенного внешнего вида"""
        style = ttk.Style()
        style.theme_use('clam')

        style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10), padding=6)
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabelframe', background='#f0f0f0')
        style.configure('TLabelframe.Label', background='#f0f0f0',
                        font=('Arial', 11, 'bold'), foreground='#2c3e50')

        style.map('TCombobox', fieldbackground=[('readonly', 'white')])

        style.configure('Horizontal.TScale', background='#f0f0f0')

        self.root.configure(bg='#f0f0f0')

    def create_test_images_folder(self):
        """Создает папку с тестовыми изображениями"""
        if not os.path.exists("test_images"):
            os.makedirs("test_images")
            self.create_sample_test_images()

    def create_sample_test_images(self):
        """Создает примеры тестовых изображений"""
        print("Создание тестовых изображений...")

        low_contrast = np.ones((300, 300), dtype=np.uint8) * 100
        low_contrast[100:200, 100:200] = 150
        cv2.imwrite("test_images/low_contrast.jpg", low_contrast)
        print("✓ Создано: test_images/low_contrast.jpg")

        dark_image = np.random.normal(50, 20, (300, 300)).astype(np.uint8)
        dark_image = np.clip(dark_image, 0, 255)
        cv2.imwrite("test_images/dark_image.jpg", dark_image)
        print("✓ Создано: test_images/dark_image.jpg")

        color_low_contrast = np.zeros((300, 300, 3), dtype=np.uint8)
        for i in range(3):
            channel = np.random.randint(50, 100, (300, 300), dtype=np.uint8)
            color_low_contrast[:, :, i] = channel
        cv2.imwrite("test_images/color_low_contrast.jpg", color_low_contrast)
        print("✓ Создано: test_images/color_low_contrast.jpg")

        hsv_dark = np.zeros((300, 300, 3), dtype=np.uint8)
        for i in range(300):
            hsv_dark[:, i, 2] = i // 2
            hsv_dark[:, i, 0] = 120
            hsv_dark[:, i, 1] = 200
        cv2.imwrite("test_images/hsv_dark.jpg", hsv_dark)
        print("✓ Создано: test_images/hsv_dark.jpg")

        noisy = np.random.randint(0, 255, (300, 300), dtype=np.uint8)
        salt_pepper = noisy.copy()
        salt_pepper[noisy < 30] = 0  # Перец
        salt_pepper[noisy > 225] = 255  # Соль
        cv2.imwrite("test_images/salt_pepper.jpg", salt_pepper)
        print("✓ Создано: test_images/salt_pepper.jpg")

        white_points = np.zeros((300, 300), dtype=np.uint8)
        white_points[50, 50] = 255
        white_points[150, 150] = 255
        white_points[250, 250] = 255
        white_points = cv2.GaussianBlur(white_points, (5, 5), 1)
        cv2.imwrite("test_images/white_points.jpg", white_points)
        print("✓ Создано: test_images/white_points.jpg")

        black_points = np.ones((300, 300), dtype=np.uint8) * 200
        black_points[50, 50] = 0
        black_points[150, 150] = 0
        black_points[250, 250] = 0
        black_points = cv2.GaussianBlur(black_points, (5, 5), 1)
        cv2.imwrite("test_images/black_points.jpg", black_points)
        print("✓ Создано: test_images/black_points.jpg")

        impulse_noise = np.ones((300, 300), dtype=np.uint8) * 128
        for _ in range(50):
            x = np.random.randint(0, 300)
            y = np.random.randint(0, 300)
            impulse_noise[x, y] = np.random.choice([0, 255])
        cv2.imwrite("test_images/impulse_noise.jpg", impulse_noise)
        print("✓ Создано: test_images/impulse_noise.jpg")

        mixed_noise = np.ones((300, 300), dtype=np.uint8) * 128
        gaussian = np.random.normal(0, 30, (300, 300)).astype(np.uint8)
        mixed_noise = np.clip(mixed_noise + gaussian, 0, 255)
        for _ in range(100):
            x = np.random.randint(0, 300)
            y = np.random.randint(0, 300)
            mixed_noise[x, y] = np.random.choice([0, 255])
        cv2.imwrite("test_images/mixed_noise.jpg", mixed_noise)
        print("✓ Создано: test_images/mixed_noise.jpg")

        gradient = np.zeros((300, 300), dtype=np.uint8)
        for i in range(300):
            gradient[:, i] = i
        cv2.imwrite("test_images/gradient.jpg", gradient)
        print("✓ Создано: test_images/gradient.jpg")

        print("✓ Все тестовые изображения созданы!")

    def create_widgets(self):
        """Создание интерфейса"""

        control_frame = ttk.LabelFrame(self.root, text="⚙️ УПРАВЛЕНИЕ", padding=15)
        control_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(button_frame, text="📁 Загрузить изображение",
                   command=self.load_image,
                   style='TButton').pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)

        ttk.Button(button_frame, text="💾 Сохранить результат",
                   command=self.save_image,
                   style='TButton').pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)

        ttk.Separator(control_frame, orient='horizontal').pack(fill=tk.X, pady=10)

        method_frame = ttk.LabelFrame(control_frame, text="📊 ВЫБОР МЕТОДА", padding=10)
        method_frame.pack(fill=tk.X, pady=(0, 10))

        self.method_var = tk.StringVar()
        methods = [
            "Линейное контрастирование",
            "Эквализация гистограммы (Grayscale)",
            "Эквализация гистограммы (RGB)",
            "Эквализация гистограммы (HSV)",
            "Медианный фильтр",
            "Минимальный фильтр",
            "Максимальный фильтр",
            "Фильтр срединной точки",
            "Альфа-усредненный фильтр"
        ]

        self.method_combo = ttk.Combobox(method_frame, textvariable=self.method_var,
                                         values=methods, state="readonly",
                                         height=10, font=('Arial', 10))
        self.method_combo.pack(fill=tk.X, pady=(5, 0))
        self.method_combo.current(0)
        self.method_combo.bind('<<ComboboxSelected>>', self.on_method_change)

        self.params_frame = ttk.LabelFrame(control_frame, text="⚙️ ПАРАМЕТРЫ", padding=10)
        self.params_frame.pack(fill=tk.X, pady=(0, 10))

        self.create_filter_params()
        self.create_contrast_params()

        ttk.Button(control_frame, text="🚀 ПРИМЕНИТЬ МЕТОД",
                   command=self.apply_method,
                   style='Accent.TButton').pack(fill=tk.X, pady=(0, 10))

        ttk.Button(control_frame, text="📈 ПОКАЗАТЬ ГИСТОГРАММЫ",
                   command=self.show_enhanced_histograms,
                   style='TButton').pack(fill=tk.X, pady=(0, 10))

        ttk.Separator(control_frame, orient='horizontal').pack(fill=tk.X, pady=10)

        test_frame = ttk.LabelFrame(control_frame, text="🧪 ТЕСТОВЫЕ ИЗОБРАЖЕНИЯ", padding=10)
        test_frame.pack(fill=tk.X)

        test_images = [
            ("🎨 Низкоконтрастное", "test_images/low_contrast.jpg"),
            ("🌙 Темное", "test_images/dark_image.jpg"),
            ("🌈 Цветное (малый контраст)", "test_images/color_low_contrast.jpg"),
            ("🍃 HSV темное", "test_images/hsv_dark.jpg"),
            ("🧂 Соль-перец", "test_images/salt_pepper.jpg"),
            ("⚪ Белые точки", "test_images/white_points.jpg"),
            ("⚫ Черные точки", "test_images/black_points.jpg"),
            ("⚡ Импульсный шум", "test_images/impulse_noise.jpg"),
            ("🌀 Смешанный шум", "test_images/mixed_noise.jpg"),
            ("📶 Градиент", "test_images/gradient.jpg")
        ]

        for name, path in test_images:
            if os.path.exists(path):
                btn = ttk.Button(test_frame, text=name,
                                 command=lambda p=path: self.load_test_image(p),
                                 style='Small.TButton')
                btn.pack(fill=tk.X, pady=2)

        display_frame = ttk.Frame(self.root)
        display_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        orig_frame = ttk.LabelFrame(display_frame, text="📷 ИСХОДНОЕ ИЗОБРАЖЕНИЕ", padding=10)
        orig_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        self.original_canvas = tk.Canvas(orig_frame, bg="#2c3e50", highlightthickness=0)
        self.original_canvas.pack(fill=tk.BOTH, expand=True)

        proc_frame = ttk.LabelFrame(display_frame, text="✨ ОБРАБОТАННОЕ ИЗОБРАЖЕНИЕ", padding=10)
        proc_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        self.processed_canvas = tk.Canvas(proc_frame, bg="#2c3e50", highlightthickness=0)
        self.processed_canvas.pack(fill=tk.BOTH, expand=True)

        # Правая панель - информация
        info_frame = ttk.LabelFrame(self.root, text="ℹ️ ИНФОРМАЦИЯ", padding=15)
        info_frame.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)

        info_text = """
🎯 ВАРИАНТ 5

📊 ГИСТОГРАММА ИЗОБРАЖЕНИЯ:
• График распределения яркости пикселей
• По оси X: значения яркости (0-255)
• По оси Y: количество пикселей

🚀 МЕТОДЫ ОБРАБОТКИ:

1️⃣ ЛИНЕЙНОЕ КОНТРАСТИРОВАНИЕ
   • Растягивает диапазон яркостей
   • Используйте для низкоконтрастных изображений

2️⃣ ЭКВАЛИЗАЦИЯ ГИСТОГРАММЫ:
   • Grayscale - для черно-белых
   • RGB - для цветных (меняет цвета)
   • HSV - сохраняет цветовой тон

3️⃣ НЕЛИНЕЙНЫЕ ФИЛЬТРЫ:
   • Медианный - против шума "соль-перец"
   • Минимальный - удаляет светлые точки
   • Максимальный - удаляет темные точки
   • Срединной точки - для импульсного шума
   • Альфа-усредненный - для смешанного шума

📝 ИНСТРУКЦИЯ:
1. Загрузите изображение или выберите тестовое
2. Выберите метод обработки
3. Настройте параметры
4. Нажмите "Применить метод"
5. Посмотрите гистограммы для анализа
        """

        info_label = tk.Text(info_frame, wrap=tk.WORD, height=30, width=30,
                             font=('Arial', 10), bg='white', fg='black', relief=tk.FLAT,
                             padx=10, pady=10)
        info_label.insert(tk.END, info_text)
        info_label.configure(state='disabled')
        info_label.pack(fill=tk.BOTH, expand=True)

        self.status_bar = ttk.Label(self.root, text="Готов к работе...",
                                    relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=1, column=0, columnspan=3, sticky="ew", padx=10, pady=(0, 10))

        self.root.columnconfigure(1, weight=3)
        self.root.rowconfigure(0, weight=1)

    def create_filter_params(self):
        """Создает параметры для фильтров"""
        self.filter_frame = ttk.Frame(self.params_frame)

        ttk.Label(self.filter_frame, text="Размер ядра фильтра:").pack(anchor=tk.W)

        kernel_frame = ttk.Frame(self.filter_frame)
        kernel_frame.pack(fill=tk.X, pady=(5, 0))

        self.kernel_size = tk.IntVar(value=3)

        self.kernel_slider = ttk.Scale(kernel_frame, from_=3, to=15,
                                       orient=tk.HORIZONTAL, variable=self.kernel_size,
                                       command=self.update_kernel_label)
        self.kernel_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        self.kernel_label = ttk.Label(kernel_frame, text="3x3", width=8)
        self.kernel_label.pack(side=tk.RIGHT)

        self.filter_frame.pack(fill=tk.X, pady=(0, 10))

    def create_contrast_params(self):
        """Создает параметры для контрастирования"""
        self.contrast_frame = ttk.Frame(self.params_frame)

        min_frame = ttk.Frame(self.contrast_frame)
        min_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(min_frame, text="Минимум:").pack(side=tk.LEFT)
        self.min_val_label = ttk.Label(min_frame, text="0", width=5)
        self.min_val_label.pack(side=tk.RIGHT)

        self.min_val = tk.IntVar(value=0)
        self.min_slider = ttk.Scale(self.contrast_frame, from_=0, to=255,
                                    orient=tk.HORIZONTAL, variable=self.min_val,
                                    command=lambda v: self.min_val_label.config(text=str(int(float(v)))))
        self.min_slider.pack(fill=tk.X, pady=(0, 10))

        max_frame = ttk.Frame(self.contrast_frame)
        max_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(max_frame, text="Максимум:").pack(side=tk.LEFT)
        self.max_val_label = ttk.Label(max_frame, text="255", width=5)
        self.max_val_label.pack(side=tk.RIGHT)

        self.max_val = tk.IntVar(value=255)
        self.max_slider = ttk.Scale(self.contrast_frame, from_=0, to=255,
                                    orient=tk.HORIZONTAL, variable=self.max_val,
                                    command=lambda v: self.max_val_label.config(text=str(int(float(v)))))
        self.max_slider.pack(fill=tk.X)

        self.contrast_frame.pack(fill=tk.X)

    def on_method_change(self, event=None):
        """Обработчик изменения выбранного метода"""
        method = self.method_var.get()

        self.filter_frame.pack_forget()
        self.contrast_frame.pack_forget()

        if method in ["Линейное контрастирование"]:
            self.contrast_frame.pack(fill=tk.X, pady=(0, 10))
        elif method in ["Медианный фильтр", "Минимальный фильтр",
                        "Максимальный фильтр", "Фильтр срединной точки",
                        "Альфа-усредненный фильтр"]:
            self.filter_frame.pack(fill=tk.X, pady=(0, 10))

    def update_kernel_label(self, value):
        """Обновляет метку размера ядра"""
        size = int(float(value))
        if size % 2 == 0:
            size += 1
        self.kernel_size.set(size)
        self.kernel_label.config(text=f"{size}x{size}")

    def load_image(self):
        """Загрузка изображения"""
        file_path = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[
                ("Изображения", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif"),
                ("Все файлы", "*.*")
            ]
        )
        if file_path:
            self.image_path = file_path
            self.original_image = cv2.imread(file_path)
            if self.original_image is not None:
                self.display_image(self.original_image, self.original_canvas)
                filename = os.path.basename(file_path)
                self.status_bar.config(
                    text=f"Загружено: {filename} ({self.original_image.shape[1]}x{self.original_image.shape[0]})")
                messagebox.showinfo("Успех",
                                    f"Изображение загружено!\n\n"
                                    f"Размер: {self.original_image.shape[1]}x{self.original_image.shape[0]}\n"
                                    f"Каналы: {self.original_image.shape[2] if len(self.original_image.shape) == 3 else 1}\n"
                                    f"Тип: {self.original_image.dtype}")

    def load_test_image(self, path):
        """Загрузка тестового изображения"""
        if os.path.exists(path):
            self.image_path = path
            self.original_image = cv2.imread(path)
            if self.original_image is not None:
                self.display_image(self.original_image, self.original_canvas)
                filename = os.path.basename(path)
                self.status_bar.config(text=f"Тестовое изображение: {filename}")

    def display_image(self, image, canvas):
        """Отображение изображения на canvas"""
        if len(image.shape) == 3:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

        h, w = image.shape[:2]

        canvas_width = canvas.winfo_width() or 400
        canvas_height = canvas.winfo_height() or 400

        scale = min(canvas_width / w, canvas_height / h) * 0.9
        new_w, new_h = int(w * scale), int(h * scale)

        img_resized = cv2.resize(image_rgb, (new_w, new_h), interpolation=cv2.INTER_AREA)
        img_pil = Image.fromarray(img_resized)
        img_tk = ImageTk.PhotoImage(img_pil)

        canvas.delete("all")
        canvas.create_image(canvas_width // 2, canvas_height // 2,
                            anchor=tk.CENTER, image=img_tk)
        canvas.image = img_tk

        canvas.create_text(10, 10, anchor=tk.NW, text=f"{w}x{h}",
                           fill="white", font=("Arial", 10, "bold"))

    def apply_method(self):
        """Применение выбранного метода обработки"""
        if self.original_image is None:
            messagebox.showwarning("Внимание", "Сначала загрузите изображение!")
            self.status_bar.config(text="Ошибка: изображение не загружено")
            return

        method = self.method_var.get()
        self.status_bar.config(text=f"Применение метода: {method}...")

        try:
            if method == "Линейное контрастирование":
                self.processed_image = self.linear_contrast()
                self.status_bar.config(text="✓ Линейное контрастирование применено")

            elif method == "Эквализация гистограммы (Grayscale)":
                self.processed_image = self.histogram_equalization_grayscale()
                self.status_bar.config(text="✓ Эквализация гистограммы (Grayscale) применена")

            elif method == "Эквализация гистограммы (RGB)":
                self.processed_image = self.histogram_equalization_rgb()
                self.status_bar.config(text="✓ Эквализация гистограммы (RGB) применена")

            elif method == "Эквализация гистограммы (HSV)":
                self.processed_image = self.histogram_equalization_hsv()
                self.status_bar.config(text="✓ Эквализация гистограммы (HSV) применена")

            elif method == "Медианный фильтр":
                self.processed_image = self.median_filter()
                self.status_bar.config(text="✓ Медианный фильтр применен")

            elif method == "Минимальный фильтр":
                self.processed_image = self.min_filter()
                self.status_bar.config(text="✓ Минимальный фильтр применен")

            elif method == "Максимальный фильтр":
                self.processed_image = self.max_filter()
                self.status_bar.config(text="✓ Максимальный фильтр применен")

            elif method == "Фильтр срединной точки":
                self.processed_image = self.midpoint_filter()
                self.status_bar.config(text="✓ Фильтр срединной точки применен")

            elif method == "Альфа-усредненный фильтр":
                self.processed_image = self.alpha_trimmed_filter()
                self.status_bar.config(text="✓ Альфа-усредненный фильтр применен")

            if self.processed_image is not None:
                self.display_image(self.processed_image, self.processed_canvas)

                self.update_statistics()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при обработке: {str(e)}")
            self.status_bar.config(text=f"Ошибка: {str(e)}")

    def linear_contrast(self):
        """Линейное контрастирование"""
        img = self.original_image.copy()
        min_val = self.min_val.get()
        max_val = self.max_val.get()

        if len(img.shape) == 3:
            for i in range(3):
                channel = img[:, :, i]
                channel_min = channel.min()
                channel_max = channel.max()
                if channel_max - channel_min > 0:
                    img[:, :, i] = np.clip((channel - channel_min) *
                                           (max_val - min_val) / (channel_max - channel_min) + min_val, 0, 255)
                else:
                    img[:, :, i] = np.clip(channel * (max_val - min_val) / 255 + min_val, 0, 255)
        else:
            img_min = img.min()
            img_max = img.max()
            if img_max - img_min > 0:
                img = np.clip((img - img_min) * (max_val - min_val) / (img_max - img_min) + min_val, 0, 255)
            else:
                img = np.clip(img * (max_val - min_val) / 255 + min_val, 0, 255)

        return img.astype(np.uint8)

    def histogram_equalization_grayscale(self):
        """Эквализация гистограммы для полутонового изображения"""
        if len(self.original_image.shape) == 3:
            gray = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = self.original_image.copy()

        equalized = cv2.equalizeHist(gray)

        if len(self.original_image.shape) == 3:
            equalized = cv2.cvtColor(equalized, cv2.COLOR_GRAY2BGR)

        return equalized

    def histogram_equalization_rgb(self):
        """Эквализация гистограммы для каждого канала RGB отдельно"""
        img = self.original_image.copy()

        channels = cv2.split(img)
        equalized_channels = []

        for channel in channels:
            equalized = cv2.equalizeHist(channel)
            equalized_channels.append(equalized)

        equalized_img = cv2.merge(equalized_channels)
        return equalized_img

    def histogram_equalization_hsv(self):
        """Эквализация гистограммы только для канала яркости в HSV"""
        img = self.original_image.copy()
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        h, s, v = cv2.split(hsv)

        v_equalized = cv2.equalizeHist(v)

        hsv_equalized = cv2.merge([h, s, v_equalized])

        equalized_img = cv2.cvtColor(hsv_equalized, cv2.COLOR_HSV2BGR)
        return equalized_img

    def median_filter(self):
        """Медианный фильтр"""
        kernel_size = self.kernel_size.get()
        if kernel_size % 2 == 0:
            kernel_size += 1

        if len(self.original_image.shape) == 3:
            channels = cv2.split(self.original_image)
            filtered_channels = []
            for channel in channels:
                filtered = cv2.medianBlur(channel, kernel_size)
                filtered_channels.append(filtered)
            filtered_img = cv2.merge(filtered_channels)
        else:
            filtered_img = cv2.medianBlur(self.original_image, kernel_size)

        return filtered_img

    def min_filter(self):
        """Минимальный фильтр (эрозия)"""
        kernel_size = self.kernel_size.get()
        if kernel_size % 2 == 0:
            kernel_size += 1

        kernel = np.ones((kernel_size, kernel_size), np.uint8)

        if len(self.original_image.shape) == 3:
            img_gray = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
            filtered = cv2.erode(img_gray, kernel)
            filtered = cv2.cvtColor(filtered, cv2.COLOR_GRAY2BGR)
        else:
            filtered = cv2.erode(self.original_image, kernel)

        return filtered

    def max_filter(self):
        """Максимальный фильтр (дилатация)"""
        kernel_size = self.kernel_size.get()
        if kernel_size % 2 == 0:
            kernel_size += 1

        kernel = np.ones((kernel_size, kernel_size), np.uint8)

        if len(self.original_image.shape) == 3:
            img_gray = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
            filtered = cv2.dilate(img_gray, kernel)
            filtered = cv2.cvtColor(filtered, cv2.COLOR_GRAY2BGR)
        else:
            filtered = cv2.dilate(self.original_image, kernel)

        return filtered

    def midpoint_filter(self):
        """Фильтр срединной точки"""
        kernel_size = self.kernel_size.get()
        if kernel_size % 2 == 0:
            kernel_size += 1

        img = self.original_image.copy()
        if len(img.shape) == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        pad = kernel_size // 2
        padded = cv2.copyMakeBorder(img, pad, pad, pad, pad, cv2.BORDER_REFLECT)
        filtered = np.zeros_like(img, dtype=np.float32)

        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                region = padded[i:i + kernel_size, j:j + kernel_size]
                min_val = np.min(region)
                max_val = np.max(region)
                filtered[i, j] = (min_val + max_val) / 2

        return np.clip(filtered, 0, 255).astype(np.uint8)

    def alpha_trimmed_filter(self):
        """Альфа-усредненный фильтр"""
        kernel_size = self.kernel_size.get()
        if kernel_size % 2 == 0:
            kernel_size += 1

        img = self.original_image.copy()
        if len(img.shape) == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        pad = kernel_size // 2
        padded = cv2.copyMakeBorder(img, pad, pad, pad, pad, cv2.BORDER_REFLECT)
        filtered = np.zeros_like(img, dtype=np.float32)

        d = 4

        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                region = padded[i:i + kernel_size, j:j + kernel_size].flatten()
                region_sorted = np.sort(region)
                trimmed = region_sorted[d // 2: -d // 2] if d > 0 else region_sorted
                filtered[i, j] = np.mean(trimmed)

        return np.clip(filtered, 0, 255).astype(np.uint8)

    def update_statistics(self):
        """Обновление статистики изображений"""
        if self.original_image is not None and self.processed_image is not None:
            if len(self.original_image.shape) == 3:
                gray_orig = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
                gray_proc = cv2.cvtColor(self.processed_image, cv2.COLOR_BGR2GRAY)
            else:
                gray_orig = self.original_image
                gray_proc = self.processed_image

            mean_orig = gray_orig.mean()
            std_orig = gray_orig.std()
            mean_proc = gray_proc.mean()
            std_proc = gray_proc.std()

            self.status_bar.config(text=f"Статистика: Исходное - μ={mean_orig:.1f}, σ={std_orig:.1f} | "
                                        f"Обработанное - μ={mean_proc:.1f}, σ={std_proc:.1f}")

    def show_enhanced_histograms(self):
        """Улучшенное отображение гистограмм с анализом"""
        if self.original_image is None:
            messagebox.showwarning("Внимание", "Сначала загрузите изображение!")
            return

        fig = plt.figure(figsize=(16, 10))
        plt.rcParams['font.size'] = 10

        ax1 = plt.subplot(2, 3, 1)
        if len(self.original_image.shape) == 3:
            ax1.imshow(cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB))
        else:
            ax1.imshow(self.original_image, cmap='gray')
        ax1.set_title('Исходное изображение', fontweight='bold')
        ax1.axis('off')

        ax2 = plt.subplot(2, 3, 4)
        if len(self.original_image.shape) == 3:
            colors = ('r', 'g', 'b')
            labels = ('Red', 'Green', 'Blue')
            for i, (color, label) in enumerate(zip(colors, labels)):
                hist = cv2.calcHist([self.original_image], [i], None, [256], [0, 256])
                ax2.plot(hist, color=color, label=label, alpha=0.7, linewidth=1.5)
            ax2.legend(fontsize=9)
            hist_title = 'Гистограмма RGB'
        else:
            hist = cv2.calcHist([self.original_image], [0], None, [256], [0, 256])
            ax2.plot(hist, 'k', label='Яркость', alpha=0.7, linewidth=1.5)
            ax2.legend(fontsize=9)
            hist_title = 'Гистограмма яркости'

        if len(self.original_image.shape) == 3:
            gray_orig = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
        else:
            gray_orig = self.original_image

        mean_orig = gray_orig.mean()
        std_orig = gray_orig.std()
        ax2.set_title(f'{hist_title}\nμ={mean_orig:.1f}, σ={std_orig:.1f}', fontweight='bold')
        ax2.set_xlabel('Интенсивность', fontweight='bold')
        ax2.set_ylabel('Частота', fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim([0, 255])

        if self.processed_image is not None:
            ax3 = plt.subplot(2, 3, 2)
            if len(self.processed_image.shape) == 3:
                ax3.imshow(cv2.cvtColor(self.processed_image, cv2.COLOR_BGR2RGB))
            else:
                ax3.imshow(self.processed_image, cmap='gray')
            ax3.set_title('Обработанное изображение', fontweight='bold')
            ax3.axis('off')

            ax4 = plt.subplot(2, 3, 5)
            if len(self.processed_image.shape) == 3:
                colors = ('r', 'g', 'b')
                for i, (color, label) in enumerate(zip(colors, labels)):
                    hist = cv2.calcHist([self.processed_image], [i], None, [256], [0, 256])
                    ax4.plot(hist, color=color, label=label, alpha=0.7, linewidth=1.5)
                ax4.legend(fontsize=9)
                hist_title_proc = 'Гистограмма RGB'
            else:
                hist = cv2.calcHist([self.processed_image], [0], None, [256], [0, 256])
                ax4.plot(hist, 'k', label='Яркость', alpha=0.7, linewidth=1.5)
                ax4.legend(fontsize=9)
                hist_title_proc = 'Гистограмма яркости'

            if len(self.processed_image.shape) == 3:
                gray_proc = cv2.cvtColor(self.processed_image, cv2.COLOR_BGR2GRAY)
            else:
                gray_proc = self.processed_image

            mean_proc = gray_proc.mean()
            std_proc = gray_proc.std()
            ax4.set_title(f'{hist_title_proc}\nμ={mean_proc:.1f}, σ={std_proc:.1f}', fontweight='bold')
            ax4.set_xlabel('Интенсивность', fontweight='bold')
            ax4.set_ylabel('Частота', fontweight='bold')
            ax4.grid(True, alpha=0.3)
            ax4.set_xlim([0, 255])

        ax5 = plt.subplot(2, 3, (3, 6))

        hist_orig = cv2.calcHist([gray_orig], [0], None, [256], [0, 256])
        cdf_orig = hist_orig.cumsum()
        cdf_orig = cdf_orig / cdf_orig[-1]  # Нормализация
        ax5.plot(cdf_orig, 'b-', label='Исходное', linewidth=2.5)

        if self.processed_image is not None:
            hist_proc = cv2.calcHist([gray_proc], [0], None, [256], [0, 256])
            cdf_proc = hist_proc.cumsum()
            cdf_proc = cdf_proc / cdf_proc[-1]
            ax5.plot(cdf_proc, 'r-', label='Обработанное', linewidth=2.5)

        ideal_cdf = np.linspace(0, 1, 256)
        ax5.plot(ideal_cdf, 'g--', label='Идеальная', linewidth=1.5, alpha=0.7)

        ax5.set_title('Кумулятивные функции распределения', fontweight='bold', fontsize=12)
        ax5.legend(fontsize=10)
        ax5.grid(True, alpha=0.3)
        ax5.set_xlabel('Интенсивность', fontweight='bold')
        ax5.set_ylabel('Накопленная вероятность', fontweight='bold')

        info_text = f"Метод: {self.method_var.get()}\n"
        info_text += f"Размер ядра: {self.kernel_size.get() if self.processed_image is not None and self.method_var.get() in ['Медианный фильтр', 'Минимальный фильтр', 'Максимальный фильтр', 'Фильтр срединной точки', 'Альфа-усредненный фильтр'] else 'N/A'}\n"
        if self.method_var.get() == "Линейное контрастирование":
            info_text += f"Диапазон: [{self.min_val.get()}, {self.max_val.get()}]"

        plt.figtext(0.5, 0.01, info_text, ha='center', fontsize=10,
                    bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.8))

        plt.suptitle(f'АНАЛИЗ ГИСТОГРАММ - {self.method_var.get()}',
                     fontsize=14, fontweight='bold', y=0.98)
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.show()

    def save_image(self):
        """Сохраняет обработанное изображение"""
        if self.processed_image is None:
            messagebox.showwarning("Внимание", "Нет обработанного изображения для сохранения!")
            return

        file_path = filedialog.asksaveasfilename(
            title="Сохранить обработанное изображение",
            defaultextension=".png",
            filetypes=[
                ("PNG", "*.png"),
                ("JPEG", "*.jpg"),
                ("BMP", "*.bmp"),
                ("TIFF", "*.tiff")
            ]
        )

        if file_path:
            try:
                cv2.imwrite(file_path, self.processed_image)
                filename = os.path.basename(file_path)
                self.status_bar.config(text=f"✓ Изображение сохранено: {filename}")
                messagebox.showinfo("Успех", f"Изображение успешно сохранено:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить изображение:\n{str(e)}")
                self.status_bar.config(text=f"Ошибка сохранения: {str(e)}")


def main():
    root = tk.Tk()

    window_width = 1400
    window_height = 800
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    center_x = int(screen_width / 2 - window_width / 2)
    center_y = int(screen_height / 2 - window_height / 2)

    root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

    try:
        root.iconbitmap('icon.ico')
    except:
        pass

    app = ImageProcessorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

#info_label