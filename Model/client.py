import threading
import socket
from asynchronous_message_server.View.client_interface import *
class Client(threading.Thread):

    def __init__(self, userName, selectUserUI):
        threading.Thread.__init__(self)
        self.userName = userName
        self.host = 'localhost'
        self.port = 8888
        self.postMethodName = 'POST'
        self.getMethodName = 'GET'
        self.sendUserNameMessage = 'send-username'
        self.sendComposedMessage = 'compose-message'
        self.start()

    def run(self) -> None:

        try:
            self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.soc.connect((self.host, self.port))
        except Exception as e:
            print(e.args[1])
        else:
            print(self.soc.getpeername())
            self.hostNameWithPort = str(self.soc.getsockname())
            print(self.hostNameWithPort)
            self.headerLines = {'Method': self.postMethodName,
                                'data': self.userName,
                                'Host': self.hostNameWithPort,
                                'User-Agent': self.userName,
                                'Message-Type': self.sendUserNameMessage
                                }
            self.httpMessage = httpRequestMessage()
            framedHttpMessage = self.httpMessage.frameHttpRequest(self.headerLines)
            try:
                self.soc.sendall(framedHttpMessage.encode('utf-8'))
            except Exception as e:
                print(e.args[1])
            else:
                self.response = self.soc.recv(1024)
                self.result = self.httpMessage.parseResposeMessage(self.response)
                print(self.result)
                if self.result['Status'] == 'True':
                    self.userUI = clientInterface(self.userName, self)
                else:
                    self.soc.close()
                    print('Taken')


    def postMeassage(self, rawMessage, toUser):
        print(rawMessage)
        self.headerLines['data'] = rawMessage
        self.headerLines['Message-Type'] = self.sendComposedMessage
        self.headerLines['To-User'] = toUser
        print(self.headerLines)
        framedComposedMessage = self.httpMessage.frameHttpRequest(self.headerLines)
        try:
            self.soc.sendall(framedComposedMessage.encode('utf-8'))
        except Exception as e:
            print(e.args[1])
        else:
            self.response = self.soc.recv(1024)
            self.result = self.httpMessage.parseResposeMessage(self.response)
            self.soc.close()
            print(self.result)

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
                           self.contentType + '\n' + 'Message-Type: ' + headerDict['Message-Type']
        if headerDict['Message-Type'] == 'compose-message':
            self.httpString += '\n' + 'Data: ' + headerDict['data'] + '\n' + 'To-User: ' + headerDict['To-User']
        return self.httpString

    def parseResposeMessage(self, resposeData):

        parsedData = resposeData.decode('utf-8')
        parsedList = parsedData.split('\n')
        parsedDict = {'Respose-Code': parsedList[0].split(" ")[0]}
        lenghtOfList = len(parsedList)
        for i in range(1, lenghtOfList):
            l = parsedList[i].split(": ", 1)
            parsedDict[l[0]] = l[1]
        return parsedDict


''' conn = http.client.HTTPConnection('localhost', 8000)
conn.request("GET", "/")
r1 = conn.getresponse()
print(r1.status, r1.reason)
data1 = r1.read()
print(data1)
conn.close()'''