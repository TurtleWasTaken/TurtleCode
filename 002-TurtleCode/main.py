import os
from tkinter import *
from tkinter import filedialog
from tkinter import simpledialog
import scripts.version as version
import scripts.conversions as conversions
import json
from functools import partial


class TurtleCode:

    def __init__(self):

        # Files
        with open("config.json") as s:
            self.config = json.load(s)
        self.sel_language(self.config["default_lang"])

        # Variable declaration START

        self.file_path = None

        self.file_text = ""
        self.current_indent = 0
        self.default_font = (self.config["default_font"], self.config["default_font_size"])

        self.version_num = int(version.get_version_num())

        self.window = Tk()
        self.main_text_box = Text(self.window, font=self.default_font)
        self.autofill_size_frame = Frame(self.window, width=self.window.winfo_width() / 8, bg="#000000")
        self.autofill_listbox = Listbox(self.window, width=self.config["autofill"]["default_box_width"],
                                        bg=self.config["autofill"]["bg_col"])

        self.menu_bar = Menu(self.window)
        self.file_menu = Menu(self.menu_bar, tearoff=0)
        self.edit_menu = Menu(self.menu_bar, tearoff=0)
        self.run_menu = Menu(self.menu_bar, tearoff=0)
        self.language_menu = Menu(self.menu_bar, tearoff=0)
        self.language_options = Menu(self.language_menu, tearoff=0)

        self.status_bar_value = StringVar()
        self.status_bar = Label(self.window, textvariable=self.status_bar_value, font=self.default_font, relief=SUNKEN,
                                anchor=W)
        # Variable declaration END

        self.window_setup()
        self.menu_bar_setup()
        self.bindings()
        self.pack_widgets()
        self.window.mainloop()

    def window_setup(self):

        self.window.config(bg=self.config["window"]["bg_col"], menu=self.menu_bar)
        self.window.geometry(self.config["window"]["size"])
        self.window.title(self.config["window"]["title"].replace("{VERSION}", str(self.version_num)))

    def menu_bar_setup(self):

        self.file_menu.add_command(label="New", command=self.MENU_new)
        self.file_menu.add_command(label="Open", command=self.MENU_open_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Save", command=self.MENU_save_file)
        self.file_menu.add_command(label="Save As", command=self.MENU_saveas_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.window.quit)

        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        self.edit_menu.add_command(label="Undo", state=DISABLED)
        self.edit_menu.add_command(label="Redo", state=DISABLED)
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Cut", state=DISABLED)
        self.edit_menu.add_command(label="Copy", state=DISABLED)
        self.edit_menu.add_command(label="Paste", state=DISABLED)
        self.edit_menu.add_command(label="Delete", state=DISABLED)
        self.edit_menu.add_command(label="Select all", state=DISABLED)
        self.edit_menu.add_separator()

        self.menu_bar.add_cascade(label="Edit", menu=self.edit_menu)

        self.language_menu.add_command(label="View language info")
        self.language_menu.add_separator()

        for lang in os.listdir("files/languages/"):
            if ".json" in lang:
                j = json.load(open("files/languages/" + lang))
                name = j["name"]
                self.language_options.add_command(label=name, command=partial(self.MENU_select_language, lang))

        self.language_menu.add_cascade(label="Change language", menu=self.language_options)

        self.menu_bar.add_cascade(label="Language", menu=self.language_menu)

        self.run_menu.add_command(label="Run Script", command=self.MENU_run_script)
        self.run_menu.add_command(label="Compile Script")
        self.run_menu.add_command(label="Configure run settings", command=self.MENU_config_run)

        self.menu_bar.add_cascade(label="Run", menu=self.run_menu)

    def pack_widgets(self):

        self.status_bar.pack(side=BOTTOM, fill=X)
        self.autofill_listbox.pack(side=RIGHT, fill=Y)
        self.main_text_box.pack(expand=1, fill=BOTH)

    def bindings(self):

        self.window.bind("<Motion>", self.update_status_bar)
        self.window.bind("<KeyRelease>", self.update_status_bar)

        self.main_text_box.bind("<KeyRelease>", self.text_callback)
        self.main_text_box.bind("<Shift-Tab>", self.autofill_callback)

    def text_callback(self, event):
        self.file_text = self.main_text_box.get("1.0", END)

        self.autofill_listbox.delete(0, END)

        self.set_tags()
        self.set_autofill()
        # self.set_auto_indent()

    # Doesnt work :(
    '''def set_auto_indent(self):
        index = self.main_text_box.index(INSERT).split(".")
        s_index = conversions.lineNum_charIndex(self.file_text, int(index[0]) - 1) + int(index[1])
        last_char = self.file_text[s_index-2]
        if index[1] == "0":
            print(index)
            if last_char in self.lang["indent_chars"]:
                self.current_indent += 1

            self.file_text = conversions.replace_string_at(self.file_text, s_index+2, s_index+2, ("    ")*self.current_indent)

        self.main_text_box.delete(1.0, END)
        self.main_text_box.insert(1.0, self.file_text)
        self.main_text_box.mark_set(INSERT, f"{index[0]}.{str(int(index[1]) + 4)}")'''

    def set_autofill(self):
        index = self.main_text_box.index(INSERT).split(".")
        current_word = \
            conversions.big_split(self.file_text.split("\n")[int(index[0]) - 1], self.config["word_separators"])[
                conversions.charIndex_wordNum(self.file_text.split("\n")[int(index[0]) - 1], int(index[1]),
                                              self.config["word_separators"])
            ]

        autofill_results = self.get_autofill(current_word)
        count = 0
        for result in autofill_results:
            count += 1
            self.autofill_listbox.insert(END, result)

        if count > 0:
            self.autofill_listbox.select_set(0)

    def set_tags(self):

        for tag in self.main_text_box.tag_names():
            self.main_text_box.tag_delete(tag)

        split_lines = self.file_text.split("\n")
        for line_num in range(len(split_lines)):
            word_split = conversions.big_split(split_lines[line_num], self.config["word_separators"])
            for word_num in range(len(word_split)):
                start_ind = conversions.wordNum_charIndex(split_lines[line_num], word_num,
                                                          self.config["word_separators"])
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

        # Single comment search
        s_comment_positions = conversions.big_search(self.file_text, self.lang["single_comment"])

        for pos in s_comment_positions:
            line_num = conversions.charIndex_lineNum(self.file_text, pos)
            line_start = conversions.lineNum_charIndex(self.file_text, line_num)
            start = str(line_num + 1) + "." + str(pos - line_start - line_num)
            end = str(line_num + 1) + "." + str(len(self.file_text.split("\n")[line_num]))

            style = self.lang["single_comment_style"]

            if style is not None:
                font = (self.config["default_font"], self.config["default_font_size"], style)
            else:
                font = self.default_font

            self.main_text_box.tag_add("comment" + str(pos), start, end)
            self.main_text_box.tag_config("comment" + str(pos), foreground=self.lang["single_comment_col"], font=font)

        # Block comment search
        b_comment_start_positions = conversions.big_search(self.file_text, self.lang["block_comment_start"])
        b_comment_end_positions = conversions.big_search(self.file_text, self.lang["block_comment_end"])

        for start in b_comment_start_positions:
            lowest = len(self.file_text) + 1

            for end in b_comment_end_positions:
                difference = end - start

                if difference < lowest:
                    lowest = difference

            line_num = conversions.charIndex_lineNum(self.file_text, start)
            line_start = conversions.lineNum_charIndex(self.file_text, line_num)
            start_pos = str(line_num + 1) + "." + str(start - line_start - line_num)
            line_num = conversions.charIndex_lineNum(self.file_text, lowest)
            line_start = conversions.lineNum_charIndex(self.file_text, line_num)
            end_pos = str(line_num + 1) + "." + str(lowest - line_start - line_num)

            style = self.lang["block_comment_style"]

            if style is not None:
                font = (self.config["default_font"], self.config["default_font_size"], style)
            else:
                font = self.default_font

            self.main_text_box.tag_add("comment" + str(start), start_pos, end_pos)
            self.main_text_box.tag_config("comment" + str(start), foreground=self.lang["block_comment_col"], font=font)

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

    def autofill_callback(self, event):

        if self.autofill_listbox.get(ACTIVE) == "":
            return

        index = self.main_text_box.index(INSERT).split(".")
        current_word = \
            conversions.big_split(self.file_text.split("\n")[int(index[0]) - 1], self.config["word_separators"])[
                conversions.charIndex_wordNum(self.file_text.split("\n")[int(index[0]) - 1], int(index[1]),
                                              self.config["word_separators"])
            ]

        word_index = int(index[1]) - len(current_word)
        split = self.file_text.split("\n")
        split[int(index[0]) - 1] = conversions.replace_string_at(self.file_text.split("\n")[int(index[0]) - 1],
                                                                 word_index, word_index + len(current_word),
                                                                 self.autofill_listbox.get(ACTIVE))
        self.file_text = "\n".join(split)
        self.file_text = self.file_text[0:len(self.file_text) - 1]

        self.main_text_box.delete(1.0, END)
        self.main_text_box.insert(1.0, self.file_text)
        self.main_text_box.mark_set(INSERT, f"{index[0]}.{str(word_index + len(self.autofill_listbox.get(ACTIVE)))}")

    def update_status_bar(self, event=None):

        MX = self.window.winfo_pointerx() - self.window.winfo_x()
        MY = self.window.winfo_pointery() - self.window.winfo_y()
        index = self.main_text_box.index(INSERT).split(".")
        L = index[0]
        C = index[1]

        value = f"X: {MX} ;; Y: {MY} || Line: {L} ;; Col: {C}"

        self.status_bar_value.set(value)

    def clear_file(self):
        self.file_text = ""
        self.main_text_box.delete(1.0, END)

    def load_file(self, path):

        file = open(path)
        self.file_text = file.read()

        self.main_text_box.delete(1.0, END)
        self.main_text_box.insert(1.0, self.file_text)
        self.main_text_box.mark_set(INSERT, "1.0")

        # Getting language
        split = self.file_text.split("\n")
        if "TC LANG" in split[0]:
            try:
                self.sel_language([0].split()[2])
                return
            except FileNotFoundError:
                self.sel_language(self.config["default_lang"])
                return
        else:
            if "." in path:
                file_extension = path.split(".")[len(path.split("."))-1]
                for lang in os.listdir("files/languages/"):
                    if ".json" in lang:
                        j = json.load(open("files/languages/" + lang))
                        if j["default_file_extension"] == file_extension:
                            self.sel_language(lang)
                            return
                self.sel_language(self.config["default_lang"])
                return

    def save_file(self, path):
        file = open(path, "w+")
        file.write(self.file_text)
        file.close()

    def sel_language(self, lang_name):
        with open("files/languages/" + lang_name) as s:
            self.lang = json.load(s)

    def MENU_select_language(self, lang_name):
        self.sel_language(lang_name)

    def MENU_new(self):
        self.clear_file()

    def MENU_open_file(self):
        filepath = filedialog.askopenfilename()
        self.file_path = filepath
        self.load_file(filepath)

    def MENU_save_file(self):
        if self.file_path is None:
            self.MENU_saveas_file()
        else:
            self.save_file(self.file_path)

    def MENU_saveas_file(self):
        filepath = filedialog.asksaveasfilename()
        self.file_path = filepath
        self.save_file(filepath)

    def MENU_config_run(self):
        simpledialog.askstring("Run system command", "Enter a command for the system to run.")

    def MENU_run_script(self):

        if self.lang["default_run_command"] is not None:
            command = self.lang["default_run_command"].replace("{FILEPATH}", conversions.format_file_path(self.file_path))
            os.system(command)


t = TurtleCode()
