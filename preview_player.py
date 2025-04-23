import sys
import vlc
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, QLabel
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QKeySequence

class VideoPreview(QWidget):
    def __init__(self, video_path):
        super().__init__()
        self.setWindowTitle("Video Preview")
        # self.setStyleSheet("background-color: black;")
        self.setGeometry(200, 200, 500, 400)

        self.videoframe = QtWidgets.QFrame(self)
        self.videoframe.setStyleSheet("background-color: black;")

        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.toggle_play)
        # self.play_button.setStyleSheet("margin-right: 10px;")
        self.play_button.setFixedWidth(80)
         
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.setStyleSheet("margin: 10px;")
        self.slider.sliderMoved.connect(self.set_position)

        self.time_label = QLabel("00:00 / 00:00")
        # # self.time_label.setStyleSheet("color: white;")
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setFixedHeight(20) #Added fixed height.

        controls_layout = QHBoxLayout()
        controls_layout.addWidget(self.play_button)
        controls_layout.addWidget(self.slider)


        layout = QVBoxLayout()
        layout.addWidget(self.videoframe)
        layout.addWidget(self.time_label)
        layout.addLayout(controls_layout)
        layout.setSpacing(0) #Remove spacing
        layout.setContentsMargins(0,0,0,0) #Remove margins
        self.setLayout(layout)

        self.instance = vlc.Instance("--quiet") # or --verbose=-1
        self.media_player = self.instance.media_player_new()
        self.media = self.instance.media_new(video_path)
        self.media_player.set_media(self.media)

        # Embed video output (macOS compatible)
        if sys.platform.startswith("linux"):
            self.media_player.set_xwindow(self.videoframe.winId())
        elif sys.platform == "win32":
            self.media_player.set_hwnd(self.videoframe.winId())
        elif sys.platform == "darwin":
            self.media_player.set_nsobject(int(self.videoframe.winId()))

        self.media_player.play()
        self.playing = True
        self.play_button.setText("Pause")

        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_slider)
        self.timer.start()

        self.show()

    def toggle_play(self):
        if self.playing:
            self.media_player.pause()
            self.playing = False
            self.play_button.setText("Play")
        else:
            self.media_player.play()
            self.playing = True
            self.play_button.setText("Pause")

    def set_position(self, position):
        if self.media_player.is_playing() or not self.playing:
            if self.media_player.get_length() > 0:
                percentage = position / self.media_player.get_length()
                self.media_player.set_position(percentage)

    def update_slider(self):
        media_length = self.media_player.get_length()
        if media_length > 0:
            self.slider.setRange(0, media_length)
            position = self.media_player.get_time()
            self.slider.setValue(position)
            self.update_time_label(position, media_length)

    def update_time_label(self, current_time, total_time):
        current_minutes, current_seconds = divmod(current_time // 1000, 60)
        total_minutes, total_seconds = divmod(total_time // 1000, 60)
        time_str = "{:02d}:{:02d} / {:02d}:{:02d}".format(current_minutes, current_seconds, total_minutes, total_seconds)
        self.time_label.setText(time_str)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Left:
            current_time = self.media_player.get_time()
            new_time = max(0, current_time - 10000)
            self.media_player.set_time(new_time)
        elif event.key() == Qt.Key_Right:
            current_time = self.media_player.get_time()
            new_time = current_time + 10000
            self.media_player.set_time(new_time)
        elif event.key() == Qt.Key_W and event.modifiers() == Qt.MetaModifier:
            self.close()  # Close the dialog on CMD-W
        elif event.key() == Qt.Key_Q and event.modifiers() == Qt.MetaModifier:
            self.close()  # Close the dialog on CMD-Q
        else:
            super().keyPressEvent(event)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python preview_player.py /path/to/video.mp4")
        sys.exit(1)
    video_path = sys.argv[1]
    app = QtWidgets.QApplication(sys.argv)
    player = VideoPreview(video_path)
    sys.exit(app.exec_())