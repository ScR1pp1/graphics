import tkinter as tk
from tkinter import filedialog, messagebox
import math

class LiangBarskyClipper:
    """Реализация алгоритма Лианга-Барски для отсечения отрезков"""

    @staticmethod
    def clip(segment, clip_window):
        """Отсечение отрезка алгоритмом Лианга-Барски"""
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

class SutherlandHodgmanClipper:
    """Реализация алгоритма Сазерленда-Ходжмана для отсечения многоугольника"""

    @staticmethod
    def clip(polygon, clip_window):
        """Отсечение многоугольника выпуклым окном"""
        if len(polygon) < 3:
            return polygon

        edges = [
            ('left', clip_window[0]),
            ('right', clip_window[2]),
            ('bottom', clip_window[1]),
            ('top', clip_window[3])
        ]

        output_polygon = polygon

        for edge_type, edge_value in edges:
            if len(output_polygon) == 0:
                break

            input_polygon = output_polygon
            output_polygon = []

            input_polygon.append(input_polygon[0])

            for i in range(len(input_polygon) - 1):
                current = input_polygon[i]
                next_point = input_polygon[i + 1]

                current_inside = SutherlandHodgmanClipper._is_inside(current, edge_type, edge_value)
                next_inside = SutherlandHodgmanClipper._is_inside(next_point, edge_type, edge_value)

                if current_inside and next_inside:
                    output_polygon.append(next_point)
                elif current_inside and not next_inside:
                    intersect = SutherlandHodgmanClipper._get_intersection(
                        current, next_point, edge_type, edge_value, clip_window
                    )
                    if intersect:
                        output_polygon.append(intersect)
                elif not current_inside and next_inside:
                    intersect = SutherlandHodgmanClipper._get_intersection(
                        current, next_point, edge_type, edge_value, clip_window
                    )
                    if intersect:
                        output_polygon.append(intersect)
                        output_polygon.append(next_point)

            if len(output_polygon) == 0:
                break

        return output_polygon

    @staticmethod
    def _is_inside(point, edge_type, edge_value):
        """Проверка, находится ли точка внутри относительно ребра"""
        x, y = point
        if edge_type == 'left':
            return x >= edge_value
        elif edge_type == 'right':
            return x <= edge_value
        elif edge_type == 'bottom':
            return y >= edge_value
        elif edge_type == 'top':
            return y <= edge_value
        return True

    @staticmethod
    def _get_intersection(p1, p2, edge_type, edge_value, clip_window):
        """Нахождение точки пересечения отрезка с ребром"""
        x1, y1 = p1
        x2, y2 = p2

        if edge_type == 'left':
            if x1 == x2:
                return None
            t = (edge_value - x1) / (x2 - x1)
            y = y1 + t * (y2 - y1)
            return (edge_value, y)
        elif edge_type == 'right':
            if x1 == x2:
                return None
            t = (edge_value - x1) / (x2 - x1)
            y = y1 + t * (y2 - y1)
            return (edge_value, y)
        elif edge_type == 'bottom':
            if y1 == y2:
                return None
            t = (edge_value - y1) / (y2 - y1)
            x = x1 + t * (x2 - x1)
            return (x, edge_value)
        elif edge_type == 'top':
            if y1 == y2:
                return None
            t = (edge_value - y1) / (y2 - y1)
            x = x1 + t * (x2 - x1)
            return (x, edge_value)
        return None


class GraphicsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная работа 5 - Вариант 5")
        self.root.geometry("1200x800")

        self.segments = []
        self.polygon = []
        self.clip_window = (0, 0, 0, 0)
        self.original_segments = []
        self.original_polygon = []
        self.clipped_segments = []
        self.clipped_polygon = []

        self.canvas_width = 800
        self.canvas_height = 600
        self.scale = 20
        self.offset_x = self.canvas_width // 2
        self.offset_y = self.canvas_height // 2

        self.create_widgets()

        self.init_canvas(self.canvas_segments)
        self.init_canvas(self.canvas_polygon)

    def create_widgets(self):
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        control_frame = tk.Frame(main_frame, width=300, relief=tk.RAISED, borderwidth=2)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        control_frame.pack_propagate(False)

        info_frame = tk.LabelFrame(control_frame, text="Информация", padx=10, pady=10)
        info_frame.pack(fill=tk.X, padx=5, pady=5)

        info_text = tk.Text(info_frame, height=6, width=35, wrap=tk.WORD)
        info_text.insert(tk.END, "Вариант 5\n\n")
        info_text.insert(tk.END, "1. Алгоритм Лианга-Барски\n")
        info_text.insert(tk.END, "2. Отсечение выпуклого многоугольника\n")
        info_text.config(state=tk.DISABLED)
        info_text.pack()

        file_frame = tk.LabelFrame(control_frame, text="Управление файлами", padx=10, pady=10)
        file_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Button(file_frame, text="Загрузить файл",
                  command=self.load_file, width=25).pack(pady=5)
        tk.Button(file_frame, text="Создать тестовые данные",
                  command=self.create_test_data, width=25).pack(pady=5)
        tk.Button(file_frame, text="Очистить всё",
                  command=self.clear_all, width=25).pack(pady=5)

        segments_frame = tk.LabelFrame(control_frame, text="Отсечение отрезков", padx=10, pady=10)
        segments_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Button(segments_frame, text="Выполнить отсечение",
                  command=self.clip_segments, width=25).pack(pady=5)
        tk.Button(segments_frame, text="Показать исходные",
                  command=self.show_original_segments, width=25).pack(pady=5)

        polygon_frame = tk.LabelFrame(control_frame, text="Отсечение многоугольника", padx=10, pady=10)
        polygon_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Button(polygon_frame, text="Выполнить отсечение",
                  command=self.clip_polygon, width=25).pack(pady=5)
        tk.Button(polygon_frame, text="Показать исходный",
                  command=self.show_original_polygon, width=25).pack(pady=5)

        self.status_label = tk.Label(control_frame, text="Готово к работе",
                                     relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)

        graphics_frame = tk.Frame(main_frame)
        graphics_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        canvas_frame1 = tk.LabelFrame(graphics_frame, text="Отсечение отрезков (Лианга-Барски)",
                                      padx=10, pady=10)
        canvas_frame1.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.canvas_segments = tk.Canvas(canvas_frame1, width=self.canvas_width,
                                         height=self.canvas_height, bg='white')
        self.canvas_segments.pack(fill=tk.BOTH, expand=True)

        canvas_frame2 = tk.LabelFrame(graphics_frame, text="Отсечение выпуклого многоугольника",
                                      padx=10, pady=10)
        canvas_frame2.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.canvas_polygon = tk.Canvas(canvas_frame2, width=self.canvas_width,
                                        height=self.canvas_height, bg='white')
        self.canvas_polygon.pack(fill=tk.BOTH, expand=True)

    def init_canvas(self, canvas):
        """Инициализация координатной системы на холсте"""
        canvas.delete("all")

        for x in range(0, self.canvas_width, 20):
            canvas.create_line(x, 0, x, self.canvas_height, fill='#f0f0f0')
        for y in range(0, self.canvas_height, 20):
            canvas.create_line(0, y, self.canvas_width, y, fill='#f0f0f0')

        canvas.create_line(0, self.offset_y, self.canvas_width, self.offset_y,
                           fill='black', width=1)  # Ось X
        canvas.create_line(self.offset_x, 0, self.offset_x, self.canvas_height,
                           fill='black', width=1)  # Ось Y

        canvas.create_text(self.canvas_width - 10, self.offset_y - 10, text="X",
                           font=("Arial", 10))
        canvas.create_text(self.offset_x + 10, 10, text="Y", font=("Arial", 10))

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
        """Преобразование математических координат в координаты холста"""
        canvas_x = self.offset_x + x * self.scale
        canvas_y = self.offset_y - y * self.scale
        return canvas_x, canvas_y

    def draw_clip_window(self, canvas):
        """Рисование отсекающего окна"""
        xmin, ymin, xmax, ymax = self.clip_window

        x1, y1 = self.transform_point(xmin, ymax)
        x2, y2 = self.transform_point(xmax, ymin)

        canvas.create_rectangle(x1, y1, x2, y2, outline='blue',
                                width=2, dash=(5, 5), fill='lightblue')

    def draw_segment(self, canvas, segment, color='red', width=2):
        """Рисование отрезка"""
        x1, y1, x2, y2 = segment
        cx1, cy1 = self.transform_point(x1, y1)
        cx2, cy2 = self.transform_point(x2, y2)
        canvas.create_line(cx1, cy1, cx2, cy2, fill=color, width=width)

    def draw_polygon(self, canvas, polygon, color='green', width=2):
        """Рисование многоугольника"""
        if len(polygon) < 2:
            return

        canvas_coords = []
        for point in polygon:
            x, y = point
            cx, cy = self.transform_point(x, y)
            canvas_coords.extend([cx, cy])

        if len(polygon) >= 3:
            canvas.create_polygon(canvas_coords, outline=color,
                                  fill=color + '80', width=width)
        else:
            canvas.create_line(canvas_coords, fill=color, width=width)

    def load_file(self):
        """Загрузка данных из файла"""
        filename = filedialog.askopenfilename(
            title="Выберите файл с данными",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )

        if not filename:
            return

        try:
            with open(filename, 'r') as f:
                lines = f.readlines()

            n = int(lines[0].strip())

            self.segments = []
            for i in range(1, n + 1):
                coords = list(map(float, lines[i].strip().split()))
                if len(coords) == 4:
                    self.segments.append(tuple(coords))
                else:
                    messagebox.showwarning("Предупреждение",
                                           f"Строка {i + 1} содержит {len(coords)} чисел вместо 4")

            window_coords = list(map(float, lines[n + 1].strip().split()))
            if len(window_coords) == 4:
                self.clip_window = tuple(window_coords)
            else:
                messagebox.showerror("Ошибка",
                                     "Координаты окна должны содержать 4 числа")
                return

            self.original_segments = self.segments.copy()
            self.clipped_segments = []

            self.create_polygon_from_segments()

            self.redraw_all()

            self.status_label.config(text=f"Загружено: {n} отрезков")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при загрузке файла:\n{str(e)}")

    def create_polygon_from_segments(self):
        """Создание многоугольника из отрезков"""
        self.polygon = []

        if not self.segments:
            return

        num_points = min(5, len(self.segments))
        for i in range(num_points):
            x1, y1, x2, y2 = self.segments[i]
            self.polygon.append((x1, y1))

        if len(self.polygon) >= 3:
            self.polygon.append(self.polygon[0])

        self.original_polygon = self.polygon.copy()
        self.clipped_polygon = []

    def create_test_data(self):
        """Создание тестовых данных"""
        self.clip_window = (-5, -5, 10, 10)

        self.segments = [
            (-10, -5, 15, 10),
            (5, -8, 12, 15),
            (-8, 12, 10, -10),
            (-3, -3, -3, 15),
            (2, -7, 2, 12),
            (-7, 3, 12, 3)
        ]

        self.original_segments = self.segments.copy()
        self.clipped_segments = []

        self.create_polygon_from_segments()

        self.redraw_all()

        self.status_label.config(text="Созданы тестовые данные: 6 отрезков")

    def redraw_all(self):
        """Перерисовка всех объектов на холстах"""
        self.init_canvas(self.canvas_segments)
        self.init_canvas(self.canvas_polygon)

        self.draw_clip_window(self.canvas_segments)
        self.draw_clip_window(self.canvas_polygon)

        for segment in self.segments:
            self.draw_segment(self.canvas_segments, segment, 'red', 2)

        if self.polygon:
            self.draw_polygon(self.canvas_polygon, self.polygon, 'green', 2)

    def clip_segments(self):
        """Выполнение отсечения отрезков алгоритмом Лианга-Барски"""
        if not self.segments:
            messagebox.showwarning("Внимание", "Нет данных для отсечения")
            return

        clipper = LiangBarskyClipper()
        self.clipped_segments = []

        for segment in self.original_segments:
            clipped = clipper.clip(segment, self.clip_window)
            if clipped:
                self.clipped_segments.append(clipped)

        self.init_canvas(self.canvas_segments)
        self.draw_clip_window(self.canvas_segments)

        for segment in self.original_segments:
            self.draw_segment(self.canvas_segments, segment, '#ffaaaa', 2)

        for segment in self.clipped_segments:
            self.draw_segment(self.canvas_segments, segment, 'darkgreen', 3)

        self.status_label.config(
            text=f"Отсечено: {len(self.clipped_segments)} из {len(self.original_segments)} отрезков")

    def clip_polygon(self):
        """Выполнение отсечения многоугольника"""
        if not self.polygon or len(self.polygon) < 3:
            messagebox.showwarning("Внимание", "Нет данных многоугольника для отсечения")
            return

        clipper = SutherlandHodgmanClipper()
        self.clipped_polygon = clipper.clip(self.original_polygon, self.clip_window)

        self.init_canvas(self.canvas_polygon)
        self.draw_clip_window(self.canvas_polygon)

        self.draw_polygon(self.canvas_polygon, self.original_polygon, '#aaffaa', 2)

        if self.clipped_polygon:
            self.draw_polygon(self.canvas_polygon, self.clipped_polygon, 'darkblue', 3)

        self.status_label.config(text=f"Многоугольник отсечен. Вершин: {len(self.clipped_polygon)}")

    def show_original_segments(self):
        """Показать исходные отрезки"""
        self.segments = self.original_segments.copy()
        self.clipped_segments = []
        self.redraw_all()
        self.status_label.config(text="Показаны исходные отрезки")

    def show_original_polygon(self):
        """Показать исходный многоугольник"""
        self.polygon = self.original_polygon.copy()
        self.clipped_polygon = []
        self.redraw_all()
        self.status_label.config(text="Показан исходный многоугольник")

    def clear_all(self):
        """Очистка всех данных"""
        self.segments = []
        self.polygon = []
        self.original_segments = []
        self.original_polygon = []
        self.clipped_segments = []
        self.clipped_polygon = []
        self.clip_window = (0, 0, 0, 0)

        self.init_canvas(self.canvas_segments)
        self.init_canvas(self.canvas_polygon)
        self.status_label.config(text="Все данные очищены")

def main():
    root = tk.Tk()
    app = GraphicsApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()