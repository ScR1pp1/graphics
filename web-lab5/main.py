import tkinter as tk
from tkinter import filedialog, messagebox
import math


class LiangBarskyClipper:
    @staticmethod
    def clip(segment, clip_window):
        x1, y1, x2, y2 = segment
        xmin, ymin, xmax, ymax = clip_window

        dx = x2 - x1
        dy = y2 - y1

        p = [-dx, dx, -dy, dy]
        q = [x1 - xmin, xmax - x1, y1 - ymin, ymax - y1]

        u1 = 0.0
        u2 = 1.0

        for i in range(4):
            if p[i] == 0:
                if q[i] < 0:
                    return None
            else:
                r = q[i] / p[i]
                if p[i] < 0:
                    u1 = max(u1, r)
                else:
                    u2 = min(u2, r)

        if u1 > u2:
            return None

        nx1 = x1 + u1 * dx
        ny1 = y1 + u1 * dy
        nx2 = x1 + u2 * dx
        ny2 = y1 + u2 * dy

        return (nx1, ny1, nx2, ny2)


class PolygonClipper:
    @staticmethod
    def clip(subject_polygon, clip_polygon):
        if len(subject_polygon) < 3 or len(clip_polygon) < 3:
            return []

        result = subject_polygon.copy()

        for i in range(len(clip_polygon)):
            if len(result) == 0:
                break

            input_list = result
            result = []

            clip_start = clip_polygon[i]
            clip_end = clip_polygon[(i + 1) % len(clip_polygon)]

            for j in range(len(input_list)):
                current_point = input_list[j]
                next_point = input_list[(j + 1) % len(input_list)]

                current_inside = PolygonClipper.is_inside(current_point, clip_start, clip_end)
                next_inside = PolygonClipper.is_inside(next_point, clip_start, clip_end)

                if current_inside:
                    if next_inside:
                        result.append(next_point)
                    else:
                        intersection = PolygonClipper.get_intersection(
                            current_point, next_point, clip_start, clip_end
                        )
                        if intersection:
                            result.append(intersection)
                else:
                    if next_inside:
                        intersection = PolygonClipper.get_intersection(
                            current_point, next_point, clip_start, clip_end
                        )
                        if intersection:
                            result.append(intersection)
                            result.append(next_point)
                    else:
                        pass

        return result

    @staticmethod
    def is_inside(point, line_start, line_end):
        x, y = point
        x1, y1 = line_start
        x2, y2 = line_end

        return (x2 - x1) * (y - y1) - (y2 - y1) * (x - x1) >= 0

    @staticmethod
    def get_intersection(line1_start, line1_end, line2_start, line2_end):
        x1, y1 = line1_start
        x2, y2 = line1_end
        x3, y3 = line2_start
        x4, y4 = line2_end

        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)

        if abs(denom) < 1e-10:
            return None

        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom

        if 0 <= t <= 1:
            x = x1 + t * (x2 - x1)
            y = y1 + t * (y2 - y1)
            return (x, y)

        return None


class GraphicsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная работа 5 - Вариант 5")
        self.root.geometry("1400x900")

        self.segments = []
        self.clip_window_rect = (0, 0, 0, 0)
        self.original_segments = []
        self.clipped_segments = []

        self.subject_polygon = []
        self.clip_polygon = []
        self.clipped_subject_polygon = []
        self.original_subject_polygon = []
        self.original_clip_polygon = []

        self.canvas_width = 800
        self.canvas_height = 600
        self.scale = 20
        self.offset_x = self.canvas_width // 2
        self.offset_y = self.canvas_height // 2

        self.create_widgets()
        self.init_canvas(self.canvas_segments)
        self.init_canvas(self.canvas_polygon_clipping)

    def create_widgets(self):
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        control_frame = tk.Frame(main_frame, width=350, bg='#f0f0f0', relief=tk.RAISED, borderwidth=2)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        control_frame.pack_propagate(False)

        info_frame = tk.LabelFrame(control_frame, text="Вариант 5", padx=10, pady=10, bg='#f0f0f0', fg='#000000')
        info_frame.pack(fill=tk.X, padx=5, pady=5)

        info_text = tk.Text(info_frame, height=8, width=40, wrap=tk.WORD, bg='#ffffff', fg='#000000')
        info_text.insert(tk.END, "Вариант 5\n\n")
        info_text.insert(tk.END, "Часть 1:\n")
        info_text.insert(tk.END, "• Алгоритм Лианга-Барски\n")
        info_text.insert(tk.END, "• Отсечение отрезков\n\n")
        info_text.insert(tk.END, "Часть 2:\n")
        info_text.insert(tk.END, "• Отсечение выпуклого многоугольника\n")
        info_text.insert(tk.END, "• Выпуклым многоугольником\n")
        info_text.config(state=tk.DISABLED)
        info_text.pack()

        file_frame = tk.LabelFrame(control_frame, text="Управление файлами", padx=10, pady=10, bg='#f0f0f0', fg='#000000')
        file_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Button(file_frame, text="Загрузить файл данных",
                  command=self.load_file, width=30,
                  bg='#4CAF50', fg='#000000', activebackground='#45a049',
                  font=('Arial', 10)).pack(pady=5)

        tk.Button(file_frame, text="Создать тестовые данные",
                  command=self.create_test_data, width=30,
                  bg='#2196F3', fg='#000000', activebackground='#1976D2',
                  font=('Arial', 10)).pack(pady=5)

        tk.Button(file_frame, text="Очистить всё",
                  command=self.clear_all, width=30,
                  bg='#f44336', fg='#000000', activebackground='#d32f2f',
                  font=('Arial', 10)).pack(pady=5)

        segments_frame = tk.LabelFrame(control_frame, text="Часть 1: Отсечение отрезков",
                                       padx=10, pady=10, bg='#f0f0f0', fg='#000000')
        segments_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Button(segments_frame, text="Выполнить отсечение отрезков",
                  command=self.clip_segments, width=30,
                  bg='#FF9800', fg='#000000', activebackground='#F57C00',
                  font=('Arial', 10)).pack(pady=5)

        tk.Button(segments_frame, text="Показать исходные отрезки",
                  command=self.show_original_segments, width=30,
                  bg='#9C27B0', fg='#000000', activebackground='#7B1FA2',
                  font=('Arial', 10)).pack(pady=5)

        polygon_frame = tk.LabelFrame(control_frame, text="Часть 2: Отсечение многоугольника",
                                      padx=10, pady=10, bg='#f0f0f0', fg='#000000')
        polygon_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Button(polygon_frame, text="Выполнить отсечение многоугольника",
                  command=self.clip_convex_polygon, width=30,
                  bg='#009688', fg='#000000', activebackground='#00796B',
                  font=('Arial', 10)).pack(pady=5)

        tk.Button(polygon_frame, text="Показать исходные многоугольники",
                  command=self.show_original_polygons, width=30,
                  bg='#795548', fg='#000000', activebackground='#5D4037',
                  font=('Arial', 10)).pack(pady=5)

        self.status_label = tk.Label(control_frame, text="Готово к работе",
                                     relief=tk.SUNKEN, anchor=tk.W,
                                     bg='#ffffff', fg='#000000',
                                     font=('Arial', 10))
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

        graphics_frame = tk.Frame(main_frame, bg='#f0f0f0')
        graphics_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        canvas_frame1 = tk.LabelFrame(graphics_frame, text="Часть 1: Отсечение отрезков",
                                      padx=10, pady=10, bg='#f0f0f0', fg='#000000')
        canvas_frame1.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.canvas_segments = tk.Canvas(canvas_frame1, width=self.canvas_width,
                                         height=self.canvas_height, bg='white')
        self.canvas_segments.pack(fill=tk.BOTH, expand=True)

        canvas_frame2 = tk.LabelFrame(graphics_frame, text="Часть 2: Отсечение многоугольника",
                                      padx=10, pady=10, bg='#f0f0f0', fg='#000000')
        canvas_frame2.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.canvas_polygon_clipping = tk.Canvas(canvas_frame2, width=self.canvas_width,
                                                 height=self.canvas_height, bg='white')
        self.canvas_polygon_clipping.pack(fill=tk.BOTH, expand=True)

    def init_canvas(self, canvas):
        canvas.delete("all")

        for x in range(0, self.canvas_width, 20):
            canvas.create_line(x, 0, x, self.canvas_height, fill='#f0f0f0')
        for y in range(0, self.canvas_height, 20):
            canvas.create_line(0, y, self.canvas_width, y, fill='#f0f0f0')

        canvas.create_line(0, self.offset_y, self.canvas_width, self.offset_y,
                           fill='black', width=1)
        canvas.create_line(self.offset_x, 0, self.offset_x, self.canvas_height,
                           fill='black', width=1)

        canvas.create_text(self.canvas_width - 10, self.offset_y - 10, text="X",
                           font=("Arial", 10, "bold"))
        canvas.create_text(self.offset_x + 10, 10, text="Y", font=("Arial", 10, "bold"))

        for i in range(-20, 21):
            x = self.offset_x + i * self.scale
            if i % 5 == 0 and i != 0:
                canvas.create_line(x, self.offset_y - 5, x, self.offset_y + 5,
                                   fill='black', width=2)
                canvas.create_text(x, self.offset_y + 15, text=str(i),
                                   font=("Arial", 8))

            y = self.offset_y - i * self.scale
            if i % 5 == 0 and i != 0:
                canvas.create_line(self.offset_x - 5, y, self.offset_x + 5, y,
                                   fill='black', width=2)
                canvas.create_text(self.offset_x - 15, y, text=str(i),
                                   font=("Arial", 8))

    def transform_point(self, x, y):
        canvas_x = self.offset_x + x * self.scale
        canvas_y = self.offset_y - y * self.scale
        return canvas_x, canvas_y

    def draw_clip_window(self, canvas):
        if not self.clip_window_rect or self.clip_window_rect == (0, 0, 0, 0):
            return

        xmin, ymin, xmax, ymax = self.clip_window_rect
        x1, y1 = self.transform_point(xmin, ymax)
        x2, y2 = self.transform_point(xmax, ymin)

        canvas.create_rectangle(x1, y1, x2, y2, outline='blue',
                                width=2, dash=(5, 5), fill='lightblue')

    def draw_segment(self, canvas, segment, color='red', width=2):
        x1, y1, x2, y2 = segment
        cx1, cy1 = self.transform_point(x1, y1)
        cx2, cy2 = self.transform_point(x2, y2)
        canvas.create_line(cx1, cy1, cx2, cy2, fill=color, width=width)

    def draw_polygon(self, canvas, polygon, color='green', fill_color=None, width=2, tag=""):
        if len(polygon) < 2:
            return

        canvas_coords = []
        for point in polygon:
            x, y = point
            cx, cy = self.transform_point(x, y)
            canvas_coords.extend([cx, cy])

        if len(polygon) >= 3:
            if fill_color is None:
                fill_color = color + '40'

            polygon_id = canvas.create_polygon(canvas_coords, outline=color,
                                               fill=fill_color, width=width, tags=tag)

            for i, point in enumerate(polygon):
                x, y = point
                cx, cy = self.transform_point(x, y)
                canvas.create_oval(cx - 3, cy - 3, cx + 3, cy + 3, fill=color, outline='black')
                canvas.create_text(cx, cy - 10, text=str(i + 1), font=("Arial", 8, "bold"))

            return polygon_id
        else:
            canvas.create_line(canvas_coords, fill=color, width=width, tags=tag)
            return None

    def load_file(self):
        filename = filedialog.askopenfilename(
            title="Выберите файл с данными",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )

        if not filename:
            return

        try:
            with open(filename, 'r') as f:
                lines = [line.strip() for line in f if line.strip()]

            line_idx = 0

            if line_idx < len(lines):
                n_segments = int(lines[line_idx])
                line_idx += 1

                self.segments = []
                for i in range(n_segments):
                    if line_idx < len(lines):
                        coords = list(map(float, lines[line_idx].split()))
                        if len(coords) == 4:
                            self.segments.append(tuple(coords))
                        line_idx += 1

                self.original_segments = self.segments.copy()
                self.clipped_segments = []

            if line_idx < len(lines):
                window_coords = list(map(float, lines[line_idx].split()))
                if len(window_coords) == 4:
                    self.clip_window_rect = tuple(window_coords)
                line_idx += 1

            self.subject_polygon = []
            self.clip_polygon = []

            if line_idx < len(lines):
                n_subject = int(lines[line_idx])
                line_idx += 1

                for i in range(n_subject):
                    if line_idx < len(lines):
                        coords = list(map(float, lines[line_idx].split()))
                        if len(coords) >= 2:
                            self.subject_polygon.append((coords[0], coords[1]))
                        line_idx += 1

            if line_idx < len(lines):
                n_clip = int(lines[line_idx])
                line_idx += 1

                for i in range(n_clip):
                    if line_idx < len(lines):
                        coords = list(map(float, lines[line_idx].split()))
                        if len(coords) >= 2:
                            self.clip_polygon.append((coords[0], coords[1]))
                        line_idx += 1

            self.original_subject_polygon = self.subject_polygon.copy()
            self.original_clip_polygon = self.clip_polygon.copy()
            self.clipped_subject_polygon = []

            self.redraw_all()

            self.status_label.config(
                text=f"Загружено: {len(self.segments)} отрезков, "
                     f"{len(self.subject_polygon)} и {len(self.clip_polygon)} вершин многоугольников"
            )

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при загрузке файла:\n{str(e)}")

    def create_test_data(self):
        self.clip_window_rect = (-5, -5, 10, 10)

        self.segments = [
            (-10, -5, 15, 10),
            (5, -8, 12, 15),
            (-8, 12, 10, -10),
            (-3, -3, -3, 15),
            (2, -7, 2, 12),
            (-7, 3, 12, 3),
            (-15, -15, -15, 15),
            (20, -5, 20, 10),
            (0, 0, 5, 5)
        ]

        self.original_segments = self.segments.copy()
        self.clipped_segments = []

        self.subject_polygon = [
            (0, 0), (2, 5), (4, 0), (6, 5), (8, 0),
            (8, -3), (4, -5), (0, -3)
        ]

        self.clip_polygon = [
            (1, -2), (7, -2), (4, 6)
        ]

        self.original_subject_polygon = self.subject_polygon.copy()
        self.original_clip_polygon = self.clip_polygon.copy()
        self.clipped_subject_polygon = []

        self.redraw_all()

        self.status_label.config(
            text="Созданы тестовые данные: 9 отрезков, 2 многоугольника"
        )

    def redraw_all(self):
        self.init_canvas(self.canvas_segments)
        self.draw_clip_window(self.canvas_segments)

        for segment in self.segments:
            self.draw_segment(self.canvas_segments, segment, 'red', 2)

        self.init_canvas(self.canvas_polygon_clipping)

        if self.clip_polygon:
            self.draw_polygon(self.canvas_polygon_clipping, self.clip_polygon,
                              'blue', 'lightblue', 2, "clip_polygon")

        if self.subject_polygon:
            self.draw_polygon(self.canvas_polygon_clipping, self.subject_polygon,
                              'green', 'lightgreen', 2, "subject_polygon")

    def clip_segments(self):
        if not self.segments:
            messagebox.showwarning("Внимание", "Нет данных для отсечения отрезков")
            return

        clipper = LiangBarskyClipper()
        self.clipped_segments = []

        for segment in self.original_segments:
            clipped = clipper.clip(segment, self.clip_window_rect)
            if clipped:
                self.clipped_segments.append(clipped)

        self.init_canvas(self.canvas_segments)
        self.draw_clip_window(self.canvas_segments)

        for segment in self.original_segments:
            self.draw_segment(self.canvas_segments, segment, '#ffaaaa', 2)

        for segment in self.clipped_segments:
            self.draw_segment(self.canvas_segments, segment, 'darkgreen', 3)

        self.status_label.config(
            text=f"Отсечено отрезков: {len(self.clipped_segments)} из {len(self.original_segments)}"
        )

    def clip_convex_polygon(self):
        if not self.subject_polygon or len(self.subject_polygon) < 3:
            messagebox.showwarning("Внимание", "Нет отсекаемого многоугольника")
            return

        if not self.clip_polygon or len(self.clip_polygon) < 3:
            messagebox.showwarning("Внимание", "Нет отсекающего многоугольника")
            return

        clipper = PolygonClipper()
        self.clipped_subject_polygon = clipper.clip(
            self.original_subject_polygon,
            self.original_clip_polygon
        )

        self.init_canvas(self.canvas_polygon_clipping)

        self.draw_polygon(self.canvas_polygon_clipping, self.original_clip_polygon,
                          'blue', 'lightblue', 2, "clip_polygon")

        self.draw_polygon(self.canvas_polygon_clipping, self.original_subject_polygon,
                          '#aaffaa', '#aaffaa40', 2, "subject_original")

        if self.clipped_subject_polygon:
            self.draw_polygon(self.canvas_polygon_clipping, self.clipped_subject_polygon,
                              'red', '#ff000040', 3, "clipped_result")

            area = self.calculate_polygon_area(self.clipped_subject_polygon)
            area_original = self.calculate_polygon_area(self.original_subject_polygon)
            percentage = (area / area_original * 100) if area_original > 0 else 0

            self.status_label.config(
                text=f"Многоугольник отсечен. Вершин: {len(self.clipped_subject_polygon)} "
                     f"(Площадь: {area:.1f}, {percentage:.1f}% от исходной)"
            )
        else:
            self.status_label.config(text="Многоугольник полностью отсечен")

    def calculate_polygon_area(self, polygon):
        if len(polygon) < 3:
            return 0

        area = 0
        n = len(polygon)

        for i in range(n):
            x1, y1 = polygon[i]
            x2, y2 = polygon[(i + 1) % n]
            area += x1 * y2 - x2 * y1

        return abs(area) / 2

    def show_original_segments(self):
        self.segments = self.original_segments.copy()
        self.clipped_segments = []
        self.redraw_all()
        self.status_label.config(text="Показаны исходные отрезки")

    def show_original_polygons(self):
        self.subject_polygon = self.original_subject_polygon.copy()
        self.clip_polygon = self.original_clip_polygon.copy()
        self.clipped_subject_polygon = []
        self.redraw_all()
        self.status_label.config(text="Показаны исходные многоугольники")

    def clear_all(self):
        self.segments = []
        self.clip_window_rect = (0, 0, 0, 0)
        self.original_segments = []
        self.clipped_segments = []

        self.subject_polygon = []
        self.clip_polygon = []
        self.clipped_subject_polygon = []
        self.original_subject_polygon = []
        self.original_clip_polygon = []

        self.init_canvas(self.canvas_segments)
        self.init_canvas(self.canvas_polygon_clipping)
        self.status_label.config(text="Все данные очищены")


def main():
    root = tk.Tk()
    app = GraphicsApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()