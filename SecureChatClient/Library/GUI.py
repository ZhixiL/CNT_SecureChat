from tkinter import *


class ChatFrame(Frame):

    def __init__(self, challenger, enter, esc):
        super(ChatFrame, self).__init__()

        if(enter is not None and esc is not None):
            ########## CHAT SCREEN ##########
            self.messages = Text(self, state="disabled")
            self.chat_scroll = Scrollbar(command=self.messages.yview)
            self.messages["yscrollcommand"] = self.chat_scroll.set
            self.messages.pack(expand=True, fill=BOTH)

            self.input_message = StringVar()
            self.chat_input = Entry(self, text=self.input_message)
            self.chat_input.pack(side=BOTTOM, fill=X)

            self.chat_input.bind("<Return>", enter)
            self.chat_input.bind("<Escape>", esc)

            self.challenger = challenger
            #################################

    def get_challenger(self):
        return self.challenger

    def get_input(self):
        return self.chat_input.get().rstrip()

    def set_focus(self):
        # Print connected message at beginning of chat
        if (self.messages.compare("end-1c", "==", "1.0")):
            self.messages.configure(state='normal')
            self.messages.insert(END, "Connected to %s\n" % self.challenger)
            self.messages.configure(state='disabled')
        self.messages.see("end")
        self.chat_input.focus_set()

    def send_message(self, user):
        self.messages.configure(state='normal')
        self.messages.insert(END, "%s: %s\n" % (user, self.chat_input.get().rstrip()))
        self.messages.see("end")
        self.messages.configure(state='disabled')
        self.input_message.set("")

    def recieve_message(self, message):
        self.messages.configure(state='normal')
        if (message == ""):
            self.messages.insert(END, "%s is now offline.\n" % self.challenger)
        else:
            self.messages.insert(END, "%s: %s\n" % (self.challenger, message))
        self.messages.see("end")
        self.messages.configure(state='disabled')

class GUI:

    def __init__(self):
        self.disconnected = False

        self.LOGIN_FRAME = 0
        self.HOME_FRAME = 1

        self.window = Tk()
        self.window.title("Chat Client")
        self.window.minsize(500, 500)
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.frames = list()

        ############# LOGIN #############
        self.frames.append(ChatFrame(self.window, None, None))

        Label(self.frames[self.LOGIN_FRAME], text="Username\t\t")\
            .place(relx=.5, rely=.4, anchor="e")
        self.input_username = StringVar()
        self.username_input = Entry(self.frames[self.LOGIN_FRAME], text=self.input_username)
        self.username_input.place(relx=.5, rely=.4, anchor="center")

        Label(self.frames[self.LOGIN_FRAME], text="Password\t\t")\
            .place(relx=.5, rely=.5, anchor="e")
        self.input_password = StringVar()
        self.password_input = Entry(self.frames[self.LOGIN_FRAME],
                                    text=self.input_password, show="*")
        self.password_input.place(relx=.5, rely=.5, anchor="center")

        self.login_button = Button(self.frames[self.LOGIN_FRAME], text="Login")
        self.login_button.place(relx=.5, rely=.6, anchor="center")

        self.current_frame = self.LOGIN_FRAME
        self.frames[self.current_frame].pack(expand=True, fill=BOTH)

        self.password_input.bind("<Return>", self.login_attempt)
        self.login_button.bind("<Button-1>", self.login_attempt)

        self.user_pass = ()
        self.logged_in = False
        #################################

        ########## CHAT SELECT ##########
        self.frames.append(ChatFrame(self.window, None, None))

        Label(self.frames[self.HOME_FRAME], text="Who would you like to chat with?") \
            .place(relx=.5, rely=.4, anchor=CENTER)
        self.input_request = StringVar()
        self.request_input = Entry(self.frames[self.HOME_FRAME], text=self.input_request)
        self.request_input.place(relx=.5, rely=.5, anchor="center")

        self.request_input.bind("<Return>", self.submit_request)

        self.request = ""
        #################################

        ########## CHAT SCREEN ##########
        self.challenger = ""
        self.outbox = ""
        #################################

    def get_disconnected(self):
        return self.disconnected

    def get_user_pass(self):
        return self.user_pass

    def get_request(self):
        return self.request

    def get_challenger(self):
        return self.challenger

    def get_outbox(self):
        outbox = self.outbox
        self.outbox = ""
        return outbox

    def login_attempt(self, event):
        self.user_pass = (self.username_input.get().strip(), self.password_input.get().strip())

    def failed_login(self):
        self.user_pass = ()
        self.username_input.config(bg="#f55555")
        self.password_input.config(bg="#f55555")
        self.input_username.set("")
        self.input_password.set("")

    def successful_login(self):
        if(not self.logged_in):
            self.logged_in = True
            self.frames[self.current_frame].pack_forget()
            self.current_frame = self.HOME_FRAME
            self.frames[self.current_frame].pack(expand=True, fill=BOTH)

    def submit_request(self, event):
        self.request = self.request_input.get().strip()
        self.challenger = self.request

    def failed_request(self):
        self.request = ""
        self.request_input.config(bg="#f55555")
        self.input_request.set("")

    def successful_request(self, challenger):
        self.request_input.config(bg="#f0f0f0")
        self.challenger = challenger
        self.frames[self.current_frame].pack_forget()
        self.current_frame = -1
        for i in range(2, len(self.frames)):
            if(self.frames[i].get_challenger() == challenger):
                self.current_frame = i
        if(self.current_frame == -1):
            self.current_frame = len(self.frames)
            self.frames.append(ChatFrame(challenger, self.send_message, self.return_home))
        self.frames[self.current_frame].pack(expand=True, fill=BOTH)
        self.frames[self.current_frame].set_focus()

    def return_home(self, event):
        self.frames[self.current_frame].pack_forget()
        self.current_frame = self.HOME_FRAME
        self.frames[self.current_frame].pack(expand=True, fill=BOTH)
        self.challenger = ""

    def send_message(self, event):
        input_get = self.frames[self.current_frame].get_input()
        if(input_get != ""):
            self.frames[self.current_frame].send_message(self.user_pass[0])
        self.outbox = input_get
        return "break"

    def receive_message(self, challenger, message):
        for i in range(2, len(self.frames)):
            if(self.frames[i].get_challenger() == challenger):
                self.frames[i].recieve_message(message)
                break;

    def update(self):
        self.window.update()

    def on_closing(self):
        self.disconnected = True
        self.window.destroy()
