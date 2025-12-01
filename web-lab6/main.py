import sys
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

class Letter3D:
    """Класс для хранения 3D модели буквы"""

    def __init__(self, letter='А'):
        self.vertices = []
        self.edges = []
        self.color = (0.0, 0.7, 1.0)
        self.transform_matrix = np.identity(4)

        if letter.upper() in ['А', 'A']:
            self.vertices = np.array([
                [0.0, 0.0, 0.0],
                [0.0, 2.0, 0.0],
                [1.0, 2.0, 0.0],
                [1.5, 1.0, 0.0],
                [-0.5, 1.0, 0.0],
                [0.5, 1.0, 0.0],
                [1.0, 1.0, 0.0],
                [0.0, 0.0, 1.0],
                [0.0, 2.0, 1.0],
                [1.0, 2.0, 1.0],
                [1.5, 1.0, 1.0],
                [-0.5, 1.0, 1.0],
                [0.5, 1.0, 1.0],
                [1.0, 1.0, 1.0],
            ])

            self.edges = [
                (0, 1), (1, 2), (2, 3), (3, 0),
                (4, 5), (5, 6), (6, 0),
                (7, 8), (8, 9), (9, 10), (10, 7),
                (11, 12), (12, 13), (13, 7),
                (0, 7), (1, 8), (2, 9), (3, 10),
                (4, 11), (5, 12), (6, 13)
            ]

    def apply_transform(self, matrix):
        """Применить матрицу преобразования"""
        self.transform_matrix = matrix @ self.transform_matrix

    def get_transformed_vertices(self):
        """Получить преобразованные вершины"""
        transformed = []
        for v in self.vertices:
            v_hom = np.append(v, 1.0)
            v_transformed = self.transform_matrix @ v_hom
            transformed.append(v_transformed[:3])
        return np.array(transformed)


class GLWidget(QOpenGLWidget):
    """Виджет OpenGL для 3D отображения"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.letter = Letter3D()
        self.xRot = 0
        self.yRot = 0
        self.zRot = 0
        self.zoom = -10
        self.show_axes = True
        self.projection_type = 'perspective'

    def initializeGL(self):
        """Инициализация OpenGL"""
        glClearColor(0.1, 0.1, 0.15, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LINE_SMOOTH)
        glLineWidth(2.0)

    def paintGL(self):
        """Отрисовка сцены"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        if self.projection_type == 'perspective':
            gluPerspective(45, self.width() / self.height(), 0.1, 100.0)
        else:
            size = 5
            glOrtho(-size, size, -size, size, -100, 100)

        gluLookAt(0, 0, self.zoom, 0, 0, 0, 0, 1, 0)

        glRotatef(self.xRot, 1.0, 0.0, 0.0)
        glRotatef(self.yRot, 0.0, 1.0, 0.0)
        glRotatef(self.zRot, 0.0, 0.0, 1.0)

        if self.show_axes:
            self.draw_axes()

        self.draw_letter()

    def draw_axes(self):
        """Рисование осей координат"""
        glBegin(GL_LINES)

        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(3.0, 0.0, 0.0)

        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, 3.0, 0.0)

        glColor3f(0.0, 0.5, 1.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, 0.0, 3.0)

        glEnd()

    def draw_letter(self):
        """Отрисовка 3D буквы"""
        vertices = self.letter.get_transformed_vertices()

        glColor3f(*self.letter.color)
        glBegin(GL_LINES)

        for edge in self.letter.edges:
            for vertex in edge:
                glVertex3fv(vertices[vertex])

        glEnd()

    def resizeGL(self, w, h):
        """Обработка изменения размера"""
        glViewport(0, 0, w, h)

    def mousePressEvent(self, event):
        """Обработка нажатия мыши"""
        self.lastPos = event.pos()

    def mouseMoveEvent(self, event):
        """Обработка движения мыши для вращения"""
        dx = event.x() - self.lastPos.x()
        dy = event.y() - self.lastPos.y()

        if event.buttons() & Qt.LeftButton:
            self.xRot += dy
            self.yRot += dx
        elif event.buttons() & Qt.RightButton:
            self.zRot += dx

        self.lastPos = event.pos()
        self.update()

    def wheelEvent(self, event):
        """Обработка колесика мыши для масштабирования"""
        self.zoom += event.angleDelta().y() * 0.01
        self.update()


class ProjectionWidget(QWidget):
    """Виджет для ортографических проекций"""

    def __init__(self, letter, projection='xy', parent=None):
        super().__init__(parent)
        self.letter = letter
        self.projection = projection
        self.setMinimumSize(200, 200)

    def paintEvent(self, event):
        """Отрисовка проекции"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.fillRect(self.rect(), QColor(30, 30, 40))

        center = self.rect().center()

        scale = 30

        painter.setPen(QPen(Qt.white, 1))
        painter.drawLine(center.x(), 0, center.x(), self.height())
        painter.drawLine(0, center.y(), self.width(), center.y())

        painter.setPen(QPen(Qt.white, 1))
        font = painter.font()
        font.setPointSize(8)
        painter.setFont(font)

        if self.projection == 'xy':
            painter.drawText(center.x() + 10, 20, "Y")
            painter.drawText(self.width() - 20, center.y() - 10, "X")
        elif self.projection == 'xz':
            painter.drawText(center.x() + 10, 20, "Z")
            painter.drawText(self.width() - 20, center.y() - 10, "X")
        else:
            painter.drawText(center.x() + 10, 20, "Z")
            painter.drawText(20, center.y() - 10, "Y")

        painter.drawText(10, 20, self.projection.upper())

        vertices = self.letter.get_transformed_vertices()

        painter.setPen(QPen(QColor(0, 180, 255), 2))

        for edge in self.letter.edges:
            points = []
            for vertex in edge:
                v = vertices[vertex]

                if self.projection == 'xy':
                    x = v[0] * scale + center.x()
                    y = -v[1] * scale + center.y()
                elif self.projection == 'xz':
                    x = v[0] * scale + center.x()
                    y = -v[2] * scale + center.y()
                else:
                    x = v[1] * scale + center.x()
                    y = -v[2] * scale + center.y()

                points.append(QPointF(x, y))

            if len(points) == 2:
                painter.drawLine(points[0], points[1])


class MainWindow(QMainWindow):
    """Главное окно приложения"""

    def __init__(self):
        super().__init__()
        self.letter = Letter3D()
        self.transform_matrix = np.identity(4)
        self.initUI()

    def initUI(self):
        """Инициализация интерфейса"""
        self.setWindowTitle('3D Визуализация Буквы - Лабораторные работы 6а-6с')
        self.setGeometry(100, 100, 1400, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        left_panel = QVBoxLayout()

        self.gl_widget = GLWidget()
        self.gl_widget.letter = self.letter
        left_panel.addWidget(self.gl_widget)

        control_3d = QGroupBox("Управление 3D видом")
        control_3d_layout = QHBoxLayout()

        self.axes_check = QCheckBox("Показать оси")
        self.axes_check.setChecked(True)
        self.axes_check.stateChanged.connect(self.toggle_axes)

        self.projection_combo = QComboBox()
        self.projection_combo.addItems(["Перспектива", "Ортографическая"])
        self.projection_combo.currentIndexChanged.connect(self.change_projection)

        control_3d_layout.addWidget(self.axes_check)
        control_3d_layout.addWidget(QLabel("Проекция:"))
        control_3d_layout.addWidget(self.projection_combo)
        control_3d_layout.addStretch()

        control_3d.setLayout(control_3d_layout)
        left_panel.addWidget(control_3d)

        main_layout.addLayout(left_panel, 70)

        right_panel = QVBoxLayout()

        transform_group = QGroupBox("Трехмерные преобразования")
        transform_layout = QGridLayout()

        transform_layout.addWidget(QLabel("Масштабирование:"), 0, 0)
        self.scale_x = QDoubleSpinBox()
        self.scale_x.setRange(0.1, 5.0)
        self.scale_x.setValue(1.0)
        self.scale_x.setSingleStep(0.1)
        transform_layout.addWidget(QLabel("X:"), 0, 1)
        transform_layout.addWidget(self.scale_x, 0, 2)

        self.scale_y = QDoubleSpinBox()
        self.scale_y.setRange(0.1, 5.0)
        self.scale_y.setValue(1.0)
        self.scale_y.setSingleStep(0.1)
        transform_layout.addWidget(QLabel("Y:"), 0, 3)
        transform_layout.addWidget(self.scale_y, 0, 4)

        self.scale_z = QDoubleSpinBox()
        self.scale_z.setRange(0.1, 5.0)
        self.scale_z.setValue(1.0)
        self.scale_z.setSingleStep(0.1)
        transform_layout.addWidget(QLabel("Z:"), 0, 5)
        transform_layout.addWidget(self.scale_z, 0, 6)

        transform_layout.addWidget(QLabel("Перенос:"), 1, 0)
        self.translate_x = QDoubleSpinBox()
        self.translate_x.setRange(-5.0, 5.0)
        self.translate_x.setValue(0.0)
        self.translate_x.setSingleStep(0.1)
        transform_layout.addWidget(QLabel("X:"), 1, 1)
        transform_layout.addWidget(self.translate_x, 1, 2)

        self.translate_y = QDoubleSpinBox()
        self.translate_y.setRange(-5.0, 5.0)
        self.translate_y.setValue(0.0)
        self.translate_y.setSingleStep(0.1)
        transform_layout.addWidget(QLabel("Y:"), 1, 3)
        transform_layout.addWidget(self.translate_y, 1, 4)

        self.translate_z = QDoubleSpinBox()
        self.translate_z.setRange(-5.0, 5.0)
        self.translate_z.setValue(0.0)
        self.translate_z.setSingleStep(0.1)
        transform_layout.addWidget(QLabel("Z:"), 1, 5)
        transform_layout.addWidget(self.translate_z, 1, 6)

        transform_layout.addWidget(QLabel("Вращение (градусы):"), 2, 0)
        self.rotate_x = QDoubleSpinBox()
        self.rotate_x.setRange(-180.0, 180.0)
        self.rotate_x.setValue(0.0)
        transform_layout.addWidget(QLabel("X:"), 2, 1)
        transform_layout.addWidget(self.rotate_x, 2, 2)

        self.rotate_y = QDoubleSpinBox()
        self.rotate_y.setRange(-180.0, 180.0)
        self.rotate_y.setValue(0.0)
        transform_layout.addWidget(QLabel("Y:"), 2, 3)
        transform_layout.addWidget(self.rotate_y, 2, 4)

        self.rotate_z = QDoubleSpinBox()
        self.rotate_z.setRange(-180.0, 180.0)
        self.rotate_z.setValue(0.0)
        transform_layout.addWidget(QLabel("Z:"), 2, 5)
        transform_layout.addWidget(self.rotate_z, 2, 6)

        self.apply_btn = QPushButton("Применить преобразования")
        self.apply_btn.clicked.connect(self.apply_transforms)
        transform_layout.addWidget(self.apply_btn, 3, 0, 1, 4)

        self.reset_btn = QPushButton("Сбросить")
        self.reset_btn.clicked.connect(self.reset_transforms)
        transform_layout.addWidget(self.reset_btn, 3, 4, 1, 3)

        transform_group.setLayout(transform_layout)
        right_panel.addWidget(transform_group)

        matrix_group = QGroupBox("Матрица преобразования")
        matrix_layout = QVBoxLayout()

        self.matrix_text = QTextEdit()
        self.matrix_text.setMaximumHeight(150)
        self.matrix_text.setReadOnly(True)
        self.matrix_text.setFont(QFont("Courier", 9))
        self.update_matrix_display()

        matrix_layout.addWidget(self.matrix_text)
        matrix_group.setLayout(matrix_layout)
        right_panel.addWidget(matrix_group)

        projections_group = QGroupBox("Ортографические проекции")
        projections_layout = QHBoxLayout()

        self.proj_xy = ProjectionWidget(self.letter, 'xy')
        self.proj_xz = ProjectionWidget(self.letter, 'xz')
        self.proj_yz = ProjectionWidget(self.letter, 'yz')

        projections_layout.addWidget(self.proj_xy)
        projections_layout.addWidget(self.proj_xz)
        projections_layout.addWidget(self.proj_yz)

        projections_group.setLayout(projections_layout)
        right_panel.addWidget(projections_group)

        main_layout.addLayout(right_panel, 30)

    def toggle_axes(self, state):
        """Переключение отображения осей"""
        self.gl_widget.show_axes = (state == Qt.Checked)
        self.gl_widget.update()

    def change_projection(self, index):
        """Изменение типа проекции"""
        self.gl_widget.projection_type = 'perspective' if index == 0 else 'ortho'
        self.gl_widget.update()

    def apply_transforms(self):
        """Применение преобразований"""
        scale_mat = np.array([
            [self.scale_x.value(), 0, 0, 0],
            [0, self.scale_y.value(), 0, 0],
            [0, 0, self.scale_z.value(), 0],
            [0, 0, 0, 1]
        ])

        translate_mat = np.array([
            [1, 0, 0, self.translate_x.value()],
            [0, 1, 0, self.translate_y.value()],
            [0, 0, 1, self.translate_z.value()],
            [0, 0, 0, 1]
        ])

        rx = np.radians(self.rotate_x.value())
        ry = np.radians(self.rotate_y.value())
        rz = np.radians(self.rotate_z.value())

        rotate_x_mat = np.array([
            [1, 0, 0, 0],
            [0, np.cos(rx), -np.sin(rx), 0],
            [0, np.sin(rx), np.cos(rx), 0],
            [0, 0, 0, 1]
        ])

        rotate_y_mat = np.array([
            [np.cos(ry), 0, np.sin(ry), 0],
            [0, 1, 0, 0],
            [-np.sin(ry), 0, np.cos(ry), 0],
            [0, 0, 0, 1]
        ])

        rotate_z_mat = np.array([
            [np.cos(rz), -np.sin(rz), 0, 0],
            [np.sin(rz), np.cos(rz), 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])

        transform_mat = translate_mat @ rotate_z_mat @ rotate_y_mat @ rotate_x_mat @ scale_mat

        self.letter.apply_transform(transform_mat)

        self.transform_matrix = transform_mat @ self.transform_matrix
        self.update_matrix_display()

        self.gl_widget.update()
        self.proj_xy.update()
        self.proj_xz.update()
        self.proj_yz.update()

    def reset_transforms(self):
        """Сброс преобразований"""
        self.letter.transform_matrix = np.identity(4)
        self.transform_matrix = np.identity(4)

        self.scale_x.setValue(1.0)
        self.scale_y.setValue(1.0)
        self.scale_z.setValue(1.0)

        self.translate_x.setValue(0.0)
        self.translate_y.setValue(0.0)
        self.translate_z.setValue(0.0)

        self.rotate_x.setValue(0.0)
        self.rotate_y.setValue(0.0)
        self.rotate_z.setValue(0.0)

        self.update_matrix_display()

        self.gl_widget.update()
        self.proj_xy.update()
        self.proj_xz.update()
        self.proj_yz.update()

    def update_matrix_display(self):
        """Обновление отображения матрицы преобразования"""
        text = ""
        for i in range(4):
            row = self.transform_matrix[i]
            text += f"[{row[0]:8.3f} {row[1]:8.3f} {row[2]:8.3f} {row[3]:8.3f}]\n"
        self.matrix_text.setText(text)

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(dark_palette)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()