import sys

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView as QWebView,QWebEnginePage as QWebPage
from PyQt5.QtWebEngineWidgets import QWebEngineSettings as QWebSettings
import subprocess

class Form(QWidget):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        # subprocess.Popen(['my_fastapi_app.exe'])
        # self.setWindowOpacity(1)
        # self.setWindowFlags(Qt.FramelessWindowHint)
        # self.setAttribute(Qt.WA_TranslucentBackground)
        # self.showFullScreen()
        rect = QApplication.desktop().screenGeometry()
        self.resize(rect.width(), rect.height())
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        self.webview = QWebView()

        vbox = QVBoxLayout()
        vbox.addWidget(self.webview)

        main = QGridLayout()
        main.setSpacing(0)
        main.addLayout(vbox, 0, 0)

        self.setLayout(main)

        # self.setWindowTitle("CoDataHD")
        # webview.load(QUrl('http://www.cnblogs.com/misoag/archive/2013/01/09/2853515.html'))
        # webview.show()

    def load(self, url):
        self.webview.load(QUrl(url))
        self.webview.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    screen = Form()
    screen.show()
    url = "http://localhost:8000/"
    screen.load(url)
    sys.exit(app.exec_())