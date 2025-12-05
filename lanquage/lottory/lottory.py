import tkinter as tk
from tkinter import messagebox
import random
from datetime import datetime


class LotteryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Lottery Draw Organizer")
        self.root.geometry("800x600")
        self.root.resizable(False, False)

        # 🎨 رنگ‌ها
        self.bg_color = "#e3f2fd"  # پس‌زمینه روشن‌تر
        self.accent_blue = "#1e88e5"  # آبی روشن برای عناصر برجسته
        self.add_blue = "#0288d1"  # آبی تیره برای دکمه افزودن
        self.delete_red = "#d32f2f"  # قرمز برای دکمه حذف
        self.clear_black = "#212121"  # مشکی برای دکمه پاکسازی
        self.winner_green = "#388e3c"  # سبز برای برنده
        self.start_purple = "#9c27b0"  # بنفش برای دکمه شروع

        self.root.configure(bg=self.bg_color)

        self.participants = []
        self.winners_history = []
        self.is_animating = False

        self.build_ui()

    def build_ui(self):
        title_lbl = tk.Label(
            self.root,
            text="🎁 Lottery Draw Organizer",
            font=("Helvetica", 24, "bold"),
            bg=self.bg_color,
            fg=self.accent_blue,
        )
        title_lbl.pack(pady=(20, 10))

        top_frame = tk.Frame(self.root, bg=self.bg_color)
        top_frame.pack(pady=(0, 15))

        tk.Label(
            top_frame,
            text="Participant Name:",
            font=("Helvetica", 12),
            bg=self.bg_color,
            fg="#212121",
        ).pack(side=tk.LEFT, padx=(0, 5))

        self.name_entry = tk.Entry(top_frame, font=("Helvetica", 12), width=35)
        self.name_entry.pack(side=tk.LEFT, padx=(0, 5))
        self.name_entry.bind("<Return>", lambda e: self.add_participant())

        add_btn = tk.Button(
            top_frame,
            text="+ Add",
            font=("Helvetica", 12, "bold"),
            bg=self.add_blue,
            fg="white",
            activebackground=self.add_blue,
            relief=tk.FLAT,
            width=12,
            command=self.add_participant,
        )
        add_btn.pack(side=tk.LEFT)

        tk.Label(
            self.root,
            text="Participants List:",
            font=("Helvetica", 12, "bold"),
            bg=self.bg_color,
            anchor="w",
        ).pack(fill="x", padx=40)

        list_frame = tk.Frame(self.root, bg=self.bg_color)
        list_frame.pack(pady=(5, 10), padx=40, fill="both", expand=True)

        self.listbox = tk.Listbox(
            list_frame,
            font=("Helvetica", 12),
            height=12,
            activestyle="none",
            selectmode=tk.SINGLE,
        )
        self.listbox.pack(side=tk.LEFT, fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_frame, command=self.listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scrollbar.set)

        btn_frame = tk.Frame(self.root, bg=self.bg_color)
        btn_frame.pack(pady=(5, 10))

        delete_btn = tk.Button(
            btn_frame,
            text="🗑 Delete Selected",
            font=("Helvetica", 12, "bold"),
            bg=self.delete_red,
            fg="white",
            width=16,
            relief=tk.FLAT,
            command=self.delete_selected,
        )
        delete_btn.pack(side=tk.LEFT, padx=5)

        clear_btn = tk.Button(
            btn_frame,
            text="🧹 Clear All",
            font=("Helvetica", 12, "bold"),
            bg=self.clear_black,
            fg="white",
            width=12,
            relief=tk.FLAT,
            command=self.clear_all,
        )
        clear_btn.pack(side=tk.LEFT, padx=5)

        self.winner_label_frame = tk.Frame(self.root, bg=self.winner_green)
        self.winner_label_frame.pack(pady=(10, 10), padx=80, fill="x")

        self.winner_label = tk.Label(
            self.winner_label_frame,
            text="Winner: Waiting for draw...",
            font=("Helvetica", 14, "bold"),
            bg=self.winner_green,
            fg="white",
            pady=8,
        )
        self.winner_label.pack(fill="x")

        self.start_btn = tk.Button(
            self.root,
            text="🎲 Start Lottery Draw!",
            font=("Helvetica", 14, "bold"),
            bg=self.start_purple,
            fg="white",
            activebackground=self.start_purple,
            relief=tk.FLAT,
            width=24,
            command=self.start_lottery,
        )
        self.start_btn.pack(pady=(5, 15))

        bottom_frame = tk.Frame(self.root, bg=self.bg_color)
        bottom_frame.pack(side=tk.BOTTOM, fill="x", pady=10)

        self.count_label = tk.Label(
            bottom_frame,
            text="Participants Count: 0",
            font=("Helvetica", 12),
            bg=self.bg_color,
            fg="#212121",
        )
        self.count_label.pack(side=tk.LEFT, padx=40)

        history_btn = tk.Button(
            bottom_frame,
            text="📜 Winners History",
            font=("Helvetica", 11, "bold"),
            bg="white",
            fg=self.accent_blue,
            relief=tk.GROOVE,
            command=self.show_history,
        )
        history_btn.pack(side=tk.RIGHT, padx=40)

    def update_count_label(self):
        self.count_label.config(text=f"Participants Count: {len(self.participants)}")

    def refresh_listbox(self):
        self.listbox.delete(0, tk.END)
        for p in self.participants:
            self.listbox.insert(tk.END, p)
        self.update_count_label()

    def add_participant(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("Warning", "Please enter a participant name.")
            return
        self.participants.append(name)
        self.name_entry.delete(0, tk.END)
        self.refresh_listbox()
        self.name_entry.focus_set()

    def delete_selected(self):
        if not self.participants:
            messagebox.showwarning("Warning", "No participants to delete.")
            return
        try:
            idx = self.listbox.curselection()[0]
        except IndexError:
            messagebox.showwarning("Warning", "Select someone first.")
            return
        del self.participants[idx]
        self.refresh_listbox()

    def clear_all(self):
        if not self.participants:
            return
        if messagebox.askyesno("Confirm", "Clear all participants?"):
            self.participants.clear()
            self.refresh_listbox()
            self.winner_label.config(text="Winner: Waiting for draw...")

    def start_lottery(self):
        if self.is_animating:
            return
        if not self.participants:
            messagebox.showerror("Error", "No participants to draw!")
            return

        self.is_animating = True
        self.start_btn.config(state=tk.DISABLED)
        self.animate_steps = 30
        self.animate_lottery()

    def animate_lottery(self):
        if self.animate_steps > 0:
            name = random.choice(self.participants)
            self.winner_label.config(text=f"Drawing... {name}")
            self.animate_steps -= 1
            self.root.after(80, self.animate_lottery)
        else:
            winner = random.choice(self.participants)
            self.winner_label.config(text=f"🏆 Winner: {winner}")
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.winners_history.append(f"{winner} — {timestamp}")
            self.is_animating = False
            self.start_btn.config(state=tk.NORMAL)

    def show_history(self):
        if not self.winners_history:
            messagebox.showinfo("Winners History", "No winners yet.")
            return
        messagebox.showinfo("Winners History", "\n".join(self.winners_history))


if __name__ == "__main__":
    root = tk.Tk()
    app = LotteryApp(root)
    root.mainloop()
