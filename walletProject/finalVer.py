# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from collections import defaultdict, OrderedDict
from decimal import Decimal, InvalidOperation
import csv

# نمودارها
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

APP_TITLE = "Personal Wallet - Advanced Version"
CURRENCY = "$"

CATEGORY_MAP = {
    "income": ["Salary", "Bonus", "Investment", "Gift", "Other"],
    "expense": [
        "Food",
        "Bills",
        "Rent",
        "Transportation",
        "Healthcare",
        "Shopping",
        "Entertainment",
        "Education",
        "Travel",
        "Other",
    ],
}
ALL_CATEGORIES = sorted(set(CATEGORY_MAP["income"] + CATEGORY_MAP["expense"]))


def fmt_amount(amount: Decimal) -> str:
    sign = "+" if amount >= 0 else "-"
    return f"{sign}{CURRENCY}{abs(amount):,.2f}"


def parse_amount(text: str) -> Decimal:
    clean = text.strip().replace(CURRENCY, "").replace(",", "")
    if clean.endswith("-"):
        clean = "-" + clean[:-1]
    return Decimal(clean)


def month_key(dt_str: str) -> str:
    return datetime.strptime(dt_str, "%Y-%m-%d %H:%M").strftime("%Y-%m")


# ---------------------- Transactions Tab ----------------------
class TransactionsUI(ttk.Frame):
    def __init__(self, master, on_change=None):
        super().__init__(master, padding=12)
        self.on_change = on_change
        self.transactions = []
        self._build_ui()
        self._refresh_balance()

    def _build_ui(self):
        self.columnconfigure(0, weight=1)

        # Header (balance + export)
        header = ttk.Frame(self)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        self.balance_var = tk.StringVar(value="Current Balance: $0.00")
        balance_lbl = ttk.Label(
            header, textvariable=self.balance_var, padding=10, anchor="w"
        )
        balance_lbl.configure(font=("Segoe UI", 16, "bold"))
        balance_lbl.grid(row=0, column=0, sticky="w")

        ttk.Button(header, text="Export CSV", command=self._export_csv).grid(
            row=0, column=1, padx=8
        )

        # Add Transaction form (بدون Type)
        form = ttk.LabelFrame(self, text="Add Transaction", padding=10)
        form.grid(row=1, column=0, sticky="ew", pady=(10, 8))
        for i in range(6):
            form.columnconfigure(i, weight=1)

        ttk.Label(form, text="Amount:").grid(row=0, column=0, sticky="w")
        self.amount_var = tk.StringVar()
        self.amount_entry = ttk.Entry(form, textvariable=self.amount_var)
        self.amount_entry.grid(row=0, column=1, sticky="ew")
        self.amount_entry.focus_set()

        ttk.Label(form, text="Category:").grid(row=0, column=2, sticky="w")
        self.category_var = tk.StringVar(value=ALL_CATEGORIES[0])
        self.category_combo = ttk.Combobox(
            form,
            textvariable=self.category_var,
            values=ALL_CATEGORIES,
            state="readonly",
        )
        self.category_combo.grid(row=0, column=3, sticky="ew")
        self.category_combo.current(0)

        ttk.Label(form, text="Description:").grid(row=0, column=4, sticky="w")
        self.desc_var = tk.StringVar()
        self.desc_entry = ttk.Entry(form, textvariable=self.desc_var)
        self.desc_entry.grid(row=0, column=5, sticky="ew")

        btns = ttk.Frame(form)
        btns.grid(row=1, column=0, columnspan=6, sticky="w", pady=(10, 0))
        ttk.Button(
            btns, text="Add Income", command=lambda: self._add_transaction("income")
        ).pack(side="left", padx=(0, 6))
        ttk.Button(
            btns, text="Add Expense", command=lambda: self._add_transaction("expense")
        ).pack(side="left", padx=(0, 6))
        ttk.Button(btns, text="Clear Form", command=self._clear_form).pack(side="left")

        # History table
        history = ttk.LabelFrame(self, text="Transaction History", padding=8)
        history.grid(row=2, column=0, sticky="nsew", pady=(8, 0))
        self.rowconfigure(2, weight=1)

        cols = ("#", "Amount", "Type", "Category", "Description", "Date")
        self.tree = ttk.Treeview(history, columns=cols, show="headings", height=10)
        for c, w in zip(cols, (50, 120, 90, 140, 260, 150)):
            self.tree.heading(c, text=c)
            self.tree.column(c, width=w, anchor="w")
        self.tree.column("Amount", anchor="e")
        self.tree.column("#", anchor="center")

        vsb = ttk.Scrollbar(history, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        history.columnconfigure(0, weight=1)
        history.rowconfigure(0, weight=1)

        style = ttk.Style(self)
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.map(
            "Treeview",
            background=[("selected", "#0078d7")],
            foreground=[("selected", "white")],
        )
        self.tree.tag_configure("income", foreground="#16803c")
        self.tree.tag_configure("expense", foreground="#a11717")

    # فقط ورودی‌ها
    def _reset_inputs(self):
        try:
            self.amount_entry.delete(0, tk.END)
        except Exception:
            self.amount_var.set("")
        try:
            self.desc_entry.delete(0, tk.END)
        except Exception:
            self.desc_var.set("")
        self.category_combo.current(0)
        self.amount_entry.focus_set()

    # پاک‌کردن همه تراکنش‌ها + فرم
    def _clear_form(self):
        if not self.transactions:
            self._reset_inputs()
            return
        ok = messagebox.askyesno(
            "Clear All Transactions", "همهٔ تراکنش‌ها حذف شوند؟ این عمل قابل بازگشت نیست."
        )
        if not ok:
            return
        self.transactions.clear()
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        self._refresh_balance()
        self._reset_inputs()
        if self.on_change:
            self.on_change(self.transactions)

    def _add_transaction(self, force_type: str):
        try:
            amount = parse_amount(self.amount_var.get())
        except (InvalidOperation, ValueError):
            messagebox.showerror(
                "Invalid Amount", "لطفاً مبلغ را به‌صورت عددی صحیح وارد کنید."
            )
            return
        if force_type == "expense" and amount > 0:
            amount = -amount
        if force_type == "income" and amount < 0:
            amount = -amount

        data = {
            "id": len(self.transactions) + 1,
            "amount": amount,
            "type": "Income" if amount >= 0 else "Expense",
            "category": self.category_var.get(),
            "description": self.desc_var.get().strip(),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        self.transactions.append(data)
        self._insert_row(data)
        self._refresh_balance()
        self._reset_inputs()
        if self.on_change:
            self.on_change(self.transactions)

    def _insert_row(self, tr):
        tag = "income" if tr["amount"] >= 0 else "expense"
        self.tree.insert(
            "",
            0,
            values=(
                tr["id"],
                fmt_amount(tr["amount"]),
                tr["type"],
                tr["category"],
                tr["description"],
                tr["date"],
            ),
            tags=(tag,),
        )

    def _refresh_balance(self):
        total = (
            sum(t["amount"] for t in self.transactions)
            if self.transactions
            else Decimal("0")
        )
        self.balance_var.set(f"Current Balance: {CURRENCY}{total:,.2f}")

    def _export_csv(self):
        if not self.transactions:
            messagebox.showinfo("Nothing to export", "هنوز تراکنشی ثبت نشده است.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            initialfile="transactions.csv",
        )
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(
                    ["#", "Amount", "Type", "Category", "Description", "Date"]
                )
                for t in sorted(self.transactions, key=lambda x: x["id"]):
                    writer.writerow(
                        [
                            t["id"],
                            f"{t['amount']}",
                            t["type"],
                            t["category"],
                            t["description"],
                            t["date"],
                        ]
                    )
            messagebox.showinfo("Exported", "CSV با موفقیت ذخیره شد.")
        except Exception as e:
            messagebox.showerror("Error", f"در ذخیره فایل مشکلی پیش آمد:\n{e}")


# ---------------------- Analytics Tab ----------------------
class AnalyticsUI(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=12)
        self._build_ui()

    def _build_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.stats_box = ttk.LabelFrame(self, text="Financial Statistics", padding=10)
        self.stats_box.grid(row=0, column=0, sticky="ew")
        for i in range(3):
            self.stats_box.columnconfigure(i, weight=1)

        self.stat_vars = OrderedDict(
            [
                ("Total Income", tk.StringVar(value="$0.00")),
                ("Total Expenses", tk.StringVar(value="$0.00")),
                ("Net Savings", tk.StringVar(value="$0.00")),
                ("Transactions", tk.StringVar(value="0")),
                ("Avg Monthly Expense", tk.StringVar(value="$0.00")),
                ("Largest Expense", tk.StringVar(value="$0.00")),
            ]
        )

        keys = list(self.stat_vars.keys())
        for idx, key in enumerate(keys):
            r, c = divmod(idx, 3)
            cell = ttk.Frame(self.stats_box, padding=(0, 4))
            cell.grid(row=r, column=c, sticky="w")
            ttk.Label(cell, text=f"{key}: ", font=("Segoe UI", 10, "bold")).pack(
                side="left"
            )
            ttk.Label(
                cell,
                textvariable=self.stat_vars[key],
                foreground=(
                    "#16803c" if key in ("Total Income", "Net Savings") else "#a15a00"
                ),
            ).pack(side="left")

        charts = ttk.LabelFrame(self, text="Expense Analytics", padding=10)
        charts.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        charts.columnconfigure(0, weight=1)
        charts.columnconfigure(1, weight=1)
        charts.rowconfigure(0, weight=1)

        self.fig_left = Figure(figsize=(4.6, 3.4), dpi=100)
        self.ax_pie = self.fig_left.add_subplot(111)
        self.canvas_left = FigureCanvasTkAgg(self.fig_left, master=charts)
        self.canvas_left.get_tk_widget().grid(
            row=0, column=0, sticky="nsew", padx=(0, 10)
        )

        self.fig_right = Figure(figsize=(4.6, 3.4), dpi=100)
        self.ax_bar = self.fig_right.add_subplot(111)
        self.canvas_right = FigureCanvasTkAgg(self.fig_right, master=charts)
        self.canvas_right.get_tk_widget().grid(row=0, column=1, sticky="nsew")

    def update_from_transactions(self, transactions):
        income = sum(t["amount"] for t in transactions if t["amount"] >= 0)
        expense = -sum(t["amount"] for t in transactions if t["amount"] < 0)
        net = income - expense
        count = len(transactions)

        largest_exp = max(
            [abs(t["amount"]) for t in transactions if t["amount"] < 0],
            default=Decimal("0"),
        )

        by_month_exp = defaultdict(Decimal)
        for t in transactions:
            ym = month_key(t["date"])
            if t["amount"] < 0:
                by_month_exp[ym] += -t["amount"]
        avg_monthly_exp = (
            (sum(by_month_exp.values()) / max(1, len(by_month_exp)))
            if by_month_exp
            else Decimal("0")
        )

        self.stat_vars["Total Income"].set(f"{CURRENCY}{income:,.2f}")
        self.stat_vars["Total Expenses"].set(f"{CURRENCY}{expense:,.2f}")
        self.stat_vars["Net Savings"].set(f"{CURRENCY}{net:,.2f}")
        self.stat_vars["Transactions"].set(str(count))
        self.stat_vars["Avg Monthly Expense"].set(f"{CURRENCY}{avg_monthly_exp:,.2f}")
        self.stat_vars["Largest Expense"].set(f"{CURRENCY}{largest_exp:,.2f}")

        # pie
        self.ax_pie.clear()
        exp_by_cat = defaultdict(Decimal)
        for t in transactions:
            if t["amount"] < 0:
                exp_by_cat[t["category"]] += -t["amount"]
        if exp_by_cat:
            labels = list(exp_by_cat.keys())
            values = [float(v) for v in exp_by_cat.values()]
            self.ax_pie.pie(values, labels=labels, autopct="%1.1f%%", startangle=140)
            self.ax_pie.set_title("Expense Distribution by Category")
        else:
            self.ax_pie.text(0.5, 0.5, "No expense data", ha="center", va="center")
        self.canvas_left.draw()

        # bar 6 ماه اخیر
        self.ax_bar.clear()
        inc_by_month = defaultdict(Decimal)
        exp_by_month = defaultdict(Decimal)
        for t in transactions:
            ym = month_key(t["date"])
            if t["amount"] >= 0:
                inc_by_month[ym] += t["amount"]
            else:
                exp_by_month[ym] += -t["amount"]
        months = sorted(set(inc_by_month) | set(exp_by_month), reverse=True)[:6]
        months.sort()
        if months:
            xi = range(len(months))
            width = 0.35
            inc_vals = [float(inc_by_month.get(m, 0)) for m in months]
            exp_vals = [float(exp_by_month.get(m, 0)) for m in months]
            self.ax_bar.bar(
                [x - width / 2 for x in xi], inc_vals, width=width, label="Income"
            )
            self.ax_bar.bar(
                [x + width / 2 for x in xi], exp_vals, width=width, label="Expense"
            )
            self.ax_bar.set_xticks(list(xi))
            self.ax_bar.set_xticklabels(months, rotation=45)
            self.ax_bar.set_ylabel(f"Amount ({CURRENCY})")
            self.ax_bar.set_title("Income vs Expense (Last 6 Months)")
            self.ax_bar.legend()
        else:
            self.ax_bar.text(0.5, 0.5, "No data", ha="center", va="center")
        self.canvas_right.draw()


# ---------------------- Budget Tab ----------------------
class BudgetUI(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=12)
        self.monthly_budget = Decimal("0")
        self.current_month = datetime.now().strftime("%Y-%m")
        self.spent_this_month = Decimal("0")
        self._build_ui()
        self._refresh_view()

    def _build_ui(self):
        self.columnconfigure(0, weight=1)

        # Setup
        setup = ttk.LabelFrame(self, text="Monthly Budget Setup", padding=10)
        setup.grid(row=0, column=0, sticky="ew")
        setup.columnconfigure(1, weight=1)

        ttk.Label(setup, text="Monthly Budget Amount:").grid(
            row=0, column=0, sticky="w"
        )
        self.budget_var = tk.StringVar(value="0.0")
        self.budget_entry = ttk.Entry(setup, textvariable=self.budget_var)
        self.budget_entry.grid(row=0, column=1, sticky="ew", padx=(6, 6))
        ttk.Button(setup, text="Set Budget", command=self._set_budget).grid(
            row=0, column=2
        )

        # Progress
        prog = ttk.LabelFrame(self, text="Budget Progress", padding=10)
        prog.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        prog.columnconfigure(0, weight=1)

        self.summary_var = tk.StringVar(
            value="Budget: $0.00 | Spent: $0.00 | Remaining: $0.00"
        )
        ttk.Label(prog, textvariable=self.summary_var).grid(
            row=0, column=0, sticky="w", pady=(0, 6)
        )

        self.progress = ttk.Progressbar(
            prog, orient="horizontal", mode="determinate", maximum=100
        )
        self.progress.grid(row=1, column=0, sticky="ew", ipady=3)
        self.percent_var = tk.StringVar(value="0.0%")
        ttk.Label(prog, textvariable=self.percent_var, anchor="center").grid(
            row=2, column=0, pady=(6, 0)
        )

        # Alerts
        alerts = ttk.LabelFrame(self, text="Budget Alerts", padding=10)
        alerts.grid(row=2, column=0, sticky="nsew", pady=(10, 0))
        alerts.rowconfigure(0, weight=1)
        alerts.columnconfigure(0, weight=1)
        self.alerts = tk.Text(alerts, height=8, wrap="word")
        self.alerts.grid(row=0, column=0, sticky="nsew")
        sb = ttk.Scrollbar(alerts, command=self.alerts.yview)
        self.alerts.configure(yscrollcommand=sb.set)
        sb.grid(row=0, column=1, sticky="ns")

    def _set_budget(self):
        try:
            value = parse_amount(self.budget_var.get())
            if value <= 0:
                raise InvalidOperation
        except Exception:
            messagebox.showerror(
                "Invalid Budget", "لطفاً بودجه ماهانه را به‌صورت عدد مثبت وارد کنید."
            )
            self.budget_entry.focus_set()
            return
        self.monthly_budget = abs(value)
        self._refresh_view()

    def update_from_transactions(self, transactions):
        # هزینه‌های ماه جاری
        this_month = datetime.now().strftime("%Y-%m")
        self.current_month = this_month
        self.spent_this_month = sum(
            (-t["amount"])
            for t in transactions
            if t["amount"] < 0 and month_key(t["date"]) == this_month
        )
        self._refresh_view()

    def _refresh_view(self):
        spent = self.spent_this_month
        budget = self.monthly_budget
        remaining = max(Decimal("0"), budget - spent)
        pct = float((spent / budget * 100) if budget > 0 else 0)
        self.progress["value"] = min(100, pct)
        self.summary_var.set(
            f"Budget: {CURRENCY}{budget:,.2f} | Spent: {CURRENCY}{spent:,.2f} | Remaining: {CURRENCY}{remaining:,.2f}"
        )
        self.percent_var.set(f"{pct:.1f}%")
        self._update_alerts(pct)

    def _update_alerts(self, pct):
        self.alerts.delete("1.0", tk.END)
        msgs = []
        if self.monthly_budget <= 0:
            msgs.append("• Set a monthly budget to start tracking.")
        else:
            if pct >= 100:
                msgs.append("• ALERT: You have exceeded your monthly budget!")
            elif pct >= 90:
                msgs.append("• WARNING: You have used 90% of your budget.")
            elif pct >= 75:
                msgs.append("• NOTICE: You have used 75% of your budget.")
            elif pct >= 50:
                msgs.append("• Heads-up: 50% of your budget is used.")
            else:
                msgs.append("• You're within your budget. Keep it up!")
        self.alerts.insert(tk.END, "\n".join(msgs))


# ---------------------- Main App with tabs ----------------------
class WalletApp(ttk.Notebook):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill="both", expand=True)

        self.analytics_tab = AnalyticsUI(self)
        self.budget_tab = BudgetUI(self)
        self.transactions_tab = TransactionsUI(
            self, on_change=self._on_transactions_changed
        )

        self.add(self.transactions_tab, text="Transactions")
        self.add(self.analytics_tab, text="Analytics")
        self.add(self.budget_tab, text="Budget")

        self._seed_sample_data()  # اختیاری

    def _on_transactions_changed(self, transactions):
        self.analytics_tab.update_from_transactions(transactions)
        self.budget_tab.update_from_transactions(transactions)

    def _seed_sample_data(self):
        samples = [
            (+2500, "Salary", "Monthly salary", "2025-10-01 09:00"),
            (-350.5, "Food", "Grocery shopping", "2025-10-05 16:30"),
            (-120, "Shopping", "Clothes", "2025-10-15 14:20"),
            (-85, "Entertainment", "Movie tickets", "2025-10-10 20:15"),
            (+2500, "Salary", "Monthly salary", "2025-09-01 09:00"),
            (-420.75, "Food", "Grocery shopping", "2025-10-05 16:30"),
            (-150, "Bills", "Electricity bill", "2025-10-10 12:00"),
            (+2500, "Salary", "Monthly salary", "2025-08-01 09:00"),
            (-380.25, "Food", "Grocery shopping", "2025-09-05 16:30"),
            (-200, "Healthcare", "Doctor visit", "2025-09-10 10:30"),
        ]
        for amt, cat, desc, dt in samples:
            data = {
                "id": len(self.transactions_tab.transactions) + 1,
                "amount": Decimal(str(amt)),
                "type": "Income" if amt >= 0 else "Expense",
                "category": cat,
                "description": desc,
                "date": dt,
            }
            self.transactions_tab.transactions.append(data)
            self.transactions_tab._insert_row(data)
        self.transactions_tab._refresh_balance()
        self._on_transactions_changed(self.transactions_tab.transactions)


# ---------------------- Run ----------------------
if __name__ == "__main__":
    root = tk.Tk()
    root.title(APP_TITLE)
    root.geometry("980x700")
    root.minsize(900, 640)
    app = WalletApp(root)
    root.mainloop()
