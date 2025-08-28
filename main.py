import tkinter as tk
import gui

def main():
    root = tk.Tk()
    root.withdraw()
    gui.load_all_icons()
    gui.create_intro_window(root)
    root.mainloop()

if __name__ == "__main__":
    main()
