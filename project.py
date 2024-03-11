import sys

from PyQt6 import uic
from PyQt6.QtGui import QPixmap, QKeyEvent
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QLabel, QPushButton
from PyQt6.QtCore import Qt

from map_image import MapImage, MapType


class Project(QMainWindow):
    SCALE_COEFF = 2

    def __init__(self):
        super().__init__()
        uic.loadUi('forms/mainWindow.ui', self)
        self._map = MapImage()
        self.updateImage()

        self.radios.buttonClicked.connect(self.select_layer)
        self.search.clicked.connect(self.search_what)
        self.drop.clicked.connect(self.drop_search_marks)

    def drop_search_marks(self):
        self._map.drop_marks()
        self.updateImage()

    def search_what(self):
        self._map.change_position(self.search_line.text())
        self.updateImage()

    def select_layer(self):
        match self.radios.checkedButton():
            case self.radio_sh:
                self._map.set_type(MapType.SCHEMA)
            case self.radio_sp:
                self._map.set_type(MapType.SATELLITE)
            case self.radio_gi:
                self._map.set_type(MapType.HYBRID)
        self.updateImage()

    def updateImage(self):
        pixmap = QPixmap()
        image = self._map.image
        if image is None:
            QMessageBox(QMessageBox.Icon.Warning, 'Ошибка', 'Не удалось загрузить карту',
                        QMessageBox.StandardButton.NoButton, self).show()
        else:
            pixmap.loadFromData(image)
        self.image.setPixmap(pixmap)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        match event.key():
            case Qt.Key.Key_PageUp:
                self._map.scaling(1 / self.SCALE_COEFF)
            case Qt.Key.Key_PageDown:
                self._map.scaling(self.SCALE_COEFF)
            case Qt.Key.Key_Up:
                self._map.screen_up()
            case Qt.Key.Key_Down:
                self._map.screen_down()
            case Qt.Key.Key_Left:
                self._map.screen_left()
            case Qt.Key.Key_Right:
                self._map.screen_right()
        if event.key() in (Qt.Key.Key_PageUp, Qt.Key.Key_PageDown, Qt.Key.Key_Up, Qt.Key.Key_Down, Qt.Key.Key_Left, Qt.Key.Key_Right):
            self.updateImage()


def exception_hook(exctype, value, traceback):
    sys._excepthook(exctype, value, traceback)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Project()
    w.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
