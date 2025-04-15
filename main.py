import sys
import qrcode
from PIL import Image, ImageDraw, ImageOps
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QLineEdit, QPushButton,
                             QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, QMessageBox,
                             QColorDialog, QSpinBox, QComboBox, QGroupBox, QCheckBox,
                             QFrame, QSizePolicy)
from PyQt5.QtGui import QPixmap, QColor, QImage, QFont, QIcon
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve


class QRGeneratorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Генератор QR-кодов Premium")
        self.setFixedSize(650, 800)
        self.setWindowIcon(QIcon(":qrcode.png"))  # Можно добавить иконку

        # Стилизация
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f7fa;
            }
            QLineEdit, QSpinBox, QComboBox {
                border: 1px solid #d1d5db;
                border-radius: 5px;
                padding: 8px;
                background: white;
            }
            QPushButton {
                background-color: #4f46e5;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4338ca;
            }
            QPushButton:disabled {
                background-color: #9ca3af;
            }
            QGroupBox {
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }
            QLabel {
                color: #374151;
            }
            QCheckBox {
                spacing: 5px;
            }
        """)

        # Основные виджеты
        self.create_input_section()
        self.create_appearance_section()
        self.create_logo_section()
        self.create_preview_section()
        self.create_action_buttons()

        # Разметка
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.input_group)
        main_layout.addWidget(self.appearance_group)
        main_layout.addWidget(self.logo_group)
        main_layout.addSpacing(10)
        main_layout.addWidget(self.qr_preview_frame, 0, Qt.AlignCenter)
        main_layout.addWidget(self.buttons_frame)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Обработчики событий
        self.connect_signals()

    def create_input_section(self):
        self.input_group = QGroupBox("Данные для QR-кода")

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("https://example.com или любой текст")
        self.input_field.setClearButtonEnabled(True)

        layout = QVBoxLayout()
        layout.addWidget(self.input_field)
        self.input_group.setLayout(layout)

    def create_appearance_section(self):
        self.appearance_group = QGroupBox("Настройки внешнего вида")

        # Цвет
        self.color_btn = QPushButton("Выбрать цвет")
        self.color_preview = QLabel()
        self.color_preview.setFixedSize(30, 30)
        self.color_preview.setStyleSheet("background-color: #000000; border-radius: 15px; border: 1px solid #d1d5db;")
        self.selected_color = "#000000"

        # Размер
        self.size_spinbox = QSpinBox()
        self.size_spinbox.setRange(100, 1000)
        self.size_spinbox.setValue(300)

        # Формат
        self.format_combobox = QComboBox()
        self.format_combobox.addItems(["PNG", "JPEG", "SVG"])

        # Расположение элементов
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Цвет QR-кода:"))
        color_layout.addWidget(self.color_btn)
        color_layout.addWidget(self.color_preview)
        color_layout.addStretch()

        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Размер (px):"))
        size_layout.addWidget(self.size_spinbox)
        size_layout.addStretch()

        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Формат сохранения:"))
        format_layout.addWidget(self.format_combobox)
        format_layout.addStretch()

        layout = QVBoxLayout()
        layout.addLayout(color_layout)
        layout.addLayout(size_layout)
        layout.addLayout(format_layout)
        self.appearance_group.setLayout(layout)

    def create_logo_section(self):
        self.logo_group = QGroupBox("Логотип")

        self.logo_checkbox = QCheckBox("Добавить логотип")
        self.logo_checkbox.setChecked(False)

        self.logo_path_label = QLabel("Файл не выбран")
        self.logo_path_label.setWordWrap(True)
        self.logo_path_label.setStyleSheet("color: #6b7280; font-style: italic;")

        self.logo_btn = QPushButton("Выбрать изображение")
        self.logo_btn.setEnabled(False)

        self.logo_size_spinbox = QSpinBox()
        self.logo_size_spinbox.setRange(10, 50)
        self.logo_size_spinbox.setValue(25)
        self.logo_size_spinbox.setSuffix("%")

        layout = QVBoxLayout()
        layout.addWidget(self.logo_checkbox)

        logo_size_layout = QHBoxLayout()
        logo_size_layout.addWidget(QLabel("Размер логотипа:"))
        logo_size_layout.addWidget(self.logo_size_spinbox)
        logo_size_layout.addStretch()

        layout.addLayout(logo_size_layout)
        layout.addWidget(self.logo_btn)
        layout.addWidget(self.logo_path_label)
        self.logo_group.setLayout(layout)

    def create_preview_section(self):
        self.qr_preview_frame = QFrame()
        self.qr_preview_frame.setFrameShape(QFrame.StyledPanel)
        self.qr_preview_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 10px;
                border: 1px dashed #d1d5db;
            }
        """)
        self.qr_preview_frame.setFixedSize(320, 320)

        self.qr_preview = QLabel()
        self.qr_preview.setAlignment(Qt.AlignCenter)
        self.qr_preview.setText("QR-код появится здесь")
        self.qr_preview.setStyleSheet("""
            QLabel {
                color: #9ca3af;
                font-style: italic;
            }
        """)

        layout = QVBoxLayout()
        layout.addWidget(self.qr_preview)
        self.qr_preview_frame.setLayout(layout)

    def create_action_buttons(self):
        self.buttons_frame = QFrame()

        self.generate_btn = QPushButton("Сгенерировать QR-код")
        self.generate_btn.setIcon(QIcon(":refresh.png"))  # Можно добавить иконку
        self.generate_btn.setFixedHeight(40)

        self.save_btn = QPushButton("Сохранить QR-код")
        self.save_btn.setIcon(QIcon(":save.png"))  # Можно добавить иконку
        self.save_btn.setFixedHeight(40)
        self.save_btn.setEnabled(False)

        layout = QHBoxLayout()
        layout.addWidget(self.generate_btn)
        layout.addWidget(self.save_btn)
        self.buttons_frame.setLayout(layout)

    def connect_signals(self):
        self.color_btn.clicked.connect(self.choose_color)
        self.logo_checkbox.stateChanged.connect(self.toggle_logo_upload)
        self.logo_btn.clicked.connect(self.choose_logo)
        self.generate_btn.clicked.connect(self.generate_qr)
        self.save_btn.clicked.connect(self.save_qr)

    def choose_color(self):
        color = QColorDialog.getColor(QColor(self.selected_color))
        if color.isValid():
            self.selected_color = color.name()
            self.color_preview.setStyleSheet(
                f"background-color: {self.selected_color}; "
                "border-radius: 15px; border: 1px solid #d1d5db;"
            )
            self.animate_color_change()

    def animate_color_change(self):
        animation = QPropertyAnimation(self.color_preview, b"size")
        animation.setDuration(200)
        animation.setStartValue(QSize(25, 25))
        animation.setEndValue(QSize(30, 30))
        animation.setEasingCurve(QEasingCurve.OutBack)
        animation.start()

    def toggle_logo_upload(self, state):
        self.logo_btn.setEnabled(state == Qt.Checked)
        if not state:
            self.logo_path_label.setText("Файл не выбран")
            if hasattr(self, 'logo_path'):
                del self.logo_path

    def choose_logo(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выбрать логотип", "",
            "Изображения (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            self.logo_path = file_path
            self.logo_path_label.setText(file_path.split("/")[-1])
            self.animate_logo_selection()

    def animate_logo_selection(self):
        animation = QPropertyAnimation(self.logo_path_label, b"color")
        animation.setDuration(500)
        animation.setStartValue(QColor("#6b7280"))
        animation.setEndValue(QColor("#1f2937"))
        animation.start()

    def generate_qr(self):
        data = self.input_field.text().strip()
        if not data:
            self.show_error("Ошибка", "Пожалуйста, введите текст или ссылку для QR-кода")
            return

        try:
            # Генерация QR-кода
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)

            img = qr.make_image(fill_color=self.selected_color, back_color="white").convert('RGB')

            # Добавление логотипа
            if self.logo_checkbox.isChecked() and hasattr(self, 'logo_path'):
                self.add_logo_to_qr(img)

            # Масштабирование для превью
            img = img.resize((300, 300), Image.LANCZOS)

            # Отображение превью
            self.display_qr_preview(img)
            self.generated_qr = img
            self.save_btn.setEnabled(True)

            # Анимация успешной генерации
            self.animate_success()

        except Exception as e:
            self.show_error("Ошибка генерации", f"Произошла ошибка: {str(e)}")

    def add_logo_to_qr(self, img):
        try:
            logo = Image.open(self.logo_path)
            qr_size = img.size[0]
            logo_size = int(qr_size * self.logo_size_spinbox.value() / 100)
            logo = logo.resize((logo_size, logo_size), Image.LANCZOS)

            # Создание круглой маски
            mask = Image.new('L', (logo_size, logo_size), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, logo_size, logo_size), fill=255)
            logo = ImageOps.fit(logo, mask.size, centering=(0.5, 0.5))
            logo.putalpha(mask)

            # Вставка логотипа
            pos = ((qr_size - logo_size) // 2, (qr_size - logo_size) // 2)
            img.paste(logo, pos, logo)
        except Exception as e:
            raise Exception(f"Ошибка при добавлении логотипа: {str(e)}")

    def display_qr_preview(self, img):
        qimage = QImage(img.tobytes(), img.size[0], img.size[1], QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)
        self.qr_preview.setPixmap(pixmap)
        self.qr_preview.setText("")

    def animate_success(self):
        animation = QPropertyAnimation(self.qr_preview_frame, b"geometry")
        animation.setDuration(300)
        animation.setStartValue(self.qr_preview_frame.geometry())
        animation.setEndValue(self.qr_preview_frame.geometry().adjusted(-5, -5, 5, 5))
        animation.setEasingCurve(QEasingCurve.InOutQuad)
        animation.start()

    def save_qr(self):
        if not hasattr(self, 'generated_qr'):
            return

        fmt = self.format_combobox.currentText().lower()
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить QR-код",
            f"qr_code.{fmt}",
            f"{fmt.upper()} Images (*.{fmt});;All Files (*)"
        )

        if file_path:
            try:
                self.generated_qr.save(file_path)
                self.show_success("Успех", f"QR-код успешно сохранён как:\n{file_path}")
            except Exception as e:
                self.show_error("Ошибка сохранения", f"Не удалось сохранить файл: {str(e)}")

    def show_error(self, title, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec_()

    def show_success(self, title, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Установка стиля по умолчанию (опционально)
    app.setStyle("Fusion")

    # Настройка шрифта
    font = QFont()
    font.setFamily("Segoe UI")
    font.setPointSize(10)
    app.setFont(font)

    window = QRGeneratorApp()
    window.show()
    sys.exit(app.exec_())