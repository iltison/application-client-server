import socket
import os
from _thread import *

import numpy as np
import pandas as pd
from setting import Setting


class Server(Setting):
    def __init__(self):
        super(Server, self).__init__()
        self.users = []
        self.df = self.loading_dataframe('Расчет NPV.XLSX')

    def set_up(self):
        self.socket.bind(self.host_adress)
        self.socket.listen(5)
        #self.socket.setblocking(False)
        print("Server is listening")

    def listen_socket(self, listened_socket=None):
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
                listened_socket.sendall(str.encode('Error'))
            except ConnectionAbortedError:
                print('клиент вышел')
                listened_socket.close()
                return 
        listened_socket.close()
                
    def accept_sockets(self):
        while True:
            Client, address = self.socket.accept()
            print('Connected to: ' + address[0] + ':' + str(address[1]))
            self.users.append(Client)
            start_new_thread(self.listen_socket, (Client, ))
        self.socket.close()

    def loading_dataframe(self,filename):
        df = pd.read_excel(filename,sheet_name='справочник')
        df['год'] = pd.to_datetime(df['год'],format='%Y').dt.year
        df['чистый денежный поток'] = df['доход'] - df['затраты']
        return df 

    def getting_npv(self, year, rate):
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