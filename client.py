import sys

from socket import *
from PyQt5 import QtWidgets
# Import QApplication and the required widgets from PyQt5.QtWidgets
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt,pyqtSignal
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QLabel
from setting import Setting
from PyQt5.QtGui import QIntValidator, QDoubleValidator, QRegExpValidator, QValidator


class Ui_MainWindow(object):
    

    def setupUi(self, MainWindow):
        if MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        self.setWindowTitle('Клиент')
        self.setFixedSize(280, 200)
        # Set the central widget and the general layout
        self.generalLayout = QVBoxLayout()
        self._centralWidget = QWidget(self)
        self.setCentralWidget(self._centralWidget)
        self._centralWidget.setLayout(self.generalLayout)
        # label rate text
        self.label_rate = QLabel(self)
        self.label_rate.setText('Cтавка \nдисконтирования')
        self.label_rate.move(20, 55)
        self.label_rate.setAlignment(Qt.AlignCenter)
        # value rate line 
        self.value_line_edit_rate = QLineEdit(self)
        self.value_line_edit_rate.move(120, 60)
        self.value_line_edit_rate.setText('0.2')
        self.value_line_edit_rate.adjustSize()
        self.value_line_edit_rate.setMaxLength(8)
        pDoubleValidator = QDoubleValidator(self)
        pDoubleValidator.setNotation(QDoubleValidator.StandardNotation)
        pDoubleValidator.setDecimals(4)
        self.value_line_edit_rate.setValidator(pDoubleValidator)

        # label year text
        self.label_year = QLabel(self)
        self.label_year.setText('Год')
        self.label_year.move(20, 85)
        self.label_year.setAlignment(Qt.AlignCenter)
        # value year text
        self.value_line_edit_year = QLineEdit(self)
        self.value_line_edit_year.move(120, 90)
        self.value_line_edit_year.setText('2050')
        self.value_line_edit_year.adjustSize()
        self.value_line_edit_year.setMaxLength(4)
        pIntValidator = QIntValidator(self)
        #pIntValidator.setRange(2020, 2050)
        self.value_line_edit_year.setValidator(pIntValidator)

        # button
        self.button = QPushButton('Расчёт', self)
        #self.button.clicked.connect(self.button1_clicked)
        self.button.resize(200,32)
        self.button.move(50, 120) 

        # Display
        self.display = QLineEdit(self)
        self.display.move(50, 10)
        self.display.resize(200, 32)
        self.display.setAlignment(Qt.AlignLeft)
        self.display.setReadOnly(True)

class EchoClientProtocol(Setting):

    def __init__(self):
        super(EchoClientProtocol, self).__init__()
        self.connection_made()
        
    def connection_made(self):
        self.socket.connect(self.host_adress)

    def close_connection(self):
        self.socket.close()

    def data_received(self):
        returned_data = self.socket.recv(2048).decode()
        return returned_data

    def send_data(self, message: str):
        self.socket.send(str.encode(message))


class main_window(QMainWindow, Ui_MainWindow):
    protocol: EchoClientProtocol

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.button.clicked.connect(self.button_handler)
        self.button.setAutoDefault(True)
        self.value_line_edit_year.textChanged.connect(self.line_edit_year_handler)
        self.value_line_edit_rate.textChanged.connect(self.line_edit_rate_handler)
        self.build_protocol()
        

    def line_edit_year_handler(self):
        try:
            if 2020 <= int(self.value_line_edit_year.text()) <= 2050:
                self.button.setEnabled(True)
            else:
                self.button.setEnabled(False)
        except ValueError:
            self.button.setEnabled(False)
    def line_edit_rate_handler(self):
        try:
            if -1 <= float(self.value_line_edit_rate.text()) <= 1:
                self.button.setEnabled(True)
            else:
                self.button.setEnabled(False)
        except ValueError:
            self.button.setEnabled(False)

    def button_handler(self):
        print("Button 1 clicked")
        if self.protocol is not None:
            npv = self.requests_data_to_server()
            self.append_text(str(npv))

    def append_text(self, content: str):
        self.display.setText(content)

    def requests_data_to_server(self):
        rate = float(self.value_line_edit_rate.text())
        year = int(self.value_line_edit_year.text())
        self.protocol.send_data("\n".join([str(rate), str(year)]))
        returned_npv = self.protocol.data_received()
        return returned_npv


    def closeEvent(self, event):
        if self.protocol is not None:
            self.protocol.close_connection()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            self.button_handler()

    def build_protocol(self):
        try:
            self.protocol = EchoClientProtocol()
            self.append_text("Подключен к серверу")
            return self.protocol
        except ConnectionRefusedError:
            self.protocol = None
            self.append_text("Нет соединения с сервером")
            return self.protocol
        
def main():
    pycalc = QApplication(sys.argv)
    view = main_window()
    view.show()
    sys.exit(pycalc.exec_())

if __name__ == '__main__':
    main()
    
    