'''
Student Name: Harish Harish
Student ID: 1001682418
'''
import threading
import socket
from datetime import datetime
from asynchronous_message_server.View.client_interface import *

# Threaded class to handle client connection
class Client(threading.Thread):

    def __init__(self, userName, mainWindow):
        threading.Thread.__init__(self)
        self.userName = userName
        self.mainUI = mainWindow
        self.host = 'localhost'
        self.port = 8888
        self.postMethodName = 'POST'
        self.getMethodName = 'GET'
        self.sendUserNameMessage = 'send-username'
        self.sendComposedMessage = 'compose-message'
        self.checkMessage = 'check-message'
        self.start()

    def run(self) -> None:

        try:
            self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.soc.connect((self.host, self.port))  # making connection with the server
        except Exception as e:
            print(e.args[1])
        else:
            self.hostNameWithPort = str(self.soc.getsockname())
            self.headerLines = {'Method': self.postMethodName,
                                'data': self.userName,
                                'Host': self.hostNameWithPort,
                                'User-Agent': self.userName,
                                'Message-Type': self.sendUserNameMessage,
                                'Date': str(datetime.now())
                                }
            self.httpMessage = httpRequestMessage()
            framedHttpMessage = self.httpMessage.frameHttpRequest(self.headerLines)
            try:
                self.soc.sendall(framedHttpMessage.encode('utf-8'))  # sending HTTP message to the server
            except Exception as e:
                print(e.args[1])
            else:
                self.response = self.soc.recv(1024)  # Receiving HTTP message from the server
                self.result = self.httpMessage.parseResposeMessage(self.response)
                if self.result['Status'] == 'True':
                    self.userUI = clientInterface(self.userName, self)
                else:
                    self.soc.close()
                    self.mainUI.displayMessageBox()

# to send POST HTTP message to the server
    def postMeassage(self, rawMessage, toUser):

        self.headerLines['data'] = rawMessage
        self.headerLines['Content-Length'] = str(len(rawMessage.encode('utf-8')))
        self.headerLines['Message-Type'] = self.sendComposedMessage
        self.headerLines['To-User'] = toUser
        self.headerLines['Date'] = str(datetime.now())
        framedComposedMessage = self.httpMessage.frameHttpRequest(self.headerLines)
        try:
            self.soc.sendall(framedComposedMessage.encode('utf-8'))
        except Exception as e:
            print(e.args[1])
        else:
            self.response = self.soc.recv(1024)
            self.result = self.httpMessage.parseResposeMessage(self.response)
            self.soc.close()

# to send GET HTTP message to the server
    def getMessage(self):

        self.headerLines['Method'] = self.getMethodName
        self.headerLines['Message-Type'] = self.checkMessage
        self.headerLines['Date'] = str(datetime.now())
        framedGetMessage = self.httpMessage.frameHttpRequest(self.headerLines)
        try:
            self.soc.sendall(framedGetMessage.encode('utf-8'))
        except Exception as e:
            print(e.args[1])
        else:
            self.response = self.soc.recv(1024)
            self.result = self.httpMessage.parseResposeMessage(self.response)
            if self.result['Status'] == 'True':
                self.userUI.displayReceivedMessage(self.result['Data'])
            else:
                self.userUI.displayReceivedMessage(None)
            self.soc.close()  # closing the connection

# To frame and parse HTTP messages
class httpRequestMessage:

    def __init__(self):

        self.postRequestLine = 'POST HTTP/1.1'
        self.getRequestLine = 'GET HTTP/1.1'
        self.contentType = 'Text'

    def frameHttpRequest(self, headerDict):

        self.httpString = ''
        if headerDict['Method'] == 'POST':
            self.httpString += self.postRequestLine
        else:
            self.httpString += self.getRequestLine
        self.httpString += '\n' + 'Host: ' + headerDict['Host'] + '\n' + 'User-Agent: ' + \
                           headerDict['User-Agent'] + '\n' + 'Content-Type: ' + \
                           self.contentType + '\n' + 'Message-Type: ' + headerDict['Message-Type'] + \
                           '\n' + 'Date: ' + headerDict['Date']
        if headerDict['Message-Type'] == 'compose-message':
            self.httpString += '\n' + 'Data: ' + headerDict['data'] + '\n' + 'To-User: ' + headerDict['To-User'] + \
                               '\n' + 'Content-Length: ' + headerDict['Content-Length']
        return self.httpString

    def parseResposeMessage(self, resposeData):

        parsedData = resposeData.decode('utf-8')
        parsedList = parsedData.split('\n')
        parsedDict = {'Respose-Code': parsedList[0].split("\n")[0]}
        lenghtOfList = len(parsedList)
        for i in range(1, lenghtOfList):
            l = parsedList[i].split(": ", 1)
            parsedDict[l[0]] = l[1]
        return parsedDict
