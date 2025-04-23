import sys
import vlc
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QFileDialog, QPushButton, QVBoxLayout, QWidget


class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VLC Video Player (PyQt5)")
        self.setGeometry(100, 100, 800, 600)

        self.instance = vlc.Instance()
        self.media_player = self.instance.media_player_new()

        self.videoframe = QtWidgets.QFrame(self)
        self.videoframe.setStyleSheet("background-color: black;")

        self.open_button = QPushButton("Open Video")
        self.open_button.clicked.connect(self.open_file)

        layout = QVBoxLayout()
        layout.addWidget(self.videoframe)
        layout.addWidget(self.open_button)
        self.setLayout(layout)

        # Embed VLC video in the widget
        if sys.platform.startswith("linux"):  # Linux
            self.media_player.set_xwindow(self.videoframe.winId())
        elif sys.platform == "win32":  # Windows
            self.media_player.set_hwnd(self.videoframe.winId())
        elif sys.platform == "darwin":  # macOS
            self.media_player.set_nsobject(int(self.videoframe.winId()))

    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Video")
        if filename:
            media = self.instance.media_new(filename)
            self.media_player.set_media(media)
            self.media_player.play()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec_())
