import socket
import os
from _thread import start_new_thread

import numpy as np
import pandas as pd
from setting import Setting


class Server(Setting):
    """
    Класс является подклассом, унаследованным от класса Setting, который содержит создание сокета TCP и данных настроек
    """
    def __init__(self):
        super(Server, self).__init__()
        self.df = self.loading_dataframe(self.filename)

    def set_up(self):
        """
        Функция для создания прослушки TCP
        """
        self.socket.bind(self.host_adress)
        self.socket.listen(5)
        print("Server is listening")

    def listen_socket(self, listened_socket=None):
        """
        Функция для прослушивания запроса TCP
        """
        while True:
            try:
                data = listened_socket.recv(2048)
                if not data:
                    break
                rate, year = [(i) for i in data.decode().split('\n')]
                rate = float(rate)
                year = int(year)
                npv = str(self.getting_npv(year, rate))
                listened_socket.sendall(str.encode(npv))

            except ValueError:
                listened_socket.sendall(str.encode('ValueError'))
            except ConnectionAbortedError:
                listened_socket.close()
                return 
        listened_socket.close()
                
    def accept_sockets(self):
        """
        Функция для принятия запрсов от клиента
        """
        try:
            while True:
                Client, address = self.socket.accept()
                print('Connected to: ' + address[0] + ':' + str(address[1]))
                start_new_thread(self.listen_socket, (Client, ))
            self.socket.close()
        except:
            return

    def loading_dataframe(self,filename):
        """
        Функция для загрузки данных 
        """
        data = pd.read_excel(filename,sheet_name='справочник')
        data['год'] = pd.to_datetime(data['год'],format='%Y').dt.year
        data['чистый денежный поток'] = data['доход'] - data['затраты']
        return data 

    def getting_npv(self, year, rate):
        """
        Функция для получения значения NPV для конкретного года 
        """
        mask = (self.df['год'] <= year)
        slice_df = self.df.loc[mask]
        list_npv = np.zeros(len(slice_df))
        for row in range(len(slice_df)):
            if row == 0:
                list_npv[row] = slice_df.loc[row, 'чистый денежный поток']/np.power(1 + rate, row+1)
            else:
                list_npv[row] = slice_df.loc[row, 'чистый денежный поток']/np.power(1 + rate, row+1) + list_npv[row-1]
        return list_npv[-1] 

if __name__ == '__main__':
    server = Server()
    server.set_up()
    server.accept_sockets()