import sys
import tkinter as tk
from pathlib import Path

from gitbloom.ui.main_window import GitBloomWindow


def main():
    root = tk.Tk()
    project_root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
    icon_path = project_root / "packaging" / "icons" / "GitBloom.png"
    if icon_path.exists():
        try:
            root._gitbloom_icon = tk.PhotoImage(file=str(icon_path))
            root.iconphoto(True, root._gitbloom_icon)
        except tk.TclError:
            pass
    GitBloomWindow(root)
    root.mainloop()
