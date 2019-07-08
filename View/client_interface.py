from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import threading
import socket
from asynchronous_message_server.Model.client import *

class clientInterface(threading.Thread):

    def __init__(self, userName, connect):
        threading.Thread.__init__(self)
        self.userName = userName
        self.connect = connect
        self.start()

    def run(self) -> None:

        self.window = Tk()
        self.window.title(self.userName)

        self.composeMessageButton = ttk.Button(self.window, text='Compose a Message',
                                               command=self.composeMessageCallBack)
        self.composeMessageButton.pack()

        self.checkMessageButton = ttk.Button(self.window, text='Check for Messages',
                                             command=self.checkMessageCallBack)
        self.checkMessageButton.pack()

        self.window.mainloop()

    def composeMessageCallBack(self):

        self.composeMessageButton.state(['disabled'])
        self.checkMessageButton.state(['disabled'])

        self.textBox = Text(self.window, width=40, height=10)
        self.textBox.pack()

        ttk.Label(self.window, text='Select Recipient').pack()

        if self.window.title() == 'A':
            ttk.Button(self.window, text='B', command=lambda: self.toUserCallBack('B')).pack()
            ttk.Button(self.window, text='C', command=lambda: self.toUserCallBack('C')).pack()
        elif self.window.title() == 'B':
            ttk.Button(self.window, text='A', command=lambda: self.toUserCallBack('A')).pack()
            ttk.Button(self.window, text='C', command=lambda: self.toUserCallBack('C')).pack()
        else:
            ttk.Button(self.window, text='A', command=lambda: self.toUserCallBack('A')).pack()
            ttk.Button(self.window, text='B', command=lambda: self.toUserCallBack('B')).pack()

        self.sendButton = ttk.Button(self.window, text='Send', command=self.doneCallBack)
        self.sendButton.state(['disabled'])
        self.sendButton.pack()

    def toUserCallBack(self, toUser):

        self.toUser = toUser
        self.sendButton.state(['!disabled'])

    def doneCallBack(self):
        message = self.textBox.get('1.0', 'end')
        message = message.split("\n")[0]
        print(message)
        self.connect.postMeassage(message, self.toUser)
        self.notifyMessageSent()
        self.window.destroy()

    def notifyMessageSent(self):
        messagebox.showinfo('Info', 'Message sent Successfully')

    def checkMessageCallBack(self):

        self.composeMessageButton.state(['disabled'])
        self.checkMessageButton.state(['disabled'])

        self.displayText = Text(self.window, width=40, height=10)
        self.displayText.pack()

        doneButton = ttk.Button(self.window, text='Done', command=self.closeWindow)
        doneButton.pack()

        self.connect.getMessage()

    def displayReceivedMessage(self, messageToDispaly):

        if messageToDispaly:
            self.displayText.insert('1.0', messageToDispaly)
        else:
            self.displayText.insert('1.0', 'No messages at this moment')

        #self.closeWindow()

    def closeWindow(self):
        self.window.destroy()

'''
   def selectUserCallBack(self, userName):

        self.connect = Client()

        if userName == 'A':
            self.userAButton.state(['disabled'])
        elif userName == 'B':
            self.userBButton.state(['disabled'])
        else:
            self.userCButton.state(['disabled'])

        window = Toplevel(self.master)
        window.title(userName)

        self.composeMessageButton = ttk.Button(window, text='Compose a Message', command=lambda: self.composeMessageCallBack(window))
        self.composeMessageButton.pack()

        checkMessageButton = ttk.Button(window, text='Check for Messages')
        checkMessageButton.pack()'''

    #def checkMessageCallBack(self):

class selectUserUI(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.start()
    def run(self) -> None:
        self.master = Tk()
        self.userOptionLabel = ttk.Label(self.master, text='Select User')
        self.userOptionLabel.grid(row=0, column=0, columnspan=3)

        self.userAButton = ttk.Button(self.master, text='A', command=lambda: selectUserCallBack('A', self))
        self.userAButton.grid(row=1, column=0)

        self.userBButton = ttk.Button(self.master, text='B', command=lambda: selectUserCallBack('B', self))
        self.userBButton.grid(row=1, column=1)

        self.userCButton = ttk.Button(self.master, text='C', command=lambda: selectUserCallBack('C', self))
        self.userCButton.grid(row=1, column=2)

        exitButton = ttk.Button(self.master, text='Exit', command=self.closeWindow)
        exitButton.grid(row=2, column=1)

        self.master.mainloop()

    def closeWindow(self):
        self.master.destroy()

    def displayMessageBox(self):
        messagebox.showerror(title='Error', message='This user name is taken.Please select another user')

def selectUserCallBack(userName, master):
     Client(userName, master)

def main():
    selectUserUI()

if __name__ == '__main__': main()