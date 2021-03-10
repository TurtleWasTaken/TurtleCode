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
        self.autofill_drag_anchor = None

        self.file_text = ""
        self.default_font = (self.config["default_font"], self.config["default_font_size"])

        self.version_num = int(version.get_version_num())

        self.window = Tk()
        self.main_text_box = Text(self.window, font=self.default_font)
        self.autofill_size_frame = Frame(self.window, width=self.window.winfo_width() / 8, bg="#000000")
        self.autofill_listbox = Listbox(self.window, width=self.config["autofill"]["default_box_width"],
                                        bg=self.config["autofill"]["bg_col"])

        self.menu_bar = Menu(self.window)

        self.file_menu = Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="New")
        self.file_menu.add_command(label="Open")
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Save")
        self.file_menu.add_command(label="Save As")
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.window.quit)

        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        self.edit_menu = Menu(self.menu_bar, tearoff=0)
        self.edit_menu.add_command(label="Undo")
        self.edit_menu.add_command(label="Redo")
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Cut")
        self.edit_menu.add_command(label="Copy")
        self.edit_menu.add_command(label="Paste")
        self.edit_menu.add_command(label="Delete")
        self.edit_menu.add_command(label="Select all")
        self.edit_menu.add_separator()

        self.edit__clipboard_menu = Menu(self.edit_menu, tearoff=0)
        self.edit__clipboard_menu.add_command(label="Copy full file path")
        self.edit__clipboard_menu.add_command(label="Copy directory name")
        self.edit__clipboard_menu.add_command(label="Copy file name")

        self.edit_menu.add_cascade(label="Clipboard Functions", menu=self.edit__clipboard_menu)

        self.edit__indent_menu = Menu(self.edit_menu, tearoff=0)
        self.edit__indent_menu.add_command(label="Increase selection indent")
        self.edit__indent_menu.add_command(label="Decrease selection indent")

        self.edit_menu.add_cascade(label="Indent Functions", menu=self.edit__indent_menu)

        self.edit__case_menu = Menu(self.edit_menu, tearoff=0)
        self.edit__case_menu.add_command(label="Convert to UPPERCASE")
        self.edit__case_menu.add_command(label="Convert to lowercase")
        self.edit__case_menu.add_command(label="Convert to Proper Case")
        self.edit__case_menu.add_command(label="Convert to Sentence case")
        self.edit__case_menu.add_command(label="Convert to iNVERTED cASE")
        self.edit__case_menu.add_command(label="Convert to rANdOM caSe")

        self.edit_menu.add_cascade(label="Case Functions", menu=self.edit__case_menu)

        self.edit__comment_menu = Menu(self.edit_menu, tearoff=0)
        self.edit__comment_menu.add_command(label="Single line comment")
        self.edit__comment_menu.add_command(label="Single line uncomment")
        self.edit__comment_menu.add_command(label="Block comment")
        self.edit__comment_menu.add_command(label="Block uncomment")

        self.edit_menu.add_cascade(label="Comment Functions", menu=self.edit__comment_menu)

        self.menu_bar.add_cascade(label="Edit", menu=self.edit_menu)

        # Variable declaration END

        self.window_setup()
        self.bindings()
        self.pack_widgets()
        self.window.mainloop()

    def window_setup(self):

        self.window.config(bg=self.config["window"]["bg_col"], menu=self.menu_bar)
        self.window.geometry(self.config["window"]["size"])
        self.window.title(self.config["window"]["title"].replace("{VERSION}", str(self.version_num)))

    def pack_widgets(self):

        self.autofill_listbox.pack(side=RIGHT, fill=Y)
        self.main_text_box.pack(expand=1, fill=BOTH)

    def bindings(self):

        self.main_text_box.bind("<KeyRelease>", self.text_callback)
        self.main_text_box.bind("<Shift-Tab>", self.autofill_callback)

    def text_callback(self, event):
        self.file_text = self.main_text_box.get("1.0", END)

        self.autofill_listbox.delete(0, END)

        self.set_tags()
        self.set_autofill()

    def set_autofill(self):
        index = self.main_text_box.index(INSERT).split(".")
        current_word = conversions.big_split(self.file_text.split("\n")[int(index[0]) - 1], self.config["word_separators"])[
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
            start = str(line_num+1)+"."+str(pos-line_start-line_num)
            end = str(line_num+1)+"."+str(len(self.file_text.split("\n")[line_num]))

            style = self.lang["single_comment_style"]

            if style is not None:
                font = (self.config["default_font"], self.config["default_font_size"], style)
            else:
                font = self.default_font

            self.main_text_box.tag_add("comment"+str(pos), start, end)
            self.main_text_box.tag_config("comment"+str(pos), foreground=self.lang["single_comment_col"], font=font)

        # Block comment search
        b_comment_start_positions = conversions.big_search(self.file_text, self.lang["block_comment_start"])
        b_comment_end_positions = conversions.big_search(self.file_text, self.lang["block_comment_end"])

        for start in b_comment_start_positions:
            lowest = len(self.file_text)+1

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
        current_word = conversions.big_split(self.file_text.split("\n")[int(index[0]) - 1], self.config["word_separators"])[
            conversions.charIndex_wordNum(self.file_text.split("\n")[int(index[0]) - 1], int(index[1]),
                                          self.config["word_separators"])
        ]

        word_index = int(index[1]) - len(current_word)
        split = self.file_text.split("\n")
        split[int(index[0]) - 1] = conversions.replace_string_at(self.file_text.split("\n")[int(index[0]) - 1],
                                                                 word_index, word_index + len(current_word),
                                                                 self.autofill_listbox.get(ACTIVE))
        self.file_text = "\n".join(split)
        self.file_text = self.file_text[0:len(self.file_text)-1]

        self.main_text_box.delete(1.0, END)
        self.main_text_box.insert(1.0, self.file_text)
        self.main_text_box.mark_set(INSERT, f"{index[0]}.{str(word_index+len(self.autofill_listbox.get(ACTIVE)))}")


t = TurtleCode()
