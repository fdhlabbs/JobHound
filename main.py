# main.py
import tkinter as tk
import controller as c

def main():
    root = tk.Tk()
    app = c.AppController(root)
    root.mainloop()

#Only run main() if this file is executed directly, NOT if it is imported by another file.”
if __name__ == "__main__":
    main()


