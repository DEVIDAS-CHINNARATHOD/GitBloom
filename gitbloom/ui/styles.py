from tkinter import ttk


def configure(root):
    root.configure(bg="#f4f4f4")
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("TFrame", background="#f4f4f4")
    style.configure("Card.TFrame", background="#ffffff")
    style.configure("TLabel", background="#f4f4f4", foreground="#222222", font=("Arial", 10))
    style.configure("Card.TLabel", background="#ffffff", foreground="#333333", font=("Arial", 10))
    style.configure("Title.TLabel", background="#f4f4f4", foreground="#111111", font=("Arial", 22, "bold"))
    style.configure("Subtitle.TLabel", background="#f4f4f4", foreground="#666666", font=("Arial", 10))
    style.configure("CardTitle.TLabel", background="#ffffff", foreground="#222222", font=("Arial", 11, "bold"))
    style.configure("TButton", font=("Arial", 10), padding=(14, 8))
    style.configure("Primary.TButton", font=("Arial", 10, "bold"), padding=(16, 9))
    style.configure("TEntry", padding=7)
    style.configure("TSpinbox", padding=7)
    style.configure("Horizontal.TProgressbar", thickness=8)
