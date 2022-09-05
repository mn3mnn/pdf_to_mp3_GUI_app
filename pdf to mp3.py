import tkinter
import tkinter.messagebox
from tkinter import filedialog
import customtkinter
import PyPDF2
import os
import pyttsx3
import threading

customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("green")  # Themes: "blue" (standard), "green", "dark-blue"


class App(customtkinter.CTk):
    WIDTH = 780
    HEIGHT = 520

    def __init__(self):
        super().__init__()
        self.filename = ""
        self.title("PDF to mp3")
        self.geometry(f"{App.WIDTH}x{App.HEIGHT}")
        # self.minsize(App.WIDTH, App.HEIGHT)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)  # call .on_closing() when app gets closed

        # ============ create two frames ============

        # configure grid layout (2x1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame_left = customtkinter.CTkFrame(master=self,
                                                 width=180,
                                                 corner_radius=0)
        self.frame_left.grid(row=0, column=0, sticky="nswe")

        self.frame_right = customtkinter.CTkFrame(master=self)
        self.frame_right.grid(row=0, column=1, sticky="nswe", padx=20, pady=20)

        # ============ frame_left ============

        # configure grid layout (1x11)
        self.frame_left.grid_rowconfigure(0, minsize=10)  # empty row with minsize as spacing
        self.frame_left.grid_rowconfigure(5, weight=1)  # empty row as spacing
        self.frame_left.grid_rowconfigure(8, minsize=20)  # empty row with minsize as spacing
        self.frame_left.grid_rowconfigure(11, minsize=10)  # empty row with minsize as spacing

        self.label_1 = customtkinter.CTkLabel(master=self.frame_left,
                                              text="Options",
                                              text_font=("Roboto Medium", -16))  # font name and size in px
        self.label_1.grid(row=1, column=0, pady=10, padx=10)

        self.button_1 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Load PDF",
                                                fg_color=("gray75", "gray30"),  # <- custom tuple-color
                                                command=lambda: threading.Thread(target=self.browse_files,
                                                                                 daemon=True).start())
        self.button_1.grid(row=2, column=0, pady=10, padx=20)

        self.button_2 = customtkinter.CTkButton(master=self.frame_left,
                                                text="Save as mp3",
                                                fg_color=("gray75", "#0D8A66"),  # <- custom tuple-color
                                                command=lambda: threading.Thread(target=self.save_mp3,
                                                                                 daemon=True).start())
        self.button_2.grid(row=3, column=0, pady=10, padx=20)

        self.switch_2 = customtkinter.CTkSwitch(master=self.frame_left,
                                                text="Dark Mode",
                                                command=self.change_mode)
        self.switch_2.grid(row=10, column=0, pady=10, padx=20, sticky="w")

        # ============ frame_right ============

        # configure grid layout (3x7)
        self.frame_right.rowconfigure((0, 1, 2, 3), weight=1)
        self.frame_right.rowconfigure(7, weight=10)
        self.frame_right.columnconfigure((0, 1), weight=1)
        self.frame_right.columnconfigure(2, weight=0)

        self.frame_info = customtkinter.CTkFrame(master=self.frame_right)
        self.frame_info.grid(row=0, column=0, columnspan=2, rowspan=4, pady=20, padx=20, sticky="nsew")

        # ============ frame_info ============

        # configure grid layout (1x1)
        self.frame_info.rowconfigure(0, weight=1)
        self.frame_info.columnconfigure(0, weight=1)

        self.label_info_1 = customtkinter.CTkLabel(master=self.frame_info,
                                                   text="\n1 - load a pdf\n\n" +
                                                        "2 - choose male or female sound\n\n" +
                                                        "3 - read pdf or save as mp3\n",
                                                   height=100,
                                                   text_font=("Roboto Medium", -14),
                                                   fg_color=("gray87", "gray38"),  # <- custom tuple-color
                                                   justify=tkinter.LEFT,
                                                   corner_radius=10)
        self.label_info_1.grid(column=0, row=0, sticky="nwe", padx=15, pady=15)

        self.label_info_2 = customtkinter.CTkLabel(master=self.frame_info,
                                                   text="Load a pdf to show info",
                                                   text_color=("#0DAA66", "#0DAF66"),
                                                   height=100,
                                                   text_font=("Roboto Medium", -14),
                                                   fg_color=("gray87", "gray38"),  # <- custom tuple-color
                                                   justify=tkinter.LEFT,
                                                   corner_radius=10)
        self.label_info_2.grid(column=0, row=1, sticky="nwe", padx=15, pady=15)

        # ============ frame_right ============

        self.radio_var = tkinter.IntVar(value=0)

        self.label_radio_group = customtkinter.CTkLabel(master=self.frame_right,
                                                        text="Select sound:")
        self.label_radio_group.grid(row=0, column=2, columnspan=1, pady=20, padx=10, sticky="")

        self.radio_button_1 = customtkinter.CTkRadioButton(master=self.frame_right,
                                                           variable=self.radio_var,
                                                           value=0, text=" Male ")
        self.radio_button_1.grid(row=1, column=2, pady=10, padx=30, sticky="n")

        self.radio_button_2 = customtkinter.CTkRadioButton(master=self.frame_right,
                                                           variable=self.radio_var,
                                                           value=1, text="Female")
        self.radio_button_2.grid(row=2, column=2, pady=10, padx=20, sticky="n")

        self.checkbox_button_1 = customtkinter.CTkButton(master=self.frame_right,
                                                         height=25,
                                                         text="Read pdf",
                                                         border_width=0,  # <- custom border_width
                                                         fg_color=("gray75", "#0D8A66"),  # <- no fg_color
                                                         command=lambda: threading.Thread(target=self.read_file,
                                                                                          daemon=True).start())
        self.checkbox_button_1.grid(row=6, column=2, columnspan=1, pady=10, padx=20, sticky="we")

        # set default values
        self.radio_button_1.select()
        self.switch_2.select()

        # init speaker options
        self.speaker = pyttsx3.init()
        self.voices = self.speaker.getProperty('voices')
        rate = self.speaker.getProperty('rate')
        self.speaker.setProperty('rate', rate - 50)
        self.is_speaking = False

        # init reader options
        self.cleaned_text = ""
        self.pdfreader = PyPDF2.PdfFileReader

    def change_mode(self):
        if self.switch_2.get() == 1:
            customtkinter.set_appearance_mode("dark")
        else:
            customtkinter.set_appearance_mode("light")

    def on_closing(self, event=0):
        self.destroy()

    def start(self):
        self.mainloop()

    def browse_files(self):
        self.filename = filedialog.askopenfilename(initialdir='/', title="Select PDF file",
                                                   filetypes=(("PDF files", "*.pdf*"), ("All files", "*.*")))
        if self.filename:
            self.pdfreader = PyPDF2.PdfFileReader(open(self.filename, 'rb'))
            # load text
            self.cleaned_text = ""
            for i in range(self.pdfreader.getNumPages()):
                text = self.pdfreader.pages[i].extractText()
                self.cleaned_text += text
            self.label_info_2.configure(text="\nOpened:  " + self.filename[self.filename.rfind('/') + 1:]
                                             + "\nnumber of pages:  " + str(self.pdfreader.getNumPages()))

    def read_file(self):
        if self.filename and not self.is_speaking:
            # get speaker gender
            self.speaker.setProperty('voice', self.voices[self.radio_var.get()].id)
            self.speaker.say(self.cleaned_text)
            self.label_info_2.configure(text="Reading " + self.filename[self.filename.rfind('/') + 1:])
            self.is_speaking = True
            self.speaker.runAndWait()

            self.speaker.stop()
            self.label_info_2.configure(text="\nOpened:  " + self.filename[self.filename.rfind('/') + 1:]
                                             + "\nnumber of pages:  " + str(self.pdfreader.getNumPages()))
            self.is_speaking = False

    def save_mp3(self):
        if self.filename:
            mp3filename = tkinter.filedialog.asksaveasfilename(filetypes=((".mp3", "*.mp3"), ("all files", "*.*")),
                                                               defaultextension=".mp3",
                                                               initialdir="/")
            if mp3filename:
                self.speaker.save_to_file(text=self.cleaned_text, filename=mp3filename, name="saving")
                self.speaker.runAndWait()
                self.speaker.stop()
                self.label_info_2.configure(text="Saving " + self.filename[self.filename.rfind('/') + 1:] + "as mp3")

                if mp3filename[mp3filename.rfind('/') + 1:] in os.listdir(mp3filename[0:mp3filename.rfind('/')]):
                    self.label_info_2.configure(text="File saved successfully.")


if __name__ == "__main__":
    app = App()
    app.start()

