from multiprocessing import freeze_support
import tkinter as tk
from app import App

def main():
    root = tk.Tk()
    root.title('Highlighter')
    root.resizable(False, False) 
    highlight_app = App(root)
    root.mainloop()

if __name__ == '__main__':
    freeze_support
    main()