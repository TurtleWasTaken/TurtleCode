from tkinter import *
import scripts.version as version
import scripts.conversions as conversions
import json


class TurtleCode:

    def __init__(self):

        # Files
        with open("config.json") as s:
            self.config = json.load(s)
        with open(self.config["default_lang_path"]) as s:
            self.lang = json.load(s)

        # Variable declaration START
        self.file_text = ""
        self.default_font = (self.config["default_font"], self.config["default_font_size"])

        self.version_num = int(version.get_version_num())

        self.window = Tk()
        self.main_text_box = Text(self.window, font=self.default_font)
        self.autofill_listbox = Listbox(self.window)
        # Variable declaration END

        self.window_setup()
        self.bindings()
        self.pack_widgets()
        self.window.mainloop()

    def window_setup(self):

        self.window.config(bg=self.config["window"]["bg_col"])
        self.window.geometry(self.config["window"]["size"])
        self.window.title(self.config["window"]["title"].replace("{VERSION}", str(self.version_num)))

    def pack_widgets(self):

        self.main_text_box.pack(expand=1, fill=BOTH)
        self.autofill_listbox.pack(side=RIGHT, expand=1, fill=Y)

    def bindings(self):

        self.main_text_box.bind("<KeyRelease>", self.text_callback)

    def text_callback(self, event):
        self.file_text = self.main_text_box.get("1.0", END)

        for tag in self.main_text_box.tag_names():
            self.main_text_box.tag_delete(tag)

        self.set_tags()
        self.set_autofill()

    def set_autofill(self):
        print(self.get_autofill("te"))

    def set_tags(self):

        split_lines = self.file_text.split("\n")
        for line_num in range(len(split_lines)):
            word_split = split_lines[line_num].split()
            for word_num in range(len(word_split)):
                start_ind = conversions.wordNum_charIndex(split_lines[line_num], word_num)
                start = f"{str(line_num + 1)}.{start_ind}"
                end = f"{str(line_num + 1)}.{start_ind + len(word_split[word_num]) + 1}"
                syntax = self.get_word_syntax(word_split[word_num])
                col = syntax["col"]
                style = syntax["style"]

                if style is not None:
                    font = (self.config["default_font"], self.config["default_font_size"], style)
                else:
                    font = self.default_font
                self.main_text_box.tag_add(word_split[word_num] + start, start, end)
                self.main_text_box.tag_config(word_split[word_num] + start, foreground=col, font=font)

    def get_word_syntax(self, word: str):

        for syntax_word in self.lang["syntax_highlighting"]:
            if syntax_word["word"] == word:
                return syntax_word
        return {"col": self.config["default_word_col"], "style": None}

    def get_autofill(self, word):

        out = []

        for auto_word in self.lang["autofill"]:
            if word in auto_word:
                out.append(auto_word)
        return out


t = TurtleCode()
