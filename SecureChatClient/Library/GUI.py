from tkinter import *

LOGIN_FRAME = 0
HOME_FRAME = 1

window = Tk()
window.title("Chat Client")
window.minsize(500, 500)
frames = list()

############# LOGIN #############
frames.append(Frame(window))

username_label = Label(frames[LOGIN_FRAME], text="Username\t\t").place(relx=.5, rely=.4, anchor="e")
input_username = StringVar()
username_input = Entry(frames[LOGIN_FRAME], text=input_username)
username_input.place(relx=.5, rely=.4, anchor="center")

password_label = Label(frames[LOGIN_FRAME], text="Password\t\t").place(relx=.5, rely=.5, anchor="e")
input_password = StringVar()
password_input = Entry(frames[LOGIN_FRAME], text=input_password, show="*")
password_input.place(relx=.5, rely=.5, anchor="center")

login_button = Button(frames[LOGIN_FRAME], text="Login")
login_button.place(relx=.5, rely=.6, anchor="center")

current_frame = LOGIN_FRAME
frames[current_frame].pack(expand=True, fill=BOTH)
user_pass = ()
#################################

########## CHAT SELECT ##########
frames.append(Frame(window))

Scrollbar(frames[HOME_FRAME], orient="vertical").pack(side=RIGHT, fill=Y)
chat_buttons = [Button(frames[HOME_FRAME], text="Chat with %s" % "Bob")]
for i in range(len(chat_buttons)):
    chat_buttons[i].pack(side=TOP, fill=X)
#################################

########## CHAT SCREEN ##########
frames.append(Frame(window))

user = challenger = ""
messages = Text(frames[2], state="disabled")
chat_scroll = Scrollbar(command=messages.yview)
messages["yscrollcommand"] = chat_scroll.set
messages.pack(expand=True, fill=BOTH)

input_message = StringVar()
chat_input = Entry(frames[2], text=input_message)
chat_input.pack(side=BOTTOM, fill=X)
#################################


def login_attempt(event):
    global user_pass
    user_pass = (username_input.get().strip(), password_input.get().strip())
    input_username.set("")
    input_password.set("")


def successful_login():
    global current_frame
    frames[current_frame].pack_forget()
    current_frame = HOME_FRAME
    frames[current_frame].pack(expand=True, fill=BOTH)


def load_chat(event, frame_num, other_user):
    global challenger, current_frame
    challenger = other_user
    frames[current_frame].pack_forget()
    current_frame = frame_num
    frames[current_frame].pack(expand=True, fill=BOTH)
    if(messages.compare("end-1c", "==", "1.0")):  # Print connected message at beginning of chat
        messages.configure(state='normal')
        messages.insert(END, "Connected to %s\n" % challenger)
        messages.configure(state='disabled')
    messages.see("end")
    chat_input.focus_set()


def return_home(event):
    global current_frame
    frames[current_frame].pack_forget()
    current_frame = HOME_FRAME
    frames[current_frame].pack(expand=True, fill=BOTH)


def send_message(event):
    input_get = chat_input.get().rstrip()
    if(input_get != ""):
        messages.configure(state='normal')
        messages.insert(END, "%s: %s\n" % (user, input_get))
        messages.see("end")
        messages.configure(state='disabled')
    input_message.set("")
    receive_message("Automatic response for testing")
    return "break"


def receive_message(message):
    messages.configure(state='normal')
    messages.insert(END, "%s: %s\n" % (challenger, message))
    messages.see("end")
    messages.configure(state='disabled')


password_input.bind("<Return>", login_attempt)
login_button.bind("<Button-1>", login_attempt)

for i in range(len(chat_buttons)):
    button_label = chat_buttons[i].cget("text")
    challenger = button_label[10:]
    chat_buttons[i].bind("<Button-1>", lambda event: load_chat(event, i+2, challenger))

chat_input.bind("<Return>", send_message)
chat_input.bind("<Escape>", return_home)
