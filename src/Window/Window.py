import os
import re
import sys
import tkinter as tk
from pathlib import Path
from shutil import copy
from tkinter import messagebox, ttk
from tkinter.filedialog import askopenfilename

from bs4 import BeautifulSoup
from epub_conversion.utils import open_book, convert_epub_to_lines
from validate_email import validate_email

from src.Config import ConfigHandler
from src.Login import Login
from src.Mailer import Mailer


class Window:

    def __init__(self):
        self.master = tk.Tk()
        self.master.maxsize(width=1420, height=400)
        self.container = ttk.Frame(self.master)
        self.canvas = tk.Canvas(self.container, width=400, height=400)
        self.scrollbar = ttk.Scrollbar(self.container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.word_list = []
        self.input = []
        self.message = []
        self.email_address = []
        self.add_new_email = ""
        self.valid_email = False
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.scrollable_frame.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # self.login()

        self.app_ui_buttons()
        self.text_box()
        self.result_box()

        self.canvas.pack(side="left", fill="both", expand=True)
        self.container.pack(side="left", fill="both", expand=True)

        self.scrollbar.pack(side="right", fill="y", expand=False)

        self.master.title("Engima")
        self.master.iconbitmap("icon.ico")
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.master.bind('<Escape>', func=lambda e: self.master.destroy())
        self.master.bind('<Control-s>', func=lambda e: self.send_mail())
        self.master.mainloop()

    def app_ui_buttons(self):
        fr_buttons = tk.Frame(self.scrollable_frame, relief=tk.RAISED, bd=3)
        btn_load = tk.Button(fr_buttons, text="Load", command=self.get_input)
        btn_open = tk.Button(fr_buttons, text="Open", command=self.open_file)
        btn_add_email = tk.Button(fr_buttons, text="Send As eMail", command=self.select_recipient)
        btn_send_mail = tk.Button(fr_buttons, text="Add Recipient", command=self.add_mail)
        setattr(self, 'checkCmd', tk.IntVar())
        self.checkCmd.set(0)

        btn_function = tk.Checkbutton(fr_buttons, variable=self.checkCmd, onvalue=1, offvalue=0, text="Decode")

        btn_open.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        btn_load.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        btn_add_email.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        btn_send_mail.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
        btn_function.grid(row=4, column=0, sticky="ew", padx=5, pady=5)
        fr_buttons.grid(row=0, column=0, sticky="ns")

    def select_recipient(self):
        ch = ConfigHandler.ConfigHandler()
        contacts = ch.get_stored_contacts()

        def check():
            email_input = self.email_addresses
            if email_input and all(map(validate_email, email_input)):
                setattr(self, 'valid_email', True)
                self.recipient_list_box_base.destroy()
                self.send_mail(email_input)

        def cur_select(evt):
            widget = evt.widget

            selected_text_list = [widget.get(i) for i in widget.curselection()]
            setattr(self, 'email_addresses', selected_text_list)
            print(self.email_addresses)

        setattr(self, 'recipient_list_box_base', tk.Toplevel(width=50, height=100))
        setattr(self, 'recipient_listbox',
                tk.Listbox(self.recipient_list_box_base, selectmode=tk.MULTIPLE, width=60, height=10,
                           font=('times', 13)))
        self.recipient_listbox.bind('<<ListboxSelect>>', cur_select)

        b = ttk.Button(self.recipient_list_box_base, text="Okay", command=check)
        b.grid(row=1, column=0)

        self.recipient_listbox.grid(row=0, column=1, sticky="ewns")

        for items in contacts:
            self.recipient_listbox.insert(0, items)

    def login(self):
        self.hide()

        def check():
            lg = Login.Login(self.un.get(), self.pw.get()).__call__()
            if lg == "Ok":
                self.show()
                self.win.destroy()

            return lg

        setattr(self, 'win', tk.Toplevel(width=100, height=100))
        self.win.wm_title("Login")
        setattr(self, 'un', tk.Entry(self.win))
        setattr(self, 'pw', tk.Entry(self.win, show='*'))
        un_label = tk.Label(self.win, text="Email address")
        pw_label = tk.Label(self.win, text="Password")
        self.un.grid(row=0, column=1)
        self.pw.grid(row=1, column=1)
        un_label.grid(row=0, column=0)
        pw_label.grid(row=1, column=0)

        b = ttk.Button(self.win, text="Okay", command=check)
        b.grid(row=2, column=0)

    def hide(self):
        self.master.withdraw()

    def show(self):
        self.master.update()
        self.master.deiconify()

    def send_mail(self, recipients):
        if self.message and self.valid_email:
            print("sending this with email: ", self.message)

            mailer = Mailer.Mailer(self.message, recipients)
            mailer.send_mail()
            del mailer

    def add_mail(self):
        def check():
            email_input = self.add_email_address.get()
            if email_input and validate_email(email_input):
                setattr(self, 'add_new_email', email_input)
                ch = ConfigHandler.ConfigHandler()
                ch.store_contact(self.add_new_email)
                self.recipient.destroy()

        setattr(self, 'recipient', tk.Toplevel(width=100, height=100))
        self.recipient.wm_title("Email recipient")

        setattr(self, 'add_email_address', tk.Entry(self.recipient))
        recipient_label = tk.Label(self.recipient, text="Email address")

        self.add_email_address.grid(row=0, column=1)
        recipient_label.grid(row=0, column=0)

        b = ttk.Button(self.recipient, text="Okay", command=check)
        b.grid(row=1, column=0)

    def open_file(self):
        try:
            file = askopenfilename(parent=self.master)

            os.makedirs(f"{sys.path[0]}/ebooks", exist_ok=True)
            if not os.path.isfile(f"{sys.path[0]}/ebooks/{Path(file).stem}.epub"):
                copy(file, f"{sys.path[0]}/ebooks")

            new_file = f"{Path(file).stem}.txt"

            if not os.path.isdir(f"{sys.path[0]}/ebook_text"):
                os.mkdir(f"{sys.path[0]}/ebook_text")

            if not os.path.isfile(f"{sys.path[0]}/ebook_text/{new_file}"):
                print("Reading epub to text..")
                book = open_book(file)

                lines = convert_epub_to_lines(book)
                with open(f"{sys.path[0]}/ebook_text/{new_file}", 'w', encoding='utf-8') as f:
                    for line in lines:
                        f.writelines(" ".join(re.split(', |_|\.|\?|;|,|:|-|!|\+|\.\.\.|–|”|…|\(|\)',
                                                       (BeautifulSoup(line, 'html.parser').text.lower() + "\r\n"))))
                print("Done..")
            else:
                print(f"Text file found.")

            with open(f"{sys.path[0]}/ebook_text/{new_file}", 'r', encoding='utf-8') as p:
                print("Generating word list..")
                text = p.read()
                words = sorted(set(text.split()))

                setattr(self, 'word_list', words)
                print("Done..")
        except FileNotFoundError as file_not_found:
            tk.messagebox.showwarning(title="Warning", message=file_not_found)
        except Exception as error:
            tk.messagebox.showerror(title="Unknown Error", message=error)

    def get_input(self):
        setattr(self, 'message', [])
        self.result_box.delete(1.0, tk.END)
        setattr(self, 'input', self.text_box.get("1.0", "end").lower().split())
        self.result_box.insert("1.0", self.translate())

    def translate(self):
        print(self.input)
        print(self.checkCmd.get())
        if self.input:
            for word in self.input:
                try:
                    if self.checkCmd.get() == 1:
                        self.message.append(str(self.word_list[int(word)]))
                    else:
                        self.message.append(str(self.word_list.index(word)))
                except ValueError:
                    self.message.append(word)
        return self.message

    def text_box(self):
        setattr(self, 'text_box', tk.Text(self.scrollable_frame, relief=tk.RAISED, bd=3))
        self.text_box.grid(row=0, column=1, sticky="ewns")

    def result_box(self):
        setattr(self, 'result_box', tk.Text(self.scrollable_frame, state="normal", relief=tk.RAISED, bd=3))
        self.result_box.grid(row=0, column=2, sticky="ewns")

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.master.destroy()
