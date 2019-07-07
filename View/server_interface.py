from asynchronous_message_server.Model.server import *

class serverUI(threading.Thread):

    def __init__(self):

        threading.Thread.__init__(self)
        self.start()

    def run(self) -> None:
        self.window = Tk()

        self.textBox = Text(self.window, width=40, height=30)
        self.textBox.pack()

        #ttk.Button(self.window, text='start', command=lambda: startCallBack()).pack()

        self.window.mainloop()

    def addToTextBox(self, message):

        self.textBox.insert('end', message)

def main():
    gui = serverUI()
    serverMain = Server()
    serverMain.startServer(gui)

if __name__ == '__main__':main()

