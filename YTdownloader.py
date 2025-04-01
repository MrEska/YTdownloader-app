from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, QMessageBox, QFileDialog, QRadioButton, QProgressBar
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import QThread, pyqtSignal
import yt_dlp
import sys


class DownloadProgress(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, link, dir, res):
        super().__init__()
        self.link = link
        self.dir = dir
        self.res = res

    def run(self):
        try:
            ydl_opts = {
                'format': f'bestvideo[height={self.res}]+bestaudio',
                'outtmpl': f'{self.dir}/%(title)s.%(ext)s',
                'progress_hooks': [self.UpdateProgress]
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.link])

            self.finished.emit()

        except Exception as e:
            self.error.emit(str(e))

    def UpdateProgress(self, d):
        if d['status'] == 'downloading':
            percent = d['_percent_str'].strip().replace('%', '')
            self.progress.emit(int(float(percent)))


class YTdownloader(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGeometry(600, 300, 500, 200)
        self.setWindowIcon(QIcon("icon.webp"))
        self.setWindowTitle("YTdownloader")
        self.Interface()

    def Interface(self):
        #Labels
        urlLabel = QLabel("Enter URL:", self)
        urlLabel.setFont(QFont("Arial", 10))
        urlLabel.setStyleSheet("font-weight: bold;")

        dirLabel = QLabel("Enter download path:", self)
        dirLabel.setFont(QFont("Arial", 10))
        dirLabel.setStyleSheet("font-weight: bold;")

        resLabel = QLabel("Choose resolution:")
        resLabel.setFont(QFont("Arial", 10))
        resLabel.setStyleSheet("font-weight: bold;")

        progLabel = QLabel("Download progress:", self)
        progLabel.setFont(QFont("Arial", 10))
        progLabel.setStyleSheet("font-weight: bold;")

        #EditFields
        self.URLfield = QLineEdit()
        self.URLfield.setPlaceholderText("Video URL")
        self.URLfield.textChanged.connect(self.CheckInput)

        self.dirField = QLineEdit()
        self.dirField.setPlaceholderText("Download path")
        self.dirField.textChanged.connect(self.CheckInput)

        #Buttons
        self.chooseDirButton = QPushButton("&Browse", self)
        self.chooseDirButton.clicked.connect(self.ChooseDir)

        self.downloadButton = QPushButton("&Download", self)
        self.downloadButton.clicked.connect(self.Download)
        self.downloadButton.setDisabled(True)

        self.pasteButton = QPushButton("&Paste", self)
        self.pasteButton.clicked.connect(self.Paste)

        #RadioButtons
        self.highest = QRadioButton("1080p", self)
        self.highest.setChecked(True)

        self.high = QRadioButton("720p", self)

        self.medium = QRadioButton("480p", self)

        self.low = QRadioButton("360p", self)

        self.lower = QRadioButton("240p", self)

        self.lowest = QRadioButton("144p", self)

        #ProgressBar
        self.progBar = QProgressBar()
        self.progBar.setValue(0)
        self.progBar.setTextVisible(True)

        #Layout
        horLayout = QHBoxLayout()
        horLayout.addWidget(self.highest)
        horLayout.addWidget(self.high)
        horLayout.addWidget(self.medium)
        horLayout.addWidget(self.low)
        horLayout.addWidget(self.lower)
        horLayout.addWidget(self.lowest)

        gridLayout = QGridLayout()
        gridLayout.addWidget(urlLabel, 0, 0)
        gridLayout.addWidget(self.URLfield, 1, 0)
        gridLayout.addWidget(self.pasteButton, 1, 1)
        gridLayout.addWidget(dirLabel, 2, 0)
        gridLayout.addWidget(self.dirField, 3, 0)
        gridLayout.addWidget(self.chooseDirButton, 3, 1)
        gridLayout.addWidget(resLabel, 4, 0)
        gridLayout.addLayout(horLayout, 5, 0)
        gridLayout.addWidget(progLabel, 6, 0)
        gridLayout.addWidget(self.progBar, 7, 0)
        gridLayout.addWidget(self.downloadButton, 8, 0)

        self.setLayout(gridLayout)

        self.show()

    def ChooseDir(self):
        dir = QFileDialog.getExistingDirectory(None, 'Select a folder:', 'C:\\', QFileDialog.ShowDirsOnly)
        self.dirField.setText(dir)

    def Paste(self):
        paste = QApplication.clipboard()
        self.URLfield.setText(paste.text())

    def ChooseRes(self):
        if self.highest.isChecked():
            return 1080
        elif self.high.isChecked():
            return 720
        elif self.medium.isChecked():
            return 480
        elif self.low.isChecked():
            return 360
        elif self.lower.isChecked():
            return 240
        elif self.lowest.isChecked():
            return 144

    def CheckInput(self):
        if self.URLfield.text() and self.dirField.text():
            self.downloadButton.setDisabled(False)
        else:
            self.downloadButton.setDisabled(True)

    def UpdateBar(self, value):
        self.progBar.setValue(value)
        self.progBar.setFormat(f"Downloading... {value}%")

    def DownloadFinished(self):
        self.progBar.setValue(100)
        self.progBar.setFormat("Downloading finished!")
        self.downloadButton.setDisabled(False)

    def ShowError(self, errorMsg):
        QMessageBox.critical(self, "Error", f"Download failed:\n{errorMsg}")
        self.downloadButton.setDisabled(False)

    def Download(self):
        link = self.URLfield.text()
        dir = self.dirField.text()
        res = self.ChooseRes()

        self.progBar.setValue(0)
        self.progBar.setFormat("Preparing...")
        self.downloadButton.setDisabled(True)

        self.thread = DownloadProgress(link, dir, res)
        self.thread.progress.connect(self.UpdateBar)
        self.thread.finished.connect(self.DownloadFinished)
        self.thread.error.connect(self.ShowError)
        self.thread.start()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = YTdownloader()
    sys.exit(app.exec_())


