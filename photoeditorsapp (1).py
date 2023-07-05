import sys
import numpy as np
import cv2
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QAction, QFileDialog, QVBoxLayout, QWidget, QPushButton, QGraphicsScene, QGraphicsPixmapItem, QGraphicsDropShadowEffect, QGraphicsBlurEffect
from PyQt5.QtGui import QImage, QPixmap, QPainter, QColor, QKeySequence, QTransform, QBrush, QPen
from PyQt5.QtCore import Qt, QPoint, QSize
from PyQt5.uic import loadUi
from editinga import Ui_Form


class PhotoEditor(QMainWindow, Ui_Form):
    def __init__(self):
        super(PhotoEditor, self).__init__()
        self.setupUi(self)
        self.browser.clicked.connect(self.open_image)
        self.undo.clicked.connect(self.undo_filter)

        # Connect other button signals to their respective functions
        self.rotate.clicked.connect(self.rotate_90)
        self.fliplr.clicked.connect(self.flip_left_right)
        self.greyfilter.clicked.connect(self.apply_grayscale)
        self.blurfilter.clicked.connect(self.apply_blur)
        self.sharpenfilter.clicked.connect(self.apply_sharpen)
        self.flipup.clicked.connect(self.flip_up_down)
        self.cancel.clicked.connect(self.cancel_changes)
        self.save.clicked.connect(self.save_image)

        self.original_image = None
        self.filtered_image = None

    def open_image(self):
        file_dialog = QFileDialog()
        image_path, _ = file_dialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.bmp *.jpeg)")
        if image_path:
            self.original_image = QImage(image_path)
            self.filtered_image = self.original_image.copy()
            self.display_image(self.filtered_image)

    def save_image(self):
        if self.filtered_image:
            file_dialog = QFileDialog()
            image_path, _ = file_dialog.getSaveFileName(self, "Save Image", "", "PNG Image (*.png *.jpg *.jpeg)")
            if image_path:
                self.filtered_image.save(image_path)

    def display_image(self, image):
        if image is None or image.isNull():
            self.clear_layout(self.pic)
            self.pic.addWidget(QtWidgets.QLabel("No Image"))
        else:
            self.clear_layout(self.pic)
            pixmap = QPixmap.fromImage(image)
            label = QtWidgets.QLabel()
            label.setPixmap(pixmap.scaled(400, 300, Qt.KeepAspectRatio))
            self.pic.addWidget(label)

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self.clear_layout(child.layout())


    def apply_grayscale(self):
        if self.original_image:
            self.filtered_image = self.original_image.convertToFormat(QImage.Format_Grayscale16)
            self.display_image(self.filtered_image)

    def rotate_90(self):
        if self.original_image:
            transform = QTransform().rotate(90)
            self.filtered_image = self.filtered_image.transformed(transform)
            self.display_image(self.filtered_image)

    def flip_left_right(self):
        if self.original_image:
            self.filtered_image = self.filtered_image.mirrored(True, False)
            self.display_image(self.filtered_image)


    def flip_up_down(self):
        if self.original_image:
            self.filtered_image = self.filtered_image.mirrored(False, True)
            self.display_image(self.filtered_image)

    def apply_blur(self):
        if self.original_image:
            scene = QGraphicsScene()
            pixmap_item = QGraphicsPixmapItem(QPixmap.fromImage(self.original_image))
            scene.addItem(pixmap_item)

            blur_effect = QGraphicsBlurEffect()
            blur_effect.setBlurRadius(10)  # Adjust the blur radius as needed

            pixmap_item.setGraphicsEffect(blur_effect)

            self.filtered_image = QImage(self.original_image.size(), QImage.Format_ARGB32)
            painter = QPainter(self.filtered_image)
            scene.render(painter)
            painter.end()

            self.display_image(self.filtered_image)

    def apply_sharpen(self):
        if self.original_image:
            image_array = self.qimage_to_ndarray(self.original_image)
            sharpened_image = cv2.filter2D(image_array, -1, self.get_sharpening_kernel())
            self.filtered_image = self.ndarray_to_qimage(sharpened_image)
            self.display_image(self.filtered_image)

    def qimage_to_ndarray(self, image):
        width = image.width()
        height = image.height()
        buffer = image.bits().asstring(width * height * 4)
        return np.frombuffer(buffer, dtype=np.uint8).reshape((height, width, 4))

    def ndarray_to_qimage(self, array):
        height, width, _ = array.shape
        bytes_per_line = 4 * width
        image = QImage(array.data, width, height, bytes_per_line, QImage.Format_ARGB32)
        return image.copy()

    def get_sharpening_kernel(self):
        kernel = np.array([
            [-1, -1, -1],
            [-1,  9, -1],
            [-1, -1, -1]
        ], dtype=np.float32)
        return kernel


    def undo_filter(self):
        if self.original_image:
            self.filtered_image = self.original_image.copy()
            self.display_image(self.filtered_image)

    def cancel_changes(self):
        sys.exit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PhotoEditor()
    window.show()
    sys.exit(app.exec_())
