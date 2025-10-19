import tkinter as tk
from tkinter import ttk, messagebox
import datetime

PRIORITIES = ["Low", "Medium", "High", "Urgent", "Critical"]
CATEGORIES = ["General", "Study", "Home", "Personal", "Shopping", "Work"]


def priority_dots(p):
    idx = PRIORITIES.index(p)
    return " ".join("✔" if i == idx else "○" for i in range(5))


def status_icon(done: bool):
    return "✅" if done else "⏳"


class AdvancedTaskManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Task Manager")
        self.root.geometry("1000x600")
        self.tasks = []
        self.tree = None

        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("TFrame", background="white")
        style.configure("TLabel", background="white")
        style.configure("TButton", background="white", relief="flat")
        style.configure(
            "Treeview",
            background="white",
            fieldbackground="white",
            foreground="black",
            bordercolor="white",
            borderwidth=0,
        )
        style.configure(
            "Treeview.Heading", background="white", foreground="black", relief="flat"
        )
        style.map(
            "Treeview.Heading",
            background=[("active", "white")],
            relief=[("active", "flat")],
        )
        style.configure(
            "Vertical.TScrollbar",
            background="white",
            troughcolor="white",
            bordercolor="white",
        )

        # ===== Search row =====
        search_row = ttk.Frame(root)
        search_row.pack(fill="x", padx=8, pady=(8, 4))
        ttk.Label(search_row, text="Search:").grid(row=0, column=0, sticky="w")
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_row, textvariable=self.search_var, width=36)
        search_entry.grid(row=0, column=1, padx=(5, 8))
        search_entry.bind("<KeyRelease>", lambda e: self.apply_filters())
        ttk.Button(
            search_row,
            text="Clear",
            command=lambda: (self.search_var.set(""), self.apply_filters()),
        ).grid(row=0, column=2)

        # ===== Single Filter (field + value) =====
        filt = ttk.Frame(root)
        filt.pack(fill="x", padx=8, pady=6)

        ttk.Label(filt, text="Filter:").grid(row=0, column=0, sticky="w")
        self.filter_field = tk.StringVar(value="Status")
        filter_box = ttk.Combobox(
            filt,
            textvariable=self.filter_field,
            values=["Status", "Priority", "Category", "Task"],
            state="readonly",
            width=12,
        )
        filter_box.grid(row=0, column=1, padx=(5, 15))

        ttk.Label(filt, text="Value:").grid(row=0, column=2, sticky="w")
        self.value_var = tk.StringVar()
        self.value_combo = ttk.Combobox(
            filt, textvariable=self.value_var, state="readonly", width=18
        )
        self.value_entry = ttk.Entry(filt, width=30)

        self.value_combo.grid(row=0, column=3, padx=(5, 0))
        filter_box.bind("<<ComboboxSelected>>", lambda e: self._refresh_value_widget())
        self.value_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())
        self.value_entry.bind("<KeyRelease>", lambda e: self.apply_filters())

        ttk.Button(filt, text="Clear Filter", command=self._clear_filter).grid(
            row=0, column=4, padx=10
        )

        add_row = ttk.Frame(root)
        add_row.pack(fill="x", padx=8, pady=(0, 6))

        self.new_task_text = tk.StringVar()
        ttk.Entry(add_row, textvariable=self.new_task_text).grid(
            row=0, column=0, sticky="ew", padx=(0, 5)
        )
        add_row.grid_columnconfigure(0, weight=1)

        ttk.Label(add_row, text="Category:").grid(row=0, column=1)
        self.new_cat_var = tk.StringVar(value="General")
        ttk.Combobox(
            add_row,
            textvariable=self.new_cat_var,
            values=CATEGORIES,
            state="readonly",
            width=12,
        ).grid(row=0, column=2, padx=(5, 5))

        ttk.Label(add_row, text="Priority:").grid(row=0, column=3)
        self.new_pri_var = tk.StringVar(value="Medium")
        ttk.Combobox(
            add_row,
            textvariable=self.new_pri_var,
            values=PRIORITIES,
            state="readonly",
            width=10,
        ).grid(row=0, column=4, padx=(5, 5))

        ttk.Button(add_row, text="Add Task", command=self.add_task).grid(
            row=0, column=5, padx=(10, 0)
        )
        add_row.bind_all("<Return>", lambda e: self.add_task())

        # ===== Table =====
        table = ttk.Frame(root)
        table.pack(fill="both", expand=True, padx=8, pady=(0, 6))

        cols = ("status", "priority", "category", "task", "created")
        self.tree = ttk.Treeview(table, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c.capitalize())
        self.tree.column("status", width=70, anchor="center")
        self.tree.column("priority", width=110, anchor="center")
        self.tree.column("category", width=120, anchor="w")
        self.tree.column("task", width=420, anchor="w")
        self.tree.column("created", width=150, anchor="center")

        vsb = ttk.Scrollbar(
            table,
            orient="vertical",
            command=self.tree.yview,
            style="Vertical.TScrollbar",
        )
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        table.grid_rowconfigure(0, weight=1)
        table.grid_columnconfigure(0, weight=1)

        # init filter widget AFTER tree is ready
        self._refresh_value_widget()
        self.apply_filters()

        # ===== Bottom buttons =====
        bottom = ttk.Frame(root)
        bottom.pack(fill="x", padx=8, pady=6)
        ttk.Button(bottom, text="Toggle Done", command=self.toggle_done).pack(
            side="left", padx=3
        )
        ttk.Button(bottom, text="Edit", command=self.edit_task).pack(
            side="left", padx=3
        )
        ttk.Button(bottom, text="Delete", command=self.delete_task).pack(
            side="left", padx=3
        )
        ttk.Button(bottom, text="Stats", command=self.show_stats).pack(
            side="left", padx=3
        )
        ttk.Button(bottom, text="Refresh", command=self.apply_filters).pack(
            side="left", padx=3
        )

        self.footer_var = tk.StringVar(value="Tasks: 0 Completed | 0 Pending | 0 Total")
        ttk.Label(root, textvariable=self.footer_var).pack(
            anchor="w", padx=8, pady=(0, 6)
        )

    # ----- dynamic filter controls -----
    def _refresh_value_widget(self):
        field = self.filter_field.get()
        # hide both, then show needed one
        try:
            self.value_combo.grid_remove()
        except:
            pass
        try:
            self.value_entry.grid_remove()
        except:
            pass

        if field == "Status":
            self.value_combo.configure(values=["Pending", "Completed"])
            self.value_var.set("")
            self.value_combo.grid(row=0, column=3, padx=(5, 0))
        elif field == "Priority":
            self.value_combo.configure(values=PRIORITIES)
            self.value_var.set("")
            self.value_combo.grid(row=0, column=3, padx=(5, 0))
        elif field == "Category":
            self.value_combo.configure(values=CATEGORIES)
            self.value_var.set("")
            self.value_combo.grid(row=0, column=3, padx=(5, 0))
        else:  # Task -> Entry
            self.value_entry.delete(0, tk.END)
            self.value_entry.grid(row=0, column=3, padx=(5, 0))

    def _clear_filter(self):
        if self.filter_field.get() == "Task":
            self.value_entry.delete(0, tk.END)
        else:
            self.value_var.set("")
        self.apply_filters(update_footer=False)

    # ----- core ops -----
    def add_task_to_store(self, text, cat, pri, done):
        self.tasks.append(
            {
                "id": len(self.tasks) + 1,
                "text": text,
                "category": cat,
                "priority": pri,
                "created": datetime.datetime.now(),
                "done": done,
            }
        )

    def add_task(self):
        text = self.new_task_text.get().strip()
        if not text:
            messagebox.showwarning("Warning", "Enter a task.")
            return
        self.add_task_to_store(
            text, self.new_cat_var.get(), self.new_pri_var.get(), False
        )
        self.new_task_text.set("")
        self.apply_filters(update_footer=True)

    def get_selected_task(self):
        sel = self.tree.selection()
        if not sel:
            return None
        tid = int(sel[0])
        for t in self.tasks:
            if t["id"] == tid:
                return t
        return None

    def toggle_done(self):
        t = self.get_selected_task()
        if not t:
            return
        t["done"] = not t["done"]
        self.apply_filters(update_footer=True)

    def delete_task(self):
        t = self.get_selected_task()
        if not t:
            return
        if messagebox.askyesno("Confirm", "Delete this task?"):
            self.tasks = [x for x in self.tasks if x["id"] != t["id"]]
            self.apply_filters(update_footer=True)

    def edit_task(self):
        t = self.get_selected_task()
        if not t:
            return
        w = tk.Toplevel(self.root, background="white")
        w.title("Edit Task")
        ttk.Label(w, text="Task:").grid(row=0, column=0, padx=6, pady=6, sticky="e")
        text_var = tk.StringVar(value=t["text"])
        ttk.Entry(w, textvariable=text_var, width=44).grid(
            row=0, column=1, padx=6, pady=6
        )
        ttk.Label(w, text="Category:").grid(row=1, column=0, padx=6, pady=6, sticky="e")
        cat_var = tk.StringVar(value=t["category"])
        ttk.Combobox(w, textvariable=cat_var, values=CATEGORIES, state="readonly").grid(
            row=1, column=1, padx=6, pady=6, sticky="w"
        )
        ttk.Label(w, text="Priority:").grid(row=2, column=0, padx=6, pady=6, sticky="e")
        pri_var = tk.StringVar(value=t["priority"])
        ttk.Combobox(w, textvariable=pri_var, values=PRIORITIES, state="readonly").grid(
            row=2, column=1, padx=6, pady=6, sticky="w"
        )

        def save():
            t["text"] = text_var.get().strip() or t["text"]
            t["category"] = cat_var.get()
            t["priority"] = pri_var.get()
            w.destroy()
            self.apply_filters(update_footer=True)

        ttk.Button(w, text="Save", command=save).grid(
            row=3, column=0, columnspan=2, pady=10
        )
        w.transient(self.root)
        w.grab_set()
        w.wait_window(w)

    def show_stats(self):
        total = len(self.tasks)
        done = sum(t["done"] for t in self.tasks)
        pending = total - done
        messagebox.showinfo(
            "Stats", f"Completed: {done}\nPending: {pending}\nTotal: {total}"
        )

    # ----- filtering/rendering -----
    def apply_filters(self, update_footer=False):
        if not self.tree:
            return
        for iid in self.tree.get_children():
            self.tree.delete(iid)

        # global search on task text
        q = self.search_var.get().strip().lower()

        # single filter
        field = self.filter_field.get()
        v_combo = self.value_var.get().strip()
        v_text = self.value_entry.get().strip().lower()

        for t in self.tasks:
            if q and q not in t["text"].lower():
                continue

            if field == "Status":
                if v_combo == "Pending" and t["done"]:
                    continue
                if v_combo == "Completed" and not t["done"]:
                    continue
            elif field == "Priority":
                if v_combo and t["priority"] != v_combo:
                    continue
            elif field == "Category":
                if v_combo and t["category"] != v_combo:
                    continue
            elif field == "Task":
                if v_text and v_text not in t["text"].lower():
                    continue

            self.tree.insert(
                "",
                "end",
                iid=str(t["id"]),
                values=(
                    status_icon(t["done"]),
                    priority_dots(t["priority"]),
                    t["category"],
                    t["text"],
                    t["created"].strftime("%Y-%m-%d %H:%M"),
                ),
            )
        if update_footer:
            self.update_footer()

    def update_footer(self):
        total = len(self.tasks)
        done = sum(t["done"] for t in self.tasks)
        pending = total - done
        self.footer_var.set(
            f"Tasks: {done} Completed | {pending} Pending | {total} Total"
        )


if __name__ == "__main__":
    root = tk.Tk()
    root.configure(bg="white")
    app = AdvancedTaskManager(root)
    root.mainloop()
