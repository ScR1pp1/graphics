import sys
import time
import math
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class RasterizationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Алгоритмы растеризации')
        self.setGeometry(100, 100, 1200, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()

        control_panel = QGroupBox("Управление")
        control_layout = QVBoxLayout()

        self.algorithm_combo = QComboBox()
        self.algorithm_combo.addItems([
            "Пошаговый алгоритм",
            "Алгоритм ЦДА",
            "Алгоритм Брезенхема (отрезок)",
            "Алгоритм Брезенхема (окружность)",
            "Алгоритм Кастла-Питвея (эллипс)"
        ])
        control_layout.addWidget(QLabel("Выбор алгоритма:"))
        control_layout.addWidget(self.algorithm_combo)

        self.x1_spin = QSpinBox()
        self.x1_spin.setRange(-100, 100)
        self.x1_spin.setValue(0)
        self.y1_spin = QSpinBox()
        self.y1_spin.setRange(-100, 100)
        self.y1_spin.setValue(0)
        self.x2_spin = QSpinBox()
        self.x2_spin.setRange(-100, 100)
        self.x2_spin.setValue(20)
        self.y2_spin = QSpinBox()
        self.y2_spin.setRange(-100, 100)
        self.y2_spin.setValue(15)

        segment_group = QGroupBox("Параметры отрезка")
        segment_layout = QGridLayout()
        segment_layout.addWidget(QLabel("x1:"), 0, 0)
        segment_layout.addWidget(self.x1_spin, 0, 1)
        segment_layout.addWidget(QLabel("y1:"), 0, 2)
        segment_layout.addWidget(self.y1_spin, 0, 3)
        segment_layout.addWidget(QLabel("x2:"), 1, 0)
        segment_layout.addWidget(self.x2_spin, 1, 1)
        segment_layout.addWidget(QLabel("y2:"), 1, 2)
        segment_layout.addWidget(self.y2_spin, 1, 3)
        segment_group.setLayout(segment_layout)
        control_layout.addWidget(segment_group)

        self.cx_spin = QSpinBox()
        self.cx_spin.setRange(-100, 100)
        self.cx_spin.setValue(0)
        self.cy_spin = QSpinBox()
        self.cy_spin.setRange(-100, 100)
        self.cy_spin.setValue(0)
        self.radius_spin = QSpinBox()
        self.radius_spin.setRange(1, 100)
        self.radius_spin.setValue(15)
        self.rx_spin = QSpinBox()
        self.rx_spin.setRange(1, 100)
        self.rx_spin.setValue(20)
        self.ry_spin = QSpinBox()
        self.ry_spin.setRange(1, 100)
        self.ry_spin.setValue(15)

        circle_group = QGroupBox("Параметры окружности/эллипса")
        circle_layout = QGridLayout()
        circle_layout.addWidget(QLabel("Центр X:"), 0, 0)
        circle_layout.addWidget(self.cx_spin, 0, 1)
        circle_layout.addWidget(QLabel("Центр Y:"), 0, 2)
        circle_layout.addWidget(self.cy_spin, 0, 3)
        circle_layout.addWidget(QLabel("Радиус:"), 1, 0)
        circle_layout.addWidget(self.radius_spin, 1, 1)
        circle_layout.addWidget(QLabel("Rx (эллипс):"), 2, 0)
        circle_layout.addWidget(self.rx_spin, 2, 1)
        circle_layout.addWidget(QLabel("Ry (эллипс):"), 2, 2)
        circle_layout.addWidget(self.ry_spin, 2, 3)
        circle_group.setLayout(circle_layout)
        control_layout.addWidget(circle_group)

        display_group = QGroupBox("Настройки отображения")
        display_layout = QVBoxLayout()

        self.grid_check = QCheckBox("Показывать сетку")
        self.grid_check.setChecked(True)
        display_layout.addWidget(self.grid_check)

        self.axes_check = QCheckBox("Показывать оси")
        self.axes_check.setChecked(True)
        display_layout.addWidget(self.axes_check)

        self.coords_check = QCheckBox("Показывать координаты")
        self.coords_check.setChecked(True)
        display_layout.addWidget(self.coords_check)

        self.smooth_check = QCheckBox("Сглаживание (Wu)")
        self.smooth_check.setChecked(False)
        display_layout.addWidget(self.smooth_check)

        display_group.setLayout(display_layout)
        control_layout.addWidget(display_group)

        self.draw_btn = QPushButton("Построить")
        self.draw_btn.clicked.connect(self.draw)
        control_layout.addWidget(self.draw_btn)

        self.clear_btn = QPushButton("Очистить")
        self.clear_btn.clicked.connect(self.clear_canvas)
        control_layout.addWidget(self.clear_btn)

        self.info_label = QLabel("")
        self.info_label.setWordWrap(True)
        control_layout.addWidget(self.info_label)

        self.time_label = QLabel("")
        control_layout.addWidget(self.time_label)

        control_panel.setLayout(control_layout)
        control_panel.setMaximumWidth(350)

        self.canvas = CanvasWidget()

        main_layout.addWidget(control_panel)
        main_layout.addWidget(self.canvas, 1)

        central_widget.setLayout(main_layout)

        self.algorithm_combo.currentIndexChanged.connect(self.on_algorithm_changed)
        self.on_algorithm_changed()

        self.draw()

    def on_algorithm_changed(self):
        algorithm = self.algorithm_combo.currentText()
        pass

    def draw(self):
        algorithm = self.algorithm_combo.currentText()

        if algorithm in ["Пошаговый алгоритм", "Алгоритм ЦДА",
                         "Алгоритм Брезенхема (отрезок)"]:
            x1, y1 = self.x1_spin.value(), self.y1_spin.value()
            x2, y2 = self.x2_spin.value(), self.y2_spin.value()

            start_time = time.perf_counter()

            if algorithm == "Пошаговый алгоритм":
                points = self.step_by_step(x1, y1, x2, y2)
                calculations = self.get_step_calculations(x1, y1, x2, y2)
            elif algorithm == "Алгоритм ЦДА":
                points = self.dda(x1, y1, x2, y2)
                calculations = self.get_dda_calculations(x1, y1, x2, y2)
            else:
                points = self.bresenham_line(x1, y1, x2, y2)
                calculations = self.get_bresenham_line_calculations(x1, y1, x2, y2)

            elapsed = (time.perf_counter() - start_time) * 1000  # в мс

        elif algorithm == "Алгоритм Брезенхема (окружность)":
            cx, cy = self.cx_spin.value(), self.cy_spin.value()
            r = self.radius_spin.value()

            start_time = time.perf_counter()
            points = self.bresenham_circle(cx, cy, r)
            calculations = self.get_circle_calculations(cx, cy, r)
            elapsed = (time.perf_counter() - start_time) * 1000

        else:
            cx, cy = self.cx_spin.value(), self.cy_spin.value()
            rx, ry = self.rx_spin.value(), self.ry_spin.value()

            start_time = time.perf_counter()
            points = self.castle_pitway(cx, cy, rx, ry)
            calculations = "Алгоритм Кастла-Питвея для эллипса"
            elapsed = (time.perf_counter() - start_time) * 1000

        if self.smooth_check.isChecked() and algorithm in ["Пошаговый алгоритм",
                                                           "Алгоритм ЦДА",
                                                           "Алгоритм Брезенхема (отрезок)"]:
            points = self.wu_line(x1, y1, x2, y2)
            calculations += "\n\nСглаживание по алгоритму Ву"

        self.canvas.set_points(points)
        self.canvas.show_grid = self.grid_check.isChecked()
        self.canvas.show_axes = self.axes_check.isChecked()
        self.canvas.show_coords = self.coords_check.isChecked()
        self.canvas.update()

        self.info_label.setText(f"Алгоритм: {algorithm}\n\n{calculations}")
        self.time_label.setText(f"Время выполнения: {elapsed:.6f} мс\n"
                                f"Количество точек: {len(points)}")

    def clear_canvas(self):
        self.canvas.clear()
        self.info_label.setText("")
        self.time_label.setText("")

    def step_by_step(self, x1, y1, x2, y2):
        """Пошаговый алгоритм"""
        points = []

        if x1 == x2:
            y_start, y_end = min(y1, y2), max(y1, y2)
            for y in range(y_start, y_end + 1):
                points.append((x1, y))
        else:
            m = (y2 - y1) / (x2 - x1)
            b = y1 - m * x1

            if abs(m) <= 1:
                x_start, x_end = min(x1, x2), max(x1, x2)
                for x in range(x_start, x_end + 1):
                    y = m * x + b
                    points.append((x, round(y)))
            else:
                y_start, y_end = min(y1, y2), max(y1, y2)
                for y in range(y_start, y_end + 1):
                    x = (y - b) / m
                    points.append((round(x), y))

        return points

    def dda(self, x1, y1, x2, y2):
        """Цифровой дифференциальный анализатор (ЦДА)"""
        points = []

        dx = x2 - x1
        dy = y2 - y1
        steps = max(abs(dx), abs(dy))

        if steps == 0:
            return [(x1, y1)]

        x_inc = dx / steps
        y_inc = dy / steps

        x, y = x1, y1
        for _ in range(steps + 1):
            points.append((round(x), round(y)))
            x += x_inc
            y += y_inc

        return points

    def bresenham_line(self, x1, y1, x2, y2):
        """Алгоритм Брезенхема для отрезка"""
        points = []

        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1

        x, y = x1, y1

        if dx > dy:
            err = dx / 2
            while x != x2:
                points.append((x, y))
                err -= dy
                if err < 0:
                    y += sy
                    err += dx
                x += sx
        else:
            err = dy / 2
            while y != y2:
                points.append((x, y))
                err -= dx
                if err < 0:
                    x += sx
                    err += dy
                y += sy

        points.append((x, y))
        return points

    def bresenham_circle(self, cx, cy, r):
        """Алгоритм Брезенхема для окружности"""
        points = []
        x = 0
        y = r
        d = 3 - 2 * r

        while x <= y:
            for dx, dy in [(x, y), (y, x), (-x, y), (-y, x),
                           (x, -y), (y, -x), (-x, -y), (-y, -x)]:
                points.append((cx + dx, cy + dy))

            if d < 0:
                d = d + 4 * x + 6
            else:
                d = d + 4 * (x - y) + 10
                y -= 1
            x += 1

        return points

    def castle_pitway(self, cx, cy, rx, ry):
        """Алгоритм Кастла-Питвея для эллипса"""
        points = []
        x = 0
        y = ry

        d1 = (ry * ry) - (rx * rx * ry) + (0.25 * rx * rx)
        dx = 2 * ry * ry * x
        dy = 2 * rx * rx * y

        while dx < dy:
            for px, py in [(x, y), (-x, y), (x, -y), (-x, -y)]:
                points.append((cx + px, cy + py))

            if d1 < 0:
                x += 1
                dx += 2 * ry * ry
                d1 += dx + (ry * ry)
            else:
                x += 1
                y -= 1
                dx += 2 * ry * ry
                dy -= 2 * rx * rx
                d1 += dx - dy + (ry * ry)

        d2 = ((ry * ry) * ((x + 0.5) * (x + 0.5))) + \
             ((rx * rx) * ((y - 1) * (y - 1))) - \
             (rx * rx * ry * ry)

        while y >= 0:
            for px, py in [(x, y), (-x, y), (x, -y), (-x, -y)]:
                points.append((cx + px, cy + py))

            if d2 > 0:
                y -= 1
                dy -= 2 * rx * rx
                d2 += (rx * rx) - dy
            else:
                y -= 1
                x += 1
                dx += 2 * ry * ry
                dy -= 2 * rx * rx
                d2 += dx - dy + (rx * rx)

        return points

    def wu_line(self, x1, y1, x2, y2):
        """Алгоритм Ву для сглаживания"""
        points = []

        def plot(x, y, c):
            points.append((x, y))

        dx = x2 - x1
        dy = y2 - y1

        if abs(dx) > abs(dy):
            if x2 < x1:
                x1, x2 = x2, x1
                y1, y2 = y2, y1

            gradient = dy / dx if dx != 0 else 1
            y = y1 + gradient

            for x in range(x1 + 1, x2):
                plot(x, int(y), 1 - (y - int(y)))
                plot(x, int(y) + 1, y - int(y))
                y += gradient
        else:
            if y2 < y1:
                x1, x2 = x2, x1
                y1, y2 = y2, y1

            gradient = dx / dy if dy != 0 else 1
            x = x1 + gradient

            for y in range(y1 + 1, y2):
                plot(int(x), y, 1 - (x - int(x)))
                plot(int(x) + 1, y, x - int(x))
                x += gradient

        return points

    def get_step_calculations(self, x1, y1, x2, y2):
        calculations = f"""
Пошаговый алгоритм:
Начальная точка: ({x1}, {y1})
Конечная точка: ({x2}, {y2})

Вычисления:
1. dx = {x2} - {x1} = {x2 - x1}
2. dy = {y2} - {y1} = {y2 - y1}
"""
        if x1 != x2:
            m = (y2 - y1) / (x2 - x1)
            b = y1 - m * x1
            calculations += f"""
3. Угловой коэффициент m = dy/dx = {y2 - y1}/{x2 - x1} = {m:.2f}
4. Свободный член b = y1 - m*x1 = {y1} - {m:.2f}*{x1} = {b:.2f}
5. Уравнение прямой: y = {m:.2f}x + {b:.2f}
"""
            if abs(m) <= 1:
                calculations += f"""
Для |m| <= 1 используем итерацию по x:
x от {min(x1, x2)} до {max(x1, x2)}
y = m*x + b, округляем до ближайшего целого
"""
            else:
                calculations += f"""
Для |m| > 1 используем итерацию по y:
y от {min(y1, y2)} до {max(y1, y2)}
x = (y - b)/m, округляем до ближайшего целого
"""
        return calculations

    def get_dda_calculations(self, x1, y1, x2, y2):
        dx = x2 - x1
        dy = y2 - y1
        steps = max(abs(dx), abs(dy))

        calculations = f"""
Алгоритм ЦДА (Digital Differential Analyzer):
Начальная точка: ({x1}, {y1})
Конечная точка: ({x2}, {y2})

Вычисления:
1. dx = {x2} - {x1} = {dx}
2. dy = {y2} - {y1} = {dy}
3. steps = max(|dx|, |dy|) = max({abs(dx)}, {abs(dy)}) = {steps}
"""
        if steps > 0:
            x_inc = dx / steps
            y_inc = dy / steps
            calculations += f"""
4. x_increment = dx/steps = {dx}/{steps} = {x_inc:.3f}
5. y_increment = dy/steps = {dy}/{steps} = {y_inc:.3f}

Итерационный процесс:
x = x + x_increment
y = y + y_increment
Округляем до ближайшего целого на каждом шаге
"""
        return calculations

    def get_bresenham_line_calculations(self, x1, y1, x2, y2):
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1

        calculations = f"""
Алгоритм Брезенхема (отрезок):
Начальная точка: ({x1}, {y1})
Конечная точка: ({x2}, {y2})

Вычисления:
1. dx = |{x2} - {x1}| = {dx}
2. dy = |{y2} - {y1}| = {dy}
3. sx = {'1' if sx > 0 else '-1'} (направление по X)
4. sy = {'1' if sy > 0 else '-1'} (направление по Y)
"""
        if dx > dy:
            err = dx / 2
            calculations += f"""
5. Основная ошибка (err) = dx/2 = {dx}/2 = {err}
6. Т.к. dx > dy, основной цикл по X
7. На каждом шаге:
   - err = err - dy
   - Если err < 0: y = y + sy, err = err + dx
   - x = x + sx
"""
        else:
            err = dy / 2
            calculations += f"""
5. Основная ошибка (err) = dy/2 = {dy}/2 = {err}
6. Т.к. dy >= dx, основной цикл по Y
7. На каждом шаге:
   - err = err - dx
   - Если err < 0: x = x + sx, err = err + dy
   - y = y + sy
"""
        return calculations

    def get_circle_calculations(self, cx, cy, r):
        calculations = f"""
Алгоритм Брезенхема (окружность):
Центр: ({cx}, {cy})
Радиус: {r}

Вычисления:
1. Начальные значения:
   x = 0
   y = {r}
   d = 3 - 2*r = 3 - 2*{r} = {3 - 2 * r}

2. Основной цикл (x <= y):
   - Рисуем 8 симметричных точек
   - Если d < 0:
       d = d + 4*x + 6
     Иначе:
       d = d + 4*(x - y) + 10
       y = y - 1
   - x = x + 1

3. Алгоритм использует только целочисленные операции
"""
        return calculations

class CanvasWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.points = []
        self.show_grid = True
        self.show_axes = True
        self.show_coords = True
        self.scale = 20
        self.offset = QPoint(self.width() // 2, self.height() // 2)

    def clear(self):
        self.points = []
        self.update()

    def set_points(self, points):
        self.points = points
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.fillRect(self.rect(), QColor(255, 255, 255))

        if self.show_grid:
            painter.setPen(QPen(QColor(230, 230, 230), 1))
            center_x = self.width() // 2
            center_y = self.height() // 2

            x = center_x % self.scale
            while x < self.width():
                painter.drawLine(x, 0, x, self.height())
                x += self.scale

            y = center_y % self.scale
            while y < self.height():
                painter.drawLine(0, y, self.width(), y)
                y += self.scale

        if self.show_axes:
            painter.setPen(QPen(QColor(0, 0, 0), 2))
            center_x = self.width() // 2
            center_y = self.height() // 2

            painter.drawLine(0, center_y, self.width(), center_y)
            painter.drawLine(center_x, 0, center_x, self.height())

            painter.drawLine(self.width() - 10, center_y - 5,
                             self.width(), center_y)
            painter.drawLine(self.width() - 10, center_y + 5,
                             self.width(), center_y)
            painter.drawLine(center_x - 5, 10,
                             center_x, 0)
            painter.drawLine(center_x + 5, 10,
                             center_x, 0)

            painter.setFont(QFont("Arial", 10))
            painter.drawText(self.width() - 20, center_y - 10, "X")
            painter.drawText(center_x + 10, 20, "Y")

            if self.show_coords:
                for i in range(-10, 11):
                    if i != 0:
                        x = center_x + i * self.scale
                        painter.drawText(x - 10, center_y + 20, str(i))
                        painter.drawLine(x, center_y - 5, x, center_y + 5)

                for i in range(-10, 11):
                    if i != 0:
                        y = center_y - i * self.scale
                        painter.drawText(center_x + 10, y + 5, str(i))
                        painter.drawLine(center_x - 5, y, center_x + 5, y)

                painter.drawText(center_x + 10, center_y + 20, "0")

        if self.points:
            center_x = self.width() // 2
            center_y = self.height() // 2

            painter.setPen(QPen(QColor(255, 0, 0), 2))
            painter.setBrush(QBrush(QColor(255, 0, 0)))

            for x, y in self.points:
                screen_x = center_x + x * self.scale
                screen_y = center_y - y * self.scale

                painter.drawRect(int(screen_x) - self.scale // 2 + 1,
                                 int(screen_y) - self.scale // 2 + 1,
                                 self.scale - 2, self.scale - 2)

                painter.drawEllipse(int(screen_x) - 2, int(screen_y) - 2, 4, 4)

    def wheelEvent(self, event):
        """Масштабирование колесиком мыши"""
        delta = event.angleDelta().y()
        if delta > 0:
            self.scale = min(self.scale + 2, 100)
        else:
            self.scale = max(self.scale - 2, 5)
        self.update()

    def resizeEvent(self, event):
        self.offset = QPoint(self.width() // 2, self.height() // 2)
        super().resizeEvent(event)

def main():
    app = QApplication(sys.argv)
    window = RasterizationApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()