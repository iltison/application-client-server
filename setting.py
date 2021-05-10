import socket

class Setting():
    def __init__(self):

        self.__host = '127.0.0.1'
        self.__port = 1233
        self.host_adress = (self.__host, self.__port)

        self.socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
        )

        