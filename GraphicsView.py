from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from qimage2ndarray import array2qimage
import numpy as np


class GraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super(GraphicsView, self).__init__(parent)
        self.graphics_scene = QGraphicsScene()
        self.pixmap_item = QGraphicsPixmapItem()
        self.graphics_scene.addItem(self.pixmap_item)
        self.setScene(self.graphics_scene)
        self.image = None
        self.window_center = 0
        self.window_width = 0
        self.window_min = 0
        self.window_max = 0
        self.set_HU_range(-1000, 3096)

    def set_image(self, image, update=True):
        self.image = np.copy(image)
        image_min = self.image.min()
        image_max = self.image.max()
        if image_min < 0:
            self.image += abs(image_min)
        self.image_range = self.image.max() - image_min
        #self.window_min, self.window_max = image_min, image_max
        if update:
            self.update()

    def update(self):
        image = np.copy(self.image)
        image = np.interp(image, (self.window_min, self.window_max), (0, 255)).astype(np.uint8)
        self.pixmap_item = QGraphicsPixmapItem(QPixmap(array2qimage(np.copy(image))))
        self.graphics_scene.removeItem(self.graphics_scene.items()[0])
        self.graphics_scene.addItem(self.pixmap_item)

    def mouseMoveEvent(self, event):
        pos = event.pos()
        x, y = pos.x(), pos.y()
        x_max, y_max = self.width(), self.height()
        #self.window_center = self.image_range * y / y_max
        self.window_center = self.image.max() * y / y_max
        self.window_width = self.image.max() * x / x_max
        half_window_width = self.window_width * 0.5
        self.window_min = self.window_center - half_window_width
        self.window_max = self.window_center + half_window_width
        self.update()

    def set_HU_range(self, HU_min, HU_max):
        self.HU_min, self.HU_max = HU_min, HU_max
        self.HU_range = self.HU_max - self.HU_min

    def resizeEvent(self, event):
        self.fitInView(self.pixmap_item.boundingRect(), Qt.KeepAspectRatio)
