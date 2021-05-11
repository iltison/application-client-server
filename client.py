import sys
import socket 

from setting import Setting
from PyQt5.QtCore import Qt,pyqtSignal
from PyQt5.QtGui import QIntValidator, QDoubleValidator, QRegExpValidator, QValidator
from PyQt5.QtWidgets import QApplication,  QLineEdit, QWidget,  QFormLayout, QPushButton
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QMainWindow
from _thread import *

class Ui_MainWindow(object):
    """
    Класс для создания объектов интерфейса 
    """
    def setupUi(self, MainWindow):
        self.setWindowTitle('Клиент')
        self.setFixedSize(280, 220)
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

        # Предупреждение о диапазоне
        self.warning = QLabel(self)
        self.warning.setText('Диапазон:\nГод = [2020,2050], Ставка = [0,1]')
        self.warning.move(30, 170)
        self.warning.resize(200, 40)

class EchoClientProtocol(Setting):
    """
    Класс является подклассом, унаследованным от класса Setting, который содержит создание сокета TCP  и данных настроек
    """
    def __init__(self):
        super(EchoClientProtocol, self).__init__()
        self.connection_made()
        
    def connection_made(self):
        """
        Функция соединения связи с сервером
        """
        self.socket.connect(self.host_adress)

    def close_connection(self):
        """
        Функция завершения связи с сервером
        """
        self.socket.close()

    def data_received(self):
        """
        Функция для получения данных с сервера
        """
        returned_data = self.socket.recv(2048).decode()
        return returned_data

    def send_data(self, message: str):
        """
        Функция для отправки данных на сервер
        args:
            message - текстовая строка, для отправки на сервер 
        """
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
        
        
    def build_protocol(self):
        """
        Создание протокола соединения с сервером
        """
        try:
            self.protocol = EchoClientProtocol()
            self.append_text("Подключен к серверу")
            return self.protocol
        except ConnectionRefusedError:
            self.protocol = None
            self.append_text("Нет соединения с сервером")
            return self.protocol

    def send_data_to_server(self):
        """
        Функция для получения и отправки данных из строки 
        """
        rate = float(self.value_line_edit_rate.text())
        year = int(self.value_line_edit_year.text())
        self.protocol.send_data("\n".join([str(rate), str(year)]))
        returned_npv = self.protocol.data_received()
        return returned_npv

    def button_handler(self):
        """
        Обработчик нажатия на кнопку
        """
        if self.protocol is not None:
            npv = self.send_data_to_server()
            self.append_text(str(npv))

    def line_edit_year_handler(self):
        """
        Обработчик для строки с годом
        """
        try:
            if 2020 <= int(self.value_line_edit_year.text()) <= 2050:
                self.button.setEnabled(True)
            else:
                self.button.setEnabled(False)
        except ValueError:
            self.button.setEnabled(False)

    def line_edit_rate_handler(self):
        """
        Обработчик для строки с ставкой дисконтирования
        """
        try:
            self.value_line_edit_rate.setText(self.value_line_edit_rate.text().replace(',','.'))
            if 0 <= float(self.value_line_edit_rate.text()) <= 1:
                self.button.setEnabled(True)
            else:
                self.button.setEnabled(False)
        except ValueError:
            self.button.setEnabled(False)

    def append_text(self, content: str):
        """
        Функция для отображения текста на дисплее
        """
        self.display.setText(content)

    def closeEvent(self, event):
        """
        Обработка события закрытия приложения, завершается соединение с сервером, если оно было
        """
        if self.protocol is not None:
            self.protocol.close_connection()

    def keyPressEvent(self, event):
        """
        Обработка события нажатия Enter, срабатывает как кнопка "Расчёт"
        """
        if event.key() == Qt.Key_Return:
            self.button_handler()

        
def main():
    pycalc = QApplication(sys.argv)
    view = main_window()
    view.show()
    sys.exit(pycalc.exec_())

if __name__ == '__main__':
    main()
    
    