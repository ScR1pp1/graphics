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

        self.original_image = None
        self.processed_image = None
        self.image_path = None

        self.create_widgets()

        self.create_test_images_folder()

    def create_test_images_folder(self):
        """Создает папку с тестовыми изображениями"""
        if not os.path.exists("test_images"):
            os.makedirs("test_images")
            self.create_sample_test_images()

    def create_sample_test_images(self):
        """Создает примеры тестовых изображений"""
        low_contrast = np.random.randint(50, 150, (300, 300), dtype=np.uint8)
        cv2.imwrite("test_images/low_contrast.jpg", low_contrast)

        noisy = np.random.randint(0, 255, (300, 300), dtype=np.uint8)
        cv2.imwrite("test_images/noisy.jpg", noisy)

        smooth = np.ones((300, 300), dtype=np.uint8) * 128
        smooth[100:200, 100:200] = 200
        smooth = cv2.GaussianBlur(smooth, (15, 15), 5)
        cv2.imwrite("test_images/blurred.jpg", smooth)

        lines = np.zeros((300, 300), dtype=np.uint8)
        cv2.line(lines, (50, 50), (250, 250), 255, 2)
        cv2.line(lines, (50, 250), (250, 50), 255, 2)
        for i in range(10):
            x = np.random.randint(0, 300)
            y = np.random.randint(0, 300)
            cv2.circle(lines, (x, y), 3, 255, -1)
        cv2.imwrite("test_images/lines_and_points.jpg", lines)

        gradient = np.zeros((300, 300), dtype=np.uint8)
        for i in range(300):
            gradient[:, i] = i
        cv2.imwrite("test_images/gradient.jpg", gradient)

    def create_widgets(self):
        control_frame = ttk.LabelFrame(self.root, text="Управление", padding=10)
        control_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        ttk.Button(control_frame, text="Загрузить изображение",
                   command=self.load_image).pack(pady=5, fill=tk.X)

        ttk.Button(control_frame, text="Сохранить результат",
                   command=self.save_image).pack(pady=5, fill=tk.X)

        ttk.Separator(control_frame, orient='horizontal').pack(fill=tk.X, pady=10)

        self.method_var = tk.StringVar()
        methods = [
            "Линейное контрастирование",
            "Эквализация гистограммы (Grayscale)",
            "Эквализация гистограммы (RGB)",
            "Эквализация гистограммы (HSV - только яркость)",
            "Медианный фильтр",
            "Минимальный фильтр",
            "Максимальный фильтр",
            "Фильтр срединной точки",
            "Альфа-усредненный фильтр"
        ]

        ttk.Label(control_frame, text="Выберите метод:").pack(pady=5)
        self.method_combo = ttk.Combobox(control_frame, textvariable=self.method_var,
                                         values=methods, state="readonly")
        self.method_combo.pack(pady=5, fill=tk.X)
        self.method_combo.current(0)

        self.filter_params_frame = ttk.Frame(control_frame)
        self.filter_params_frame.pack(pady=10, fill=tk.X)

        ttk.Label(self.filter_params_frame, text="Размер ядра:").pack()
        self.kernel_size = tk.IntVar(value=3)
        ttk.Scale(self.filter_params_frame, from_=3, to=15, orient=tk.HORIZONTAL,
                  variable=self.kernel_size, command=self.update_kernel_label).pack(fill=tk.X)
        self.kernel_label = ttk.Label(self.filter_params_frame, text="3x3")
        self.kernel_label.pack()

        self.contrast_params_frame = ttk.Frame(control_frame)
        self.contrast_params_frame.pack(pady=10, fill=tk.X)

        ttk.Label(self.contrast_params_frame, text="Минимум:").pack()
        self.min_val = tk.IntVar(value=0)
        ttk.Scale(self.contrast_params_frame, from_=0, to=255, orient=tk.HORIZONTAL,
                  variable=self.min_val).pack(fill=tk.X)

        ttk.Label(self.contrast_params_frame, text="Максимум:").pack()
        self.max_val = tk.IntVar(value=255)
        ttk.Scale(self.contrast_params_frame, from_=0, to=255, orient=tk.HORIZONTAL,
                  variable=self.max_val).pack(fill=tk.X)

        ttk.Button(control_frame, text="Применить метод",
                   command=self.apply_method).pack(pady=10, fill=tk.X)

        ttk.Button(control_frame, text="Показать гистограммы",
                   command=self.show_histograms).pack(pady=5, fill=tk.X)

        ttk.Separator(control_frame, orient='horizontal').pack(fill=tk.X, pady=10)
        ttk.Label(control_frame, text="Тестовые изображения:").pack(pady=5)

        test_images = [
            ("Низкоконтрастное", "test_images/low_contrast.jpg"),
            ("Зашумленное", "test_images/noisy.jpg"),
            ("Размытое", "test_images/blurred.jpg"),
            ("Точки и линии", "test_images/lines_and_points.jpg"),
            ("Градиент", "test_images/gradient.jpg")
        ]

        for name, path in test_images:
            if os.path.exists(path):
                ttk.Button(control_frame, text=name,
                           command=lambda p=path: self.load_test_image(p)).pack(pady=2, fill=tk.X)

        display_frame = ttk.Frame(self.root)
        display_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        self.original_label = ttk.Label(display_frame, text="Исходное изображение")
        self.original_label.pack(pady=5)
        self.original_canvas = tk.Canvas(display_frame, width=400, height=400, bg="gray")
        self.original_canvas.pack(pady=5)

        self.processed_label = ttk.Label(display_frame, text="Обработанное изображение")
        self.processed_label.pack(pady=5)
        self.processed_canvas = tk.Canvas(display_frame, width=400, height=400, bg="gray")
        self.processed_canvas.pack(pady=5)

        info_frame = ttk.LabelFrame(self.root, text="Информация", padding=10)
        info_frame.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)

        info_text = """
Вариант 5 включает:

1. Построение и эквализация гистограммы 
   изображения + линейное контрастирование

2. Реализация нелинейных фильтров, 
   основанных на порядковых статистиках

Доступные методы:
• Линейное контрастирование
• Эквализация гистограммы (3 метода)
• Медианный фильтр
• Минимальный/максимальный фильтры
• Фильтр срединной точки
• Альфа-усредненный фильтр

Для тестирования созданы изображения:
- Низкоконтрастные
- Зашумленные
- Размытые
- С точками и линиями
- С перепадами яркости
        """

        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack()

        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

    def update_kernel_label(self, value):
        size = int(float(value))
        if size % 2 == 0:
            size += 1
        self.kernel_size.set(size)
        self.kernel_label.config(text=f"{size}x{size}")

    def load_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff")]
        )
        if file_path:
            self.image_path = file_path
            self.original_image = cv2.imread(file_path)
            if self.original_image is not None:
                self.display_image(self.original_image, self.original_canvas)
                messagebox.showinfo("Успех", f"Изображение загружено\nРазмер: {self.original_image.shape}")

    def load_test_image(self, path):
        self.image_path = path
        self.original_image = cv2.imread(path)
        if self.original_image is not None:
            self.display_image(self.original_image, self.original_canvas)

    def display_image(self, image, canvas):
        """Отображает изображение на canvas"""
        if len(image.shape) == 3:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

        h, w = image.shape[:2]
        scale = min(400 / w, 400 / h)
        new_w, new_h = int(w * scale), int(h * scale)

        img_resized = cv2.resize(image_rgb, (new_w, new_h))
        img_pil = Image.fromarray(img_resized)
        img_tk = ImageTk.PhotoImage(img_pil)

        canvas.delete("all")
        canvas.config(width=new_w, height=new_h)
        canvas.create_image(new_w // 2, new_h // 2, anchor=tk.CENTER, image=img_tk)
        canvas.image = img_tk

    def apply_method(self):
        if self.original_image is None:
            messagebox.showwarning("Предупреждение", "Сначала загрузите изображение")
            return

        method = self.method_var.get()

        try:
            if method == "Линейное контрастирование":
                self.processed_image = self.linear_contrast()

            elif method == "Эквализация гистограммы (Grayscale)":
                self.processed_image = self.histogram_equalization_grayscale()

            elif method == "Эквализация гистограммы (RGB)":
                self.processed_image = self.histogram_equalization_rgb()

            elif method == "Эквализация гистограммы (HSV - только яркость)":
                self.processed_image = self.histogram_equalization_hsv()

            elif method == "Медианный фильтр":
                self.processed_image = self.median_filter()

            elif method == "Минимальный фильтр":
                self.processed_image = self.min_filter()

            elif method == "Максимальный фильтр":
                self.processed_image = self.max_filter()

            elif method == "Фильтр срединной точки":
                self.processed_image = self.midpoint_filter()

            elif method == "Альфа-усредненный фильтр":
                self.processed_image = self.alpha_trimmed_filter()

            if self.processed_image is not None:
                self.display_image(self.processed_image, self.processed_canvas)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при обработке: {str(e)}")

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
            img_min = img.min()
            img_max = img.max()
            if img_max - img_min > 0:
                img = np.clip((img - img_min) * (max_val - min_val) / (img_max - img_min) + min_val, 0, 255)

        return img.astype(np.uint8)

    def histogram_equalization_grayscale(self):
        """Эквализация гистограммы для полутонового изображения"""
        if len(self.original_image.shape) == 3:
            gray = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = self.original_image.copy()

        equalized = cv2.equalizeHist(gray)
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
            # Для цветного изображения
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

    def show_histograms(self):
        """Показывает гистограммы исходного и обработанного изображений"""
        if self.original_image is None:
            return

        fig, axes = plt.subplots(2, 2, figsize=(10, 8))

        if len(self.original_image.shape) == 3:
            colors = ('b', 'g', 'r')
            for i, color in enumerate(colors):
                hist = cv2.calcHist([self.original_image], [i], None, [256], [0, 256])
                axes[0, 0].plot(hist, color=color)
            axes[0, 0].set_title('Исходное (RGB)')
        else:
            hist = cv2.calcHist([self.original_image], [0], None, [256], [0, 256])
            axes[0, 0].plot(hist, 'k')
            axes[0, 0].set_title('Исходное (Gray)')

        axes[0, 0].set_xlim([0, 256])

        if self.processed_image is not None:
            if len(self.processed_image.shape) == 3:
                colors = ('b', 'g', 'r')
                for i, color in enumerate(colors):
                    hist = cv2.calcHist([self.processed_image], [i], None, [256], [0, 256])
                    axes[0, 1].plot(hist, color=color)
                axes[0, 1].set_title('Обработанное (RGB)')
            else:
                hist = cv2.calcHist([self.processed_image], [0], None, [256], [0, 256])
                axes[0, 1].plot(hist, 'k')
                axes[0, 1].set_title('Обработанное (Gray)')

            axes[0, 1].set_xlim([0, 256])

        if len(self.original_image.shape) == 3:
            axes[1, 0].imshow(cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB))
        else:
            axes[1, 0].imshow(self.original_image, cmap='gray')
        axes[1, 0].set_title('Исходное изображение')
        axes[1, 0].axis('off')

        if self.processed_image is not None:
            if len(self.processed_image.shape) == 3:
                axes[1, 1].imshow(cv2.cvtColor(self.processed_image, cv2.COLOR_BGR2RGB))
            else:
                axes[1, 1].imshow(self.processed_image, cmap='gray')
            axes[1, 1].set_title('Обработанное изображение')
            axes[1, 1].axis('off')

        plt.tight_layout()
        plt.show()

    def save_image(self):
        """Сохраняет обработанное изображение"""
        if self.processed_image is None:
            messagebox.showwarning("Предупреждение", "Нет обработанного изображения для сохранения")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".jpg",
            filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png"), ("BMP", "*.bmp")]
        )

        if file_path:
            cv2.imwrite(file_path, self.processed_image)
            messagebox.showinfo("Успех", f"Изображение сохранено: {file_path}")

def main():
    root = tk.Tk()
    app = ImageProcessorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()