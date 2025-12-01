import tkinter as tk
from tkinter import ttk, colorchooser
import colorsys
import numpy as np
import warnings

class ColorConverter:
    @staticmethod
    def cmyk_to_rgb(c, m, y, k):
        """Преобразование CMYK [0,1] -> RGB [0,255]"""
        r = 255 * (1 - c) * (1 - k)
        g = 255 * (1 - m) * (1 - k)
        b = 255 * (1 - y) * (1 - k)
        return r, g, b

    @staticmethod
    def rgb_to_cmyk(r, g, b):
        """Преобразование RGB [0,255] -> CMYK [0,1]"""
        if (r, g, b) == (0, 0, 0):
            return 0.0, 0.0, 0.0, 1.0
        c = 1 - r / 255
        m = 1 - g / 255
        y = 1 - b / 255
        k = min(c, m, y)
        if (1 - k) > 0:
            c = (c - k) / (1 - k)
            m = (m - k) / (1 - k)
            y = (y - k) / (1 - k)
        else:
            c = m = y = 0
        return c, m, y, k

    @staticmethod
    def rgb_to_hsv(r, g, b):
        """RGB [0,255] -> HSV [0°,0-1,0-1]"""
        r_norm, g_norm, b_norm = r / 255, g / 255, b / 255
        h, s, v = colorsys.rgb_to_hsv(r_norm, g_norm, b_norm)
        return h * 360, s, v

    @staticmethod
    def hsv_to_rgb(h, s, v):
        """HSV [0°,0-1,0-1] -> RGB [0,255]"""
        r_norm, g_norm, b_norm = colorsys.hsv_to_rgb(h / 360, s, v)
        return r_norm * 255, g_norm * 255, b_norm * 255

    @staticmethod
    def rgb_to_xyz(r, g, b):
        """RGB [0,255] -> XYZ (стандартный D65)"""
        r_norm = r / 255.0
        g_norm = g / 255.0
        b_norm = b / 255.0

        r_norm = r_norm / 12.92 if r_norm <= 0.04045 else ((r_norm + 0.055) / 1.055) ** 2.4
        g_norm = g_norm / 12.92 if g_norm <= 0.04045 else ((g_norm + 0.055) / 1.055) ** 2.4
        b_norm = b_norm / 12.92 if b_norm <= 0.04045 else ((b_norm + 0.055) / 1.055) ** 2.4

        x = r_norm * 0.4124564 + g_norm * 0.3575761 + b_norm * 0.1804375
        y = r_norm * 0.2126729 + g_norm * 0.7151522 + b_norm * 0.0721750
        z = r_norm * 0.0193339 + g_norm * 0.1191920 + b_norm * 0.9503041
        return x, y, z

    @staticmethod
    def xyz_to_lab(x, y, z):
        """XYZ -> Lab (D65)"""
        xn, yn, zn = 0.95047, 1.00000, 1.08883

        x_ratio = x / xn
        y_ratio = y / yn
        z_ratio = z / zn

        def f(t):
            if t > (6 / 29) ** 3:
                return t ** (1 / 3)
            else:
                return (1 / 3) * (29 / 6) ** 2 * t + 4 / 29

        fx = f(x_ratio)
        fy = f(y_ratio)
        fz = f(z_ratio)

        l = 116 * fy - 16
        a = 500 * (fx - fy)
        b = 200 * (fy - fz)
        return l, a, b

    @staticmethod
    def lab_to_xyz(l, a, b):
        """Lab -> XYZ (D65)"""
        xn, yn, zn = 0.95047, 1.00000, 1.08883

        fy = (l + 16) / 116
        fx = a / 500 + fy
        fz = fy - b / 200

        def inv_f(t):
            if t > 6 / 29:
                return t ** 3
            else:
                return 3 * (6 / 29) ** 2 * (t - 4 / 29)

        x = inv_f(fx) * xn
        y = inv_f(fy) * yn
        z = inv_f(fz) * zn
        return x, y, z

    @staticmethod
    def xyz_to_rgb(x, y, z):
        """XYZ -> RGB [0,255] (стандартный D65)"""
        r_linear = x * 3.2404542 + y * -1.5371385 + z * -0.4985314
        g_linear = x * -0.9692660 + y * 1.8760108 + z * 0.0415560
        b_linear = x * 0.0556434 + y * -0.2040259 + z * 1.0572252

        def inv_gamma(c):
            if c <= 0.0031308:
                return 12.92 * c
            else:
                return 1.055 * (c ** (1 / 2.4)) - 0.055

        r = inv_gamma(r_linear)
        g = inv_gamma(g_linear)
        b = inv_gamma(b_linear)

        r = max(0, min(1, r)) * 255
        g = max(0, min(1, g)) * 255
        b = max(0, min(1, b)) * 255
        return r, g, b

    @staticmethod
    def rgb_to_lab(r, g, b):
        """RGB [0,255] -> Lab"""
        x, y, z = ColorConverter.rgb_to_xyz(r, g, b)
        return ColorConverter.xyz_to_lab(x, y, z)

    @staticmethod
    def lab_to_rgb(l, a, b):
        """Lab -> RGB [0,255]"""
        x, y, z = ColorConverter.lab_to_xyz(l, a, b)
        return ColorConverter.xyz_to_rgb(x, y, z)

class ColorConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Color Converter - CMYK ↔ LAB ↔ HSV")
        self.root.geometry("900x600")
        self.converter = ColorConverter()
        self.updating = False
        self.warning_label = None

        self.current_rgb = (128, 128, 128)

        self.create_widgets()
        self.update_all_from_rgb()

    def create_widgets(self):
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10)

        tk.Button(top_frame, text="Выбрать из палитры", command=self.choose_color,
                  font=("Arial", 10), padx=10, pady=5).pack(side=tk.LEFT, padx=5)

        self.color_canvas = tk.Canvas(self.root, width=200, height=50, bg='#808080',
                                      relief=tk.RAISED, borderwidth=2)
        self.color_canvas.pack(pady=10)

        models_frame = tk.Frame(self.root)
        models_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        cmyk_frame = tk.LabelFrame(models_frame, text="CMYK (0-100%)", font=("Arial", 10, "bold"),
                                   padx=10, pady=10)
        cmyk_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        self.cmyk_vars = []
        self.cmyk_entries = []
        self.cmyk_sliders = []
        cmyk_labels = ['C', 'M', 'Y', 'K']
        for i, label in enumerate(cmyk_labels):
            tk.Label(cmyk_frame, text=label, font=("Arial", 10)).grid(row=0, column=i, padx=10, pady=5)

            var = tk.DoubleVar(value=50)
            self.cmyk_vars.append(var)
            entry = tk.Entry(cmyk_frame, textvariable=var, width=8, font=("Arial", 10), justify='center')
            entry.grid(row=1, column=i, padx=10, pady=5)
            entry.bind('<KeyRelease>', lambda e, idx=i: self.on_cmyk_entry_change(idx))
            self.cmyk_entries.append(entry)

            slider = tk.Scale(cmyk_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                              variable=var, length=120, showvalue=0,
                              command=lambda v, idx=i: self.on_cmyk_slider(idx))
            slider.grid(row=2, column=i, padx=10, pady=5)
            self.cmyk_sliders.append(slider)

        lab_frame = tk.LabelFrame(models_frame, text="LAB", font=("Arial", 10, "bold"),
                                  padx=10, pady=10)
        lab_frame.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")
        self.lab_vars = []
        self.lab_entries = []
        self.lab_sliders = []
        lab_labels = ['L*', 'a*', 'b*']
        lab_ranges = [(0, 100), (-128, 127), (-128, 127)]
        for i, (label, (min_val, max_val)) in enumerate(zip(lab_labels, lab_ranges)):
            tk.Label(lab_frame, text=label, font=("Arial", 10)).grid(row=0, column=i, padx=10, pady=5)

            var = tk.DoubleVar(value=(min_val + max_val) / 2)
            self.lab_vars.append(var)
            entry = tk.Entry(lab_frame, textvariable=var, width=8, font=("Arial", 10), justify='center')
            entry.grid(row=1, column=i, padx=10, pady=5)
            entry.bind('<KeyRelease>', lambda e, idx=i: self.on_lab_entry_change(idx))
            self.lab_entries.append(entry)

            slider = tk.Scale(lab_frame, from_=min_val, to=max_val, orient=tk.HORIZONTAL,
                              variable=var, length=120, showvalue=0,
                              command=lambda v, idx=i: self.on_lab_slider(idx))
            slider.grid(row=2, column=i, padx=10, pady=5)
            self.lab_sliders.append(slider)

        hsv_frame = tk.LabelFrame(models_frame, text="HSV", font=("Arial", 10, "bold"),
                                  padx=10, pady=10)
        hsv_frame.grid(row=0, column=2, padx=10, pady=5, sticky="nsew")
        self.hsv_vars = []
        self.hsv_entries = []
        self.hsv_sliders = []
        hsv_labels = ['H°', 'S%', 'V%']
        hsv_ranges = [(0, 360), (0, 100), (0, 100)]
        for i, (label, (min_val, max_val)) in enumerate(zip(hsv_labels, hsv_ranges)):
            tk.Label(hsv_frame, text=label, font=("Arial", 10)).grid(row=0, column=i, padx=10, pady=5)

            var = tk.DoubleVar(value=(min_val + max_val) / 2)
            self.hsv_vars.append(var)
            entry = tk.Entry(hsv_frame, textvariable=var, width=8, font=("Arial", 10), justify='center')
            entry.grid(row=1, column=i, padx=10, pady=5)
            entry.bind('<KeyRelease>', lambda e, idx=i: self.on_hsv_entry_change(idx))
            self.hsv_entries.append(entry)

            slider = tk.Scale(hsv_frame, from_=min_val, to=max_val, orient=tk.HORIZONTAL,
                              variable=var, length=120, showvalue=0,
                              command=lambda v, idx=i: self.on_hsv_slider(idx))
            slider.grid(row=2, column=i, padx=10, pady=5)
            self.hsv_sliders.append(slider)

        self.warning_label = tk.Label(self.root, text="", fg="red", font=("Arial", 9))
        self.warning_label.pack(pady=5)

        models_frame.columnconfigure(0, weight=1)
        models_frame.columnconfigure(1, weight=1)
        models_frame.columnconfigure(2, weight=1)

    def choose_color(self):
        """Открытие диалога выбора цвета"""
        color_result = colorchooser.askcolor(title="Выберите цвет", initialcolor=self.get_hex_color())
        if color_result and color_result[0] is not None:
            r, g, b = map(int, color_result[0])
            self.current_rgb = (r, g, b)
            self.update_all_from_rgb()

    def get_hex_color(self):
        """Возвращает текущий цвет в формате HEX"""
        return f'#{int(self.current_rgb[0]):02x}{int(self.current_rgb[1]):02x}{int(self.current_rgb[2]):02x}'

    def update_color_display(self):
        """Обновление отображения цвета"""
        hex_color = self.get_hex_color()
        self.color_canvas.config(bg=hex_color)

    def show_warning(self, message):
        """Отображение предупреждения"""
        self.warning_label.config(text=message)
        self.root.after(3000, lambda: self.warning_label.config(text=""))

    def update_all_from_rgb(self):
        """Обновление всех моделей из текущего RGB"""
        if self.updating:
            return
        self.updating = True

        r, g, b = self.current_rgb

        try:
            c, m, y, k = self.converter.rgb_to_cmyk(r, g, b)
            self.cmyk_vars[0].set(round(c * 100, 1))
            self.cmyk_vars[1].set(round(m * 100, 1))
            self.cmyk_vars[2].set(round(y * 100, 1))
            self.cmyk_vars[3].set(round(k * 100, 1))

            l, a, b_lab = self.converter.rgb_to_lab(r, g, b)
            self.lab_vars[0].set(round(l, 1))
            self.lab_vars[1].set(round(a, 1))
            self.lab_vars[2].set(round(b_lab, 1))

            h, s, v = self.converter.rgb_to_hsv(r, g, b)
            self.hsv_vars[0].set(round(h, 1))
            self.hsv_vars[1].set(round(s * 100, 1))
            self.hsv_vars[2].set(round(v * 100, 1))

            self.update_color_display()
        except Exception as e:
            self.show_warning(f"Ошибка преобразования: {str(e)}")
        finally:
            self.updating = False

    def on_cmyk_entry_change(self, index):
        """Обработка изменения CMYK через поле ввода"""
        if self.updating:
            return
        try:
            c = max(0, min(100, float(self.cmyk_entries[0].get()))) / 100
            m = max(0, min(100, float(self.cmyk_entries[1].get()))) / 100
            y = max(0, min(100, float(self.cmyk_entries[2].get()))) / 100
            k = max(0, min(100, float(self.cmyk_entries[3].get()))) / 100

            r, g, b = self.converter.cmyk_to_rgb(c, m, y, k)
            self.current_rgb = (r, g, b)
            self.update_all_from_rgb()
        except (ValueError, TypeError):
            pass

    def on_cmyk_slider(self, index):
        """Обработка изменения CMYK через ползунок"""
        self.on_cmyk_entry_change(index)

    def on_lab_entry_change(self, index):
        """Обработка изменения LAB через поле ввода"""
        if self.updating:
            return
        try:
            l = float(self.lab_entries[0].get())
            a = float(self.lab_entries[1].get())
            b = float(self.lab_entries[2].get())

            r, g, b = self.converter.lab_to_rgb(l, a, b)

            if any(val < 0 or val > 255 for val in (r, g, b)):
                self.show_warning("Цвет вышел за границы RGB. Производится обрезание.")
                r = max(0, min(255, r))
                g = max(0, min(255, g))
                b = max(0, min(255, b))

            self.current_rgb = (r, g, b)
            self.update_all_from_rgb()
        except (ValueError, TypeError):
            pass

    def on_lab_slider(self, index):
        """Обработка изменения LAB через ползунок"""
        self.on_lab_entry_change(index)

    def on_hsv_entry_change(self, index):
        """Обработка изменения HSV через поле ввода"""
        if self.updating:
            return
        try:
            h = max(0, min(360, float(self.hsv_entries[0].get())))
            s = max(0, min(100, float(self.hsv_entries[1].get()))) / 100
            v = max(0, min(100, float(self.hsv_entries[2].get()))) / 100

            r, g, b = self.converter.hsv_to_rgb(h, s, v)
            self.current_rgb = (r, g, b)
            self.update_all_from_rgb()
        except (ValueError, TypeError):
            pass

    def on_hsv_slider(self, index):
        """Обработка изменения HSV через ползунок"""
        self.on_hsv_entry_change(index)

def main():
    root = tk.Tk()
    app = ColorConverterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()