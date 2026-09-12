import os
import threading
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk

from gitbloom.core.files import cleanup, copy_files, copy_folder
from gitbloom.core.git import clone_repository, commit, push
from gitbloom.core.planner import build_plan, collect_files
from gitbloom.ui.styles import configure


class GitBloomWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("GitBloom")
        self.root.geometry("920x700")
        self.root.minsize(780, 620)
        configure(root)
        self.folder = ""
        self.selected_files = []
        self.plan = []
        self.workspace = None
        self.repository = None
        self.show_settings()

    def clear(self):
        for child in self.root.winfo_children():
            child.destroy()

    def header(self, title, subtitle):
        frame = ttk.Frame(self.root, padding=(28, 24, 28, 12))
        frame.pack(fill="x")
        ttk.Label(frame, text=title, style="Title.TLabel").pack(anchor="w")
        ttk.Label(frame, text=subtitle, style="Subtitle.TLabel").pack(anchor="w", pady=(3, 0))

    def card(self, parent):
        frame = ttk.Frame(parent, style="Card.TFrame", padding=18)
        frame.pack(fill="x", pady=(0, 12))
        return frame

    def show_settings(self):
        self.clear()
        self.header("GitBloom", "Create an organized Git commit timeline from your project.")
        body = ttk.Frame(self.root, padding=(28, 0, 28, 28))
        body.pack(fill="both", expand=True)

        repo = self.card(body)
        ttk.Label(repo, text="Remote repository", style="CardTitle.TLabel").pack(anchor="w")
        self.repo_var = tk.StringVar()
        ttk.Entry(repo, textvariable=self.repo_var).pack(fill="x", pady=(10, 0))
        ttk.Label(repo, text="Remote Git repository URL", style="Card.TLabel").pack(anchor="w", pady=(4, 0))

        project = self.card(body)
        ttk.Label(project, text="Project files", style="CardTitle.TLabel").pack(anchor="w")
        row = ttk.Frame(project, style="Card.TFrame")
        row.pack(fill="x", pady=(10, 0))
        self.input_var = tk.StringVar()
        ttk.Entry(row, textvariable=self.input_var, state="readonly").pack(side="left", fill="x", expand=True)
        ttk.Button(row, text="Select folder", command=self.choose_folder).pack(side="left", padx=(10, 0))
        ttk.Button(row, text="Select files", command=self.choose_files).pack(side="left", padx=(8, 0))
        self.file_info = ttk.Label(project, text="Select a folder or one or more files", style="Card.TLabel")
        self.file_info.pack(anchor="w", pady=(8, 0))

        settings = self.card(body)
        ttk.Label(settings, text="Commit settings", style="CardTitle.TLabel").pack(anchor="w")
        fields = ttk.Frame(settings, style="Card.TFrame")
        fields.pack(fill="x", pady=(12, 0))

        start_frame = ttk.Frame(fields, style="Card.TFrame")
        start_frame.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ttk.Label(start_frame, text="Start date", style="Card.TLabel").pack(anchor="w")
        self.start_var = tk.StringVar()
        ttk.Entry(start_frame, textvariable=self.start_var).pack(fill="x", pady=(5, 0))
        ttk.Label(start_frame, text="DD-MM-YYYY", style="Card.TLabel").pack(anchor="w", pady=(3, 0))

        count_frame = ttk.Frame(fields, style="Card.TFrame")
        count_frame.pack(side="left", fill="x", expand=True, padx=8)
        ttk.Label(count_frame, text="Number of commits", style="Card.TLabel").pack(anchor="w")
        self.count_var = tk.IntVar(value=1)
        self.count_spinbox = ttk.Spinbox(
            count_frame,
            from_=1,
            to=999999,
            textvariable=self.count_var,
            command=self.commit_count_changed,
        )
        self.count_spinbox.pack(fill="x", pady=(5, 0))
        self.count_spinbox.bind("<KeyRelease>", lambda event: self.commit_count_changed())
        self.count_spinbox.bind("<FocusOut>", lambda event: self.commit_count_changed())
        ttk.Label(
            count_frame,
            text="Automatically set to the number of selected files; editable.",
            style="Card.TLabel",
        ).pack(anchor="w", pady=(3, 0))

        timeline = ttk.Frame(settings, style="Card.TFrame")
        timeline.pack(fill="x", pady=(16, 0))
        top = ttk.Frame(timeline, style="Card.TFrame")
        top.pack(fill="x")
        ttk.Label(top, text="Date range", style="Card.TLabel").pack(side="left")
        self.days_label = ttk.Label(top, text="0 days", style="Card.TLabel")
        self.days_label.pack(side="right")
        self.days_scale = ttk.Scale(timeline, from_=0, to=1, orient="horizontal", command=self.timeline_changed)
        self.days_scale.set(0)
        self.days_scale.pack(fill="x", pady=(10, 0))
        ttk.Label(
            timeline,
            text="Drag to extend the end date. Maximum range: the number of commits.",
            style="Card.TLabel",
        ).pack(anchor="w", pady=(4, 0))

        actions = ttk.Frame(body)
        actions.pack(fill="x", pady=(3, 0))
        ttk.Button(actions, text="Generate commit plan", style="Primary.TButton", command=self.generate_plan).pack(side="right")

        # Keep the selected source and the automatic commit count visible when
        # the user returns from the plan screen.
        if self.folder:
            files = collect_files(self.folder)
            if files:
                self.input_var.set(self.folder)
                self.file_info.config(text=f"{len(files)} files found")
                self.count_var.set(len(files))
                self.commit_count_changed()
        elif self.selected_files:
            names = ", ".join(os.path.basename(path) for path in self.selected_files[:3])
            if len(self.selected_files) > 3:
                names += f" and {len(self.selected_files) - 3} more"
            self.input_var.set(names)
            self.file_info.config(text=f"{len(self.selected_files)} files selected")
            self.count_var.set(len(self.selected_files))
            self.commit_count_changed()

    def choose_folder(self):
        folder = filedialog.askdirectory(title="Select project folder")
        if not folder:
            return
        files = collect_files(folder)
        if not files:
            messagebox.showwarning("GitBloom", "The selected folder contains no files.")
            return
        self.folder = folder
        self.selected_files = []
        self.input_var.set(folder)
        self.file_info.config(text=f"{len(files)} files found")
        self.count_var.set(len(files))
        self.commit_count_changed()

    def choose_files(self):
        files = filedialog.askopenfilenames(title="Select project files")
        if not files:
            return
        self.folder = ""
        self.selected_files = [os.path.abspath(path) for path in files]
        names = ", ".join(os.path.basename(path) for path in self.selected_files[:3])
        if len(self.selected_files) > 3:
            names += f" and {len(self.selected_files) - 3} more"
        self.input_var.set(names)
        self.file_info.config(text=f"{len(self.selected_files)} files selected")
        self.count_var.set(len(self.selected_files))
        self.commit_count_changed()

    def get_files(self):
        if self.folder:
            return collect_files(self.folder)
        return [os.path.basename(path) for path in self.selected_files]

    def timeline_changed(self, value):
        self.days_label.config(text=f"{int(round(float(value)))} days")

    def commit_count_changed(self):
        """Keep the date range limited to the editable commit count."""
        try:
            count = max(1, int(self.count_var.get()))
        except (TypeError, ValueError, tk.TclError):
            return

        self.days_scale.configure(to=count)
        current_days = int(round(float(self.days_scale.get())))
        if current_days > count:
            self.days_scale.set(count)
            self.timeline_changed(count)

    def generate_plan(self):
        try:
            url = self.repo_var.get().strip()
            if not url.startswith(("https://", "http://", "git@")):
                raise ValueError("Enter a valid remote Git repository URL.")
            if not self.folder and not self.selected_files:
                raise ValueError("Select a project folder or one or more files.")
            start = datetime.strptime(self.start_var.get().strip(), "%d-%m-%Y")
            files = self.get_files()
            count = max(1, int(self.count_var.get()))
            if count > len(files):
                count = len(files)
                self.count_var.set(count)
            self.commit_count_changed()
            days = int(round(float(self.days_scale.get())))
            self.plan = build_plan(files, start, days, count)
            self.show_plan()
        except ValueError as error:
            messagebox.showerror("GitBloom", str(error))

    def show_plan(self):
        self.clear()
        self.header("Commit plan", f"{len(self.plan)} commits")
        body = ttk.Frame(self.root, padding=(28, 0, 28, 20))
        body.pack(fill="both", expand=True)
        canvas = tk.Canvas(body, bg="#ffffff", highlightthickness=0)
        scroll = ttk.Scrollbar(body, orient="vertical", command=canvas.yview)
        frame = ttk.Frame(canvas, style="Card.TFrame")
        frame.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame, anchor="nw")
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        for item in self.plan:
            card = ttk.Frame(frame, style="Card.TFrame", padding=14)
            card.pack(fill="x", padx=2, pady=(0, 10))
            top = ttk.Frame(card, style="Card.TFrame")
            top.pack(fill="x")
            ttk.Label(top, text=f"Commit {item['number']}", style="CardTitle.TLabel").pack(side="left")
            ttk.Label(top, text=item["date"].strftime("%d-%m-%Y"), style="Card.TLabel").pack(side="right")
            ttk.Label(card, text=item["message"], style="Card.TLabel").pack(anchor="w", pady=(7, 4))
            ttk.Label(card, text="\n".join(item["files"]), style="Card.TLabel").pack(anchor="w")

        actions = ttk.Frame(self.root, padding=(28, 0, 28, 24))
        actions.pack(fill="x")
        ttk.Button(actions, text="Back", command=self.show_settings).pack(side="left")
        ttk.Button(actions, text="Create commits", style="Primary.TButton", command=self.confirm_create).pack(side="right")

    def confirm_create(self):
        if messagebox.askyesno("GitBloom", "Create the commits using this plan?"):
            self.show_progress()
            threading.Thread(target=self.process, daemon=True).start()

    def show_progress(self):
        self.clear()
        self.header("Processing", "GitBloom is working on your repository.")
        body = ttk.Frame(self.root, padding=(28, 0, 28, 28))
        body.pack(fill="both", expand=True)
        self.status = tk.StringVar(value="Preparing...")
        ttk.Label(body, textvariable=self.status, style="Subtitle.TLabel").pack(anchor="w", pady=(0, 12))
        self.progress = ttk.Progressbar(body, maximum=100, mode="determinate")
        self.progress.pack(fill="x")
        self.percent = tk.StringVar(value="0%")
        ttk.Label(body, textvariable=self.percent).pack(anchor="w", pady=(7, 14))
        self.log = tk.Text(body, height=18, relief="solid", borderwidth=1, state="disabled")
        self.log.pack(fill="both", expand=True)

    def write_log(self, text):
        def update():
            self.log.config(state="normal")
            self.log.insert("end", text + "\n")
            self.log.see("end")
            self.log.config(state="disabled")
        self.root.after(0, update)

    def set_progress(self, current, total, text):
        value = int(current / total * 100)
        def update():
            self.progress.configure(value=value)
            self.percent.set(f"{value}%")
            self.status.set(text)
        self.root.after(0, update)

    def process(self):
        try:
            self.write_log("Cloning remote repository...")
            self.workspace, self.repository = clone_repository(self.repo_var.get().strip())
            self.write_log("Repository ready.")
            self.write_log("Copying selected project files...")
            if self.folder:
                copy_folder(self.folder, self.repository)
            else:
                copy_files(self.selected_files, "", self.repository)

            total = len(self.plan)
            for index, item in enumerate(self.plan, 1):
                self.set_progress(index - 1, total, f"Creating commit {index} of {total}")
                commit(self.repository, item["files"], item["date"], item["message"])
                self.write_log(f"Created: {item['message']}")
                self.set_progress(index, total, f"Created commit {index} of {total}")
            self.root.after(0, self.finished)
        except Exception as error:
            # Exception variables are cleared after an except block in Python.
            # Pass the text as an argument so the scheduled callback keeps it.
            self.root.after(0, self.failed, str(error))

    def finished(self):
        push_it = messagebox.askyesno("GitBloom", "Commits created successfully. Push them to the remote repository?")
        if push_it:
            try:
                self.status.set("Pushing...")
                self.write_log("Pushing to remote repository...")
                push(self.repository)
                self.write_log("Push completed.")
                messagebox.showinfo("GitBloom", "Commits created and pushed successfully.")
            except Exception as error:
                messagebox.showerror("GitBloom", str(error))
        else:
            messagebox.showinfo("GitBloom", "Commits were created locally. Nothing was pushed.")
        cleanup(self.workspace)
        self.workspace = self.repository = None

    def failed(self, error):
        cleanup(self.workspace)
        self.workspace = self.repository = None
        messagebox.showerror("GitBloom", error)
