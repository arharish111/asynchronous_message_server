'''
MIT License

Copyright (c) 2019 Harish

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import socket
import threading
from datetime import datetime
from asynchronous_message_server.View.server_interface import *
userDict = {'A': 0, 'B': 0, 'C': 0} #to store connected users
aList = []  # to store messages for client A
bList = []  # to store messages for client B
cList = []  # to store messages for client C

# To start the server
class Server:

    def startServer(self, interface):

        self.interface = interface
        host = 'localhost'  # setting host
        port = 8888  # setting port number
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc.bind((host, port))  # binding to the set host and port number
        self.soc.listen(3)  # only listens to three clients
        while True:
            conn, addr = self.soc.accept()
            if conn:
                Connections(conn, self.interface)

# Threading sub-class to handle clients
class Connections(threading.Thread):

    def __init__(self, conn, interface):
        threading.Thread.__init__(self)
        self.conn = conn
        self.interface = interface
        self.headerLines = {'Server': str(self.conn.getsockname()), 'Status': 'True'}
        self.start()  # threads gets started

    def run(self) -> None:
        while True:
            data = self.conn.recv(1024)  # receive data from the client
            if data:
                result = self.parseData(data)
                self.interface.addToTextBox(result)  # Display HTTP response
                if self.headerLines['Status'] == 'True':
                    self.conn.sendall(result.encode('utf-8'))  # send data to the client
                else:
                    self.conn.sendall(result.encode('utf-8'))
                    break

# Function to parse the incoming HTTP message
    def parseData(self, data):
        parsedData = data.decode('utf-8')
        self.interface.addToTextBox(parsedData)  # Display incoming HTTP request
        parsedList = parsedData.split('\n')
        parsedDict = {'Method': parsedList[0].split(" ")[0]}
        lenghtOfList = len(parsedList)

        for i in range(1, lenghtOfList):
            l = parsedList[i].split(": ", 1)
            parsedDict[l[0]] = l[1]

        self.httpRespose = httpResponseMessage()

        if parsedDict['Message-Type'] == 'send-username':

            self.headerLines['Message-Type'] = 'respond-username'

            if userDict[parsedDict['User-Agent']]:
                self.headerLines['Status'] = 'False'
            else:
                userDict[parsedDict['User-Agent']] = 1
                self.interface.addToTextBox('Connected User: ' + parsedDict['User-Agent'])

        elif parsedDict['Message-Type'] == 'compose-message':

            self.headerLines['Message-Type'] = 'respond-compose'

            if parsedDict['To-User'] == 'A':
                aList.append(parsedDict['Data'])

            elif parsedDict['To-User'] == 'B':
                bList.append(parsedDict['Data'])

            else:
                cList.append(parsedDict['Data'])
            userDict[parsedDict['User-Agent']] = 0
            self.interface.addToTextBox('Disconnected User: ' + parsedDict['User-Agent'])

        elif parsedDict['Message-Type'] == 'check-message':

            self.headerLines['Message-Type'] = 'respond-check'

            if parsedDict['User-Agent'] == 'A':
                self.headerLines['From-List'] = 'A'
                if not aList:
                    self.headerLines['Status'] = 'False'

            elif parsedDict['User-Agent'] == 'B':
                self.headerLines['From-List'] = 'B'
                if not bList:
                    self.headerLines['Status'] = 'False'

            else:
                self.headerLines['From-List'] = 'C'
                if not cList:
                    self.headerLines['Status'] = 'False'

            userDict[parsedDict['User-Agent']] = 0
            self.interface.addToTextBox('Disconnected User: ' + parsedDict['User-Agent'])
        self.headerLines['Date'] = str(datetime.now())
        return self.httpRespose.framehttpRespose(self.headerLines)

# Class to frame HTTP response messages
class httpResponseMessage:

    def __init__(self):

        self.okResponse = 'HTTP/1.1 200 OK'
        self.contentType = 'Text'
        self.accepted = 'True'
        self.rejected = 'False'
        self.messageAccepted = 'True'

    def framehttpRespose(self, headerDict):

        self.httpString = ''
        self.httpString += self.okResponse
        self.httpString += '\n' + 'Server: ' + headerDict['Server'] + '\n' + 'Content-Type: ' + self.contentType + \
                            '\n' + 'Message-Type: ' + headerDict['Message-Type'] + \
                           '\n' + 'Status: ' + headerDict['Status'] + '\n' + 'Date: ' + headerDict['Date']
        if headerDict['Message-Type'] == 'respond-check':
            if headerDict['Status'] == 'True':
                if headerDict['From-List'] == 'A':
                    framedString = self.listToString(aList)
                    aList.clear()
                elif headerDict['From-List'] == 'B':
                    framedString = self.listToString(bList)
                    bList.clear()
                else:
                    framedString = self.listToString(cList)
                    cList.clear()
                contentLength = str(len(framedString.encode('utf-8')))
                self.httpString += '\n' + 'Data: ' + framedString + '\n' + 'Content-Length: ' + contentLength

        return self.httpString

    def listToString(self, messageList):

        string = ''
        for s in messageList:
            string += s + ','
        return string
