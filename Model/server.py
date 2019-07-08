import socket
import threading
from asynchronous_message_server.View.server_interface import *
userDict = {'A': 0, 'B': 0, 'C': 0}
aList = []
bList = []
cList = []
class Server:

    def startServer(self, interface):

        self.interface = interface
        host = 'localhost'
        port = 8888
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.soc.bind((host, port))
        self.soc.listen(3)
        while True:
            conn, addr = self.soc.accept()
            if conn:
                print(f'1.{conn}')
                Connections(conn, self.interface)

class Connections(threading.Thread):

    def __init__(self, conn, interface):
        threading.Thread.__init__(self)
        self.conn = conn
        self.interface = interface
        self.headerLines = {'Server': str(self.conn.getsockname()), 'Status': 'True'}
        self.start()

    def run(self) -> None:
        while True:
            data = self.conn.recv(1024)
            if data:
                result = self.parseData(data)
                if self.headerLines['Status'] == 'True':
                    self.conn.sendall(result.encode('utf-8'))
                else:
                    self.conn.sendall(result.encode('utf-8'))
                    break


    def parseData(self, data):
        parsedData = data.decode('utf-8')
        self.interface.addToTextBox(parsedData)
        parsedList = parsedData.split('\n')
        parsedDict = {'Method': parsedList[0].split(" ")[0]}
        lenghtOfList = len(parsedList)
        print(lenghtOfList)
        for i in range(1, lenghtOfList):
            l = parsedList[i].split(": ", 1)
            print(l)
            parsedDict[l[0]] = l[1]
        print(parsedDict)
        self.httpRespose = httpResponseMessage()

        if parsedDict['Message-Type'] == 'send-username':

            self.headerLines['Message-Type'] = 'respond-username'

            if userDict[parsedDict['User-Agent']]:
                self.headerLines['Status'] = 'False'
            else:
                userDict[parsedDict['User-Agent']] = 1

        elif parsedDict['Message-Type'] == 'compose-message':

            self.headerLines['Message-Type'] = 'respond-compose'

            if parsedDict['To-User'] == 'A':
                aList.append(parsedDict['Data'])

            elif parsedDict['To-User'] == 'B':
                bList.append(parsedDict['Data'])

            else:
                cList.append(parsedDict['Data'])
            userDict[parsedDict['User-Agent']] = 0

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

        return self.httpRespose.framehttpRespose(self.headerLines)

class httpResponseMessage:

    def __init__(self):

        self.okResponse = 'HTTP/1.1 200 OK'
        self.contentType = 'Text'
        self.accepted = 'True'
        self.rejected = 'False'
        self.messageAccepted = 'True'

    def framehttpRespose(self, headerDict):

        print(headerDict)
        self.httpString = ''
        self.httpString += self.okResponse
        self.httpString += '\n' + 'Server: ' + headerDict['Server'] + '\n' + 'Content-Type: ' + self.contentType + \
                            '\n' + 'Message-Type: ' + headerDict['Message-Type'] + \
                           '\n' + 'Status: ' + headerDict['Status']
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
                self.httpString += '\n' + 'Data: ' + framedString

        return self.httpString

    def listToString(self, messageList):

        string = ''
        for s in messageList:
            string += s + ','
        return string




#if __name__ == '__main__':main()

'''httpd = HTTPServer(('localhost', 8000), Server)
    httpd.serve_forever()'''
'''class Server(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Hello, world!')'''