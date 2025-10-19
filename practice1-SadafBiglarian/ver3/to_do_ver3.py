import tkinter as tk
from tkinter import messagebox, ttk
import datetime



class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("To-Do List App")
        self.root.geometry("450x350")
        
        self.categories = ["Home", "Study", "Shopping", "Work", "General"]
        self.current_category = "Home"

        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        ttk.Label(main_frame, text=" new task:").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        self.task_entry = ttk.Entry(main_frame, width=30)
        self.task_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))

        self.choose_category = tk.StringVar(value=self.current_category)
        self.category_combo = ttk.Combobox(main_frame, 
                                         textvariable=self.choose_category,
                                         values=self.categories,
                                         state="readonly",
                                         width=12)
        self.category_combo.grid(row=0, column=2, pady=5, padx=(5, 0))

        self.add_btn = ttk.Button(main_frame, text=" add task ", command=self.add_task)
        self.add_btn.grid(row=0, column=3, pady=5, padx=(5, 0))

        self.task_listbox = tk.Listbox(main_frame, height=15, selectmode=tk.SINGLE)
        self.task_listbox.grid(
            row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10
        )

        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=2, column=0, columnspan=3, pady=10)

        self.delete_btn = ttk.Button(
            buttons_frame, text="delet task ", command=self.delete_task
        )
        self.delete_btn.grid(row=0, column=0, padx=5)

        self.done_btn = ttk.Button(
            buttons_frame, text="  mark as done", command=self.mark_done
        )
        self.done_btn.grid(row=0, column=1, padx=5)

        self.clear_btn = ttk.Button(
            buttons_frame, text="clear all  ", command=self.clear_tasks
        )
        self.clear_btn.grid(row=0, column=2, padx=5)

        # Bind Enter key to add task
        self.task_entry.bind("<Return>", lambda event: self.add_task())

    def add_task(self):
        """Add New Task"""
        task = self.task_entry.get().strip()
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        current_category = self.choose_category.get()
        
        if task:
            self.task_listbox.insert(tk.END,f"[{current_category}] {task} - ({current_time}) " )
            self.task_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("warning", "please add a task")

    def delete_task(self):
        """delete task"""
        try:
            selected_index = self.task_listbox.curselection()[0]
            self.task_listbox.delete(selected_index)
        except IndexError:
            messagebox.showwarning("warning", "please choose a task")

    def clear_tasks(self):
        """clear all tasks"""
        if messagebox.askyesno("confirm", "delete all??"):
            self.task_listbox.delete(0, tk.END)

    def mark_done(self):
        """Mark as Done"""
        try:
            selected_index = self.task_listbox.curselection()[0]
            task = self.task_listbox.get(selected_index)

            if not task.startswith("✔ "):
                self.task_listbox.delete(selected_index)
                self.task_listbox.insert(selected_index, f"✔ {task}")

        except IndexError:
            messagebox.showwarning("warning", "please choose a task")


if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()
    import tkinter as tk
