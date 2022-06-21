import tkinter as tk
import time
from highlighter import Highlight_Set, Highlighter
from collections import defaultdict
from multiprocessing import Pool, freeze_support, Process
import threading

class App(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        self.master = master
        self.highlight_sets = []
        self.strings_frame = tk.Frame(self.master)
        strings = Strings(self.strings_frame)
        self.highlight_sets.append(strings)
        self.load_widgets()

        self.docs_path_frame = tk.Frame(self.master)
        self.docs_path_frame.grid(row=5, columnspan=2)
        self.docs_path_label = tk.Label(self.docs_path_frame, text='Documents Path')
        self.docs_path_label.grid(row=0, column=0)
        self.docs_path_entry = tk.Entry(self.docs_path_frame, width=40)
        self.docs_path_entry.grid(row=0, column=1, pady=25)

        self.status_frame = tk.Frame(self.master)
        self.status_frame.grid(row=7)
        self.status_text = tk.Label(self.status_frame, text='Processing...')

        

    def load_widgets(self):
        self.string_sets = defaultdict(dict)
        self.set_row = 1

        self.buttons_frame = tk.Frame(self.master)
        self.buttons_frame.grid(row=2, columnspan=2, pady=4)

        self.add_set_btn = tk.Button(self.buttons_frame, text='+', command=self.add_set_box)
        self.add_set_btn.grid(row=0, column=0, padx=15)
        
        self.remove_set_btn = tk.Button(self.buttons_frame, text='-', state=tk.DISABLED, command=self.remove_set_box)
        if len(self.highlight_sets) < 2:
            self.remove_set_btn.config(state=tk.DISABLED)
        else:
            self.remove_set_btn.config(state=tk.NORMAL)

        self.remove_set_btn.grid(row=0, column=1, padx=15)
        self.center_frame = tk.Frame(self.master)
        self.center_frame.grid()
        
        self.strings_frame.grid()
        self.load_highlight_sets()


        self.action_frame = tk.Frame(self.master)
        self.action_frame.grid(row=6, pady=10)
        self.run_btn = tk.Button(self.action_frame, text='Run', command=self.run)
        self.run_btn.grid()


    def add_set_box(self):
        if len(self.highlight_sets) < 3:
            self.highlight_sets.append(Strings(self.strings_frame))

        
        for widget in self.master.children.values():
            widget.forget()

        self.load_widgets()
        if len(self.highlight_sets) == 3:
            self.add_set_btn.config(state=tk.DISABLED)

    def remove_set_box(self):
        remove_set = self.highlight_sets[-1]
        remove_set.label.destroy()
        remove_set.input.destroy()
        remove_set.color.destroy()
        for button in remove_set.buttons:
            button.destroy()
        remove_set.set_box.destroy()

        self.highlight_sets.pop(-1)

        for widget in self.master.children.values():
            widget.forget()

        self.load_widgets()


    def load_highlight_sets(self):
        for set in self.highlight_sets:
            set.load()

    
    def run(self):
        docs_path = self.docs_path_entry.get()
        highlight_fields = []
        for set in self.highlight_sets:
            strings_path = set.input.get()
            color = set.color_value.get()
            if set.parse_value.get() != 1:
                highlight_fields.append(Highlight_Set(strings_path, color, parse=False))
            else:
                highlight_fields.append(Highlight_Set(strings_path, color))
            
        highlighter = Highlighter(highlight_fields, docs_path)

        thread = threading.Thread(target=highlighter.run_highlighter)
        thread.start()
        self.status_text.grid()
        thread.join()
        self.status_text.config(text='Done!')

            
        
class Strings:
    def __init__(self, master):
        self.master = master
        self.set_box = tk.Frame(self.master, highlightbackground="yellow", highlightthickness=2, relief=tk.RIDGE)
        self.body = tk.Frame(self.set_box, height=75, width=350)
        self.color_options = ['Yellow', 'Green', 'Blue', 'Red', 'Redact']
        self.color_value = tk.StringVar(self.set_box)
        self.color_value.set('Yellow')  

        self.label = tk.Label(self.body, text='Strings')
        self.input = tk.Entry(self.body, width=40)
        self.color = tk.OptionMenu(self.body, self.color_value, *self.color_options, command=self.change_color)

        self.parse_value = tk.IntVar(self.body, 1)
        self.parse_options = {'Boolean': 1, 'Regex': 2}

    def change_color(self, *args):
        if self.color_value.get() != 'Redact':
            self.set_box.config(highlightbackground=self.color_value.get().lower())
        else:
            self.set_box.config(highlightbackground='black')

    def load(self):
        self.set_box.grid(pady=5, padx=5)
        self.body.grid(row=0, pady=2, padx=2)
        self.label.grid(row=0, column=0)
        self.color.grid(row=0, column=2)
        self.input.grid(row=0, column=1)
        self.input.update()
        self.buttons_frame = tk.Frame(self.body)
        self.buttons = []
        
        for (key, value) in self.parse_options.items():
            self.buttons.append(tk.Radiobutton(self.buttons_frame, text = key, variable = self.parse_value, value=value))
        
        self.buttons_frame.grid(row=1, columnspan=2, pady=2)
        
        for index, button in enumerate(self.buttons):
            button.grid(row=0, column=index)


