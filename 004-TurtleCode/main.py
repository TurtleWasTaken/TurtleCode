import os
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import simpledialog
from tkinter import messagebox
from tkinter import font
import scripts.version as version
import scripts.conversions as conversions
import json
from functools import partial


class modded_window(Tk):

    def __init__(self, *args):
        super(modded_window, self).__init__(*args)

    def quit(self):
        if messagebox.askyesno("?", "Are you sure you want to quit?"):
            self.tk.quit()

    def destroy(self):
        if messagebox.askyesno("?", "Are you sure you want to quit?"):
            self.tk.quit()


class TurtleCode:

    def __init__(self):

        # Files
        with open("config.json") as s:
            self.config = json.load(s)
        with open("files/styles.json") as s:
            self.style = json.load(s)[self.config["default_style"]]
        self.sel_language(self.config["default_lang"])

        # Variable declaration START

        self.file_path = None
        self.project_path = None

        self.file_text = ""
        self.current_indent = 0
        self.needs_saving = False
        self.default_font = (self.config["default_font"], self.config["default_font_size"])

        self.version_num = int(version.get_version_num())

        self.window = modded_window()

        self.text_box_scrollbar = Scrollbar(self.window)

        self.main_text_box = Text(self.window, font=self.default_font, yscrollcommand=self.text_box_scrollbar.set, bg=self.style["fir_bg_col"])
        self.main_text_box_height = None

        self.text_box_scrollbar.config(command=self.custom_scroll_bind)

        self.autofill_size_frame = Frame(self.window, width=self.config["autofill"]["default_box_width"])
        self.autofill_listbox = Listbox(self.autofill_size_frame, bg=self.style["sec_bg_col"])
        self.autofill_width = self.config["autofill"]["default_box_width"]

        self.menu_bar = Menu(self.window)
        self.edit_menu = Menu(self.menu_bar, tearoff=0)
        self.file_menu = Menu(self.menu_bar, tearoff=0)
        self.run_menu = Menu(self.menu_bar, tearoff=0)
        self.language_menu = Menu(self.menu_bar, tearoff=0)
        self.language_options = Menu(self.language_menu, tearoff=0)

        self.status_bar_value = StringVar()
        self.status_bar = Label(self.window, textvariable=self.status_bar_value, font=self.default_font, relief=SUNKEN, anchor=W)

        # You can tell why I hate ttk. It doesnt even work. I give up.
        style = ttk.Style()
        style.configure("Treeview", foreground = 'maroon', fieldbackground="#383838", background="#383838")
        self.project_tree_frame = Frame(self.window, width=self.config["project_view"]["default_box_width"])
        self.project_tree = ttk.Treeview(self.project_tree_frame, style="Treeview")
        self.project_tree_drag_anchor = (0,0)
        self.project_tree_width = self.config["project_view"]["default_box_width"]
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
        self.file_menu.add_command(label="Open folder as project", command=self.MENU_open_project)
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
        self.run_menu.add_command(label="Compile Script", state=DISABLED)
        self.run_menu.add_command(label="Configure run settings", command=self.MENU_config_run, state=DISABLED)

        self.menu_bar.add_cascade(label="Run", menu=self.run_menu)

    def pack_widgets(self):

        self.status_bar.pack(side=BOTTOM, fill=X)
        self.project_tree_frame.pack(side=LEFT, fill=Y)
        self.project_tree.pack(side=LEFT, fill=BOTH, expand=1)
        self.project_tree_frame.pack_propagate(False)
        self.autofill_listbox.pack(side=RIGHT, fill=BOTH, expand=1)
        self.autofill_size_frame.pack(side=RIGHT, fill=Y)
        self.autofill_size_frame.pack_propagate(False)

        self.text_box_scrollbar.pack(side=RIGHT, fill=Y)
        self.main_text_box.pack(expand=1, fill=BOTH)

    def bindings(self):

        self.window.bind("<Motion>", self.update_status_bar)
        self.window.bind("<KeyRelease>", self.update_status_bar)

        self.main_text_box.bind("<KeyRelease>", self.text_callback)
        self.main_text_box.bind("<Shift-Tab>", self.autofill_callback)
        self.main_text_box.bind("<Configure>", self.on_text_configure)

        self.project_tree.bind("<B1-Motion>", self.project_view_drag)
        self.project_tree.bind("<Double-1>", self.project_tree_sel)
        self.autofill_listbox.bind("<B1-Motion>", self.autofill_drag)
                        
        # Key binds
        self.window.bind("<Control-s>", self.MENU_save_file)
        self.window.bind("<Control-o>", self.MENU_open_file)
        self.window.bind("<Shift-Control-S>", self.MENU_saveas_file)
        self.window.bind("<Control-Shift-O>", self.MENU_open_project)
        self.window.bind("<Control-r>", self.MENU_run_script)
                        

    def custom_scroll_bind(self, *args):

        if self.config["set_tags_with_scroll"]:
            self.set_tags("mouse")
        self.main_text_box.yview(*args)

    def text_callback(self, event):
        print(event)
        self.needs_saving = True
        self.update_window_title()
        if event.char == "\t":
            cursor = self.main_text_box.index(INSERT).split(".")
            pos = cursor[0] + "." + str(int(cursor[1])-1)
            self.main_text_box.delete(pos)
            self.main_text_box.insert(INSERT, "    ")
        self.file_text = self.main_text_box.get("1.0", END)

        self.autofill_listbox.delete(0, END)

        self.set_tags("section")
        self.set_autofill()
        #self.set_auto_indent(event.char, event.keysym)

    def set_auto_indent(self, keysym):
        
        if keysym == "Return":
            self.main_text_box.insert(INSERT, "    "*self.current_indent)
        elif keysym == "Tab":
            self.current_indent += 1
        elif keysym == "BackSpace":
            print("BACKSPACE")

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

    def set_tags(self, flag):

        if flag == "all":
            search_start = 0
            search_end = len(self.file_text.split("\n"))
        elif flag == "section":
            line_num = int(self.main_text_box.index(INSERT).split(".")[0])-1
            search_start = max(0, line_num-self.main_text_box_height)
            search_end = min(len(self.file_text.split("\n"))-2, line_num+self.main_text_box_height)

        elif flag == "mouse":
            line_num = int(self.main_text_box.index(CURRENT).split(".")[0]) - 1
            search_start = max(0, line_num - self.main_text_box_height)
            search_end = min(len(self.file_text.split("\n")) - 2, line_num + self.main_text_box_height)

        else:
            return

        split_lines = self.file_text.split("\n")
                  
        for tag in self.main_text_box.tag_names():
            self.main_text_box.tag_delete(tag)

        for line_num in range(search_start, search_end):
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

        str_start = None
        str_end = None
        for line_num in range(search_start, search_end):
            char_split = list(split_lines[line_num])
            for char_num in range(len(char_split)):
                char = char_split[char_num]
                if "str_chars" not in self.lang:
                    continue
                if char in self.lang.get("str_chars"):
                    if str_start is None:
                        str_start = str(line_num+1)+"."+str(char_num)
                    elif str_end is None and str_start is not None:
                        str_end = str(line_num+1)+"."+str(char_num+1)
                        col = self.style["str_col"]
                        style = self.style["str_style"]
                        if style is not None:
                            font = (self.config["default_font"], self.config["default_font_size"], style)
                        else:
                            font = self.default_font
                        self.main_text_box.tag_add(str_start + str_end, str_start, str_end)
                        self.main_text_box.tag_config(str_start + str_end, foreground=col, font=font)
                        str_start = None
                        str_end = None

        # Single comment search
        if self.lang["single_comment"] == None or self.lang["block_comment_start"] == None or self.lang["block_comment_start"] == None:
            return
        s_comment_positions = conversions.big_search(self.file_text, self.lang["single_comment"])

        for pos in s_comment_positions:
            line_num = conversions.charIndex_lineNum(self.file_text, pos)
            line_start = conversions.lineNum_charIndex(self.file_text, line_num)
            
            start = str(line_num + 1) + "." + str(pos - line_start - line_num-1)
            end = str(line_num + 1) + "." + str(len(self.file_text.split("\n")[line_num]))

            style = self.style["comment_style"]

            if style is not None:
                font = (self.config["default_font"], self.config["default_font_size"], style)
            else:
                font = self.default_font

            self.main_text_box.tag_add("comment" + str(pos), start, end)
            self.main_text_box.tag_config("comment" + str(pos), foreground=self.style["comment_col"], font=font)

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

            style = self.style["comment_style"]

            if style is not None:
                font = (self.config["default_font"], self.config["default_font_size"], style)
            else:
                font = self.default_font

            self.main_text_box.tag_add("comment" + str(start), start_pos, end_pos)
            self.main_text_box.tag_config("comment" + str(start), foreground=self.style["comment_col"], font=font)

    def get_word_syntax(self, word: str):

        for syntax_word in self.lang["syntax_highlighting"]:
            if syntax_word == word:
                return self.style["code_syntax"][self.lang["syntax_highlighting"][syntax_word]]
        return {"col": self.style["base_col"], "style": None}

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
        self.main_text_box.insert(1.0, self.file_text.replace("\t", "    "))
        self.main_text_box.mark_set(INSERT, f"{index[0]}.{str(word_index + len(self.autofill_listbox.get(ACTIVE)))}")

    def on_text_configure(self, event):

        f = font.Font(family=self.default_font[0], size=self.default_font[1])
        height = int(round(event.height / f.metrics("linespace"), 0))
        self.main_text_box_height = height

    def update_status_bar(self, event=None):

        mx = self.window.winfo_pointerx() - self.window.winfo_x()
        my = self.window.winfo_pointery() - self.window.winfo_y()
        index = self.main_text_box.index(INSERT).split(".")
        l = index[0]
        c = index[1]

        value = f"X: {mx} ;; Y: {my} || Line: {l} ;; Col: {c} | Lang: {self.lang['name']}"

        self.status_bar_value.set(value)
    
    def update_window_title(self):
        title = self.config["window"]["title"].replace("{VERSION}", str(self.version_num)).replace("{FILEPATH}", str(self.file_path))
        if self.file_text != open(self.file_path).read():
            title += " *"
        self.window.title(title)

    def autofill_drag(self, event=None):
        x = self.window.winfo_pointerx() - self.window.winfo_x()
        rel_x = x - self.window.winfo_width() + self.autofill_width
        width = self.window.winfo_width() - x
        if -10 < rel_x < 10:
            self.autofill_width = width
            print(self.autofill_width)
            self.autofill_size_frame.config(width=self.autofill_width)

    def project_view_drag(self, event=None):
        x = self.window.winfo_pointerx() - self.window.winfo_x()
        if self.project_tree_width - 10 < x < self.project_tree_width + 15:
            self.project_tree_width = x
            self.project_tree_frame.config(width=self.project_tree_width)

    def map_project_folder(self, path):
        self.project_tree.insert("", iid=path, index=0, text=">:)")
        self.map_folder(path)

    def map_folder(self, folder_path):
        contents = os.listdir(folder_path)

        for file_dir in contents:
            self.project_tree.insert(folder_path, iid=folder_path+"\\"+file_dir, index=END, text=file_dir)
            if os.path.isdir(folder_path+"\\"+file_dir):
                self.map_folder(folder_path+"\\"+file_dir)

    def project_tree_sel(self, event=None):
        item = self.project_tree.focus()
        if item != "":
            if os.path.isfile(item):
                self.file_path = item
                self.load_file(item)

    def clear_file(self):
        self.file_text = ""
        self.main_text_box.delete(1.0, END)

    def load_file(self, path):

        file = open(path)
        self.file_text = file.read()

        self.main_text_box.delete(1.0, END)
        self.main_text_box.insert(1.0, self.file_text.replace("\t", "    "))
        self.main_text_box.mark_set(INSERT, "1.0")

        # Getting language
        split = self.file_text.split("\n")
        if "TC LANG" in split[0]:
            try:
                self.sel_language([0].split()[2])
                self.set_tags("all")
                return
            except FileNotFoundError:
                self.sel_language(self.config["default_lang"])
                self.set_tags("all")
                return
        else:
            if "." in path:
                file_extension = path.split(".")[len(path.split(".")) - 1]
                for lang in os.listdir("files/languages/"):
                    if ".json" in lang:
                        j = json.load(open("files/languages/" + lang))
                        if file_extension in j["default_file_extensions"]:
                            self.sel_language(lang)
                            self.set_tags("all")
                            return
                self.sel_language(self.config["default_lang"])
                self.set_tags("all")
                return

    def save_file(self, path):
        self.needs_saving = False
        self.update_window_title()
        file = open(path, "w+")
        file.write(self.file_text)
        file.close()

    def sel_language(self, lang_name):
        with open("files/languages/" + lang_name) as s:
            self.lang = json.load(s)

    def MENU_select_language(self, lang_name, event=None):
        self.sel_language(lang_name)

    def MENU_new(self, event=None):
        self.clear_file()

    def MENU_open_file(self, event=None):
        filepath = filedialog.askopenfilename()
        self.file_path = filepath
        self.load_file(filepath)

    def MENU_open_project(self, event=None):
        filepath = filedialog.askdirectory()
        self.clear_file()
        self.map_project_folder(filepath)
        self.project_path = filepath

    def MENU_save_file(self, event=None):
        if self.file_path is None:
            self.MENU_saveas_file()
        else:
            self.save_file(self.file_path)

    def MENU_saveas_file(self, event=None):
        filepath = filedialog.asksaveasfilename()
        if os.is_file(filepath):
            self.file_path = filepath
            self.save_file(filepath)
        else:
            open(filepath, "x").close()
            self.file_path = filepath
            self.save_file(filepath)

    def MENU_config_run(self, event=None):
        simpledialog.askstring("Run system command", "Enter a command for the system to run.")

    def MENU_run_script(self, event=None):

        if self.lang["default_run_command"] is not None:
            command = self.lang["default_run_command"].replace("{FILEPATH}",
                                                               conversions.format_file_path(self.file_path))
            os.system(command)


try:
    t = TurtleCode()
except Exception as E:
    messagebox.showerror("Oh no! A fatal error occurred!", str(E))



