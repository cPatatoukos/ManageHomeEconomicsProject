from __future__ import annotations

import tkinter as tk
from datetime import date
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk
from typing import Any, Callable, Optional

from analytics import (
    ChartPanel,
    default_month,
    default_year,
    expenses_by_category_pie,
    expenses_over_time_line,
    income_vs_expense_bars,
)
from database import (
    CategoryInUseError,
    DuplicateUsernameError,
    FinanceDB,
    FinanceDBError,
    InvalidCredentialsError,
)
from export import MONTH_NAMES, export_month_to_xlsx

NEW_CATEGORY = "➕ Νέα κατηγορία…"

COLORS = {
    "grad_top": "#dbeafe",
    "grad_bottom": "#6ee7b7",
    "bg": "#ecfdf5",
    "sidebar": "#ecfdf5",
    "sidebar_hover": "#ccfbf1",
    "sidebar_active_bg": "#99f6e4",
    "sidebar_active_bar": "#0d9488",
    "sidebar_text": "#0a0a0a",
    "sidebar_muted": "#374151",
    "card": "#ffffff",
    "card_shadow": "#94a3b8",
    "text": "#0a0a0a",
    "muted": "#374151",
    "income": "#059669",
    "expense": "#dc2626",
    "primary": "#0d9488",
    "primary_hover": "#0f766e",
    "primary_light": "#ccfbf1",
    "border": "#cbd5e1",
    "border_focus": "#0d9488",
    "input_bg": "#ffffff",
}

FONT = ("Helvetica Neue", 11)
FONT_BOLD = ("Helvetica Neue", 11, "bold")
FONT_TITLE = ("Helvetica Neue", 20, "bold")
FONT_SMALL = ("Helvetica Neue", 10)


def _hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{r:02x}{g:02x}{b:02x}"


def _lerp_color(c1: str, c2: str, t: float) -> str:
    r1, g1, b1 = _hex_to_rgb(c1)
    r2, g2, b2 = _hex_to_rgb(c2)
    return _rgb_to_hex(
        int(r1 + (r2 - r1) * t),
        int(g1 + (g2 - g1) * t),
        int(b1 + (b2 - b1) * t),
    )


class GradientBackground:
    def __init__(self, master: tk.Misc) -> None:
        self.master = master
        self.canvas = tk.Canvas(master, highlightthickness=0, bd=0, bg=COLORS["grad_top"])
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self._bind_id = master.bind("<Configure>", self._draw, add="+")
        self._draw()

    def destroy(self) -> None:
        if self._bind_id:
            try:
                self.master.unbind("<Configure>", self._bind_id)
            except tk.TclError:
                pass
            self._bind_id = ""
        try:
            if self.canvas.winfo_exists():
                self.canvas.destroy()
        except tk.TclError:
            pass

    def _draw(self, _event: tk.Event | None = None) -> None:
        try:
            if not self.canvas.winfo_exists():
                return
        except tk.TclError:
            return
        self.canvas.delete("all")
        w = max(self.canvas.winfo_width(), 2)
        h = max(self.canvas.winfo_height(), 2)
        steps = max(h // 4, 24)
        for i in range(steps):
            color = _lerp_color(COLORS["grad_top"], COLORS["grad_bottom"], i / steps)
            y0 = int(h * i / steps)
            y1 = int(h * (i + 1) / steps) + 1
            self.canvas.create_rectangle(0, y0, w, y1, fill=color, outline=color)

    def send_to_back(self) -> None:
        try:
            if self.canvas.winfo_exists():
                self.canvas.lower()
        except tk.TclError:
            pass


def shadow_card(
    parent: tk.Misc,
    *,
    inner_padx: int = 18,
    inner_pady: int = 16,
    fill: str | None = "x",
    expand: bool = False,
    **pack_kw: Any,
) -> tk.Frame:
    wrap = tk.Frame(parent, bg=COLORS["bg"])
    shadow = tk.Frame(wrap, bg=COLORS["card_shadow"])
    shadow.pack(fill="both", expand=True, padx=(0, 3), pady=(0, 3))
    card = tk.Frame(
        shadow, bg=COLORS["card"], padx=inner_padx, pady=inner_pady,
        highlightbackground=COLORS["border"], highlightthickness=1,
    )
    card.pack(fill="both", expand=True, padx=(0, 2), pady=(0, 2))
    if fill is not None:
        wrap.pack(fill=fill, expand=expand, **pack_kw)
    return card


def modern_button(
    parent: tk.Misc,
    text: str,
    command: Callable[[], None] | None = None,
    *,
    primary: bool = False,
    fill_x: bool = False,
) -> tk.Button:
    if primary:
        bg, fg, active = COLORS["primary_light"], COLORS["text"], COLORS["primary"]
    else:
        bg, fg, active = COLORS["card"], COLORS["text"], COLORS["primary_light"]
    btn = tk.Button(
        parent, text=text, command=command, font=FONT_BOLD if primary else FONT,
        bg=bg, fg=fg, activebackground=active, activeforeground=COLORS["text"],
        relief="flat", bd=0, cursor="hand2", padx=16, pady=10,
        highlightthickness=1, highlightbackground=COLORS["primary"] if primary else COLORS["border"],
    )
    if fill_x:
        btn.pack(fill="x")
    return btn


def modern_entry(parent: tk.Misc, *, show: str | None = None, width: int = 28) -> tk.Entry:
    kw: dict[str, Any] = {
        "font": FONT, "bg": COLORS["input_bg"], "fg": COLORS["text"],
        "insertbackground": COLORS["text"], "relief": "flat", "bd": 0,
        "highlightthickness": 2, "highlightbackground": COLORS["border"],
        "highlightcolor": COLORS["border_focus"], "width": width,
    }
    if show:
        kw["show"] = show
    return tk.Entry(parent, **kw)


def labeled(parent: tk.Misc, text: str, bg: str | None = None) -> tk.Label:
    return tk.Label(
        parent, text=text, font=FONT_SMALL, fg=COLORS["text"],
        bg=bg or COLORS["bg"], anchor="w",
    )


def setup_theme(root: tk.Tk) -> ttk.Style:
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    root.configure(bg=COLORS["bg"])
    style.configure(".", background=COLORS["bg"], foreground=COLORS["text"], font=FONT)
    style.configure("TFrame", background=COLORS["bg"])
    style.configure("TLabel", background=COLORS["bg"], foreground=COLORS["text"], font=FONT)
    style.configure("Muted.TLabel", background=COLORS["bg"], foreground=COLORS["text"], font=FONT_SMALL)
    style.configure("Title.TLabel", font=FONT_TITLE, foreground=COLORS["text"], background=COLORS["bg"])
    style.configure("TRadiobutton", background=COLORS["bg"], foreground=COLORS["text"], font=FONT)
    style.configure("TCheckbutton", background=COLORS["card"], foreground=COLORS["text"], font=FONT)
    style.configure("Card.TCheckbutton", background=COLORS["card"], foreground=COLORS["text"])
    style.configure("Card.TRadiobutton", background=COLORS["card"], foreground=COLORS["text"])
    style.configure("TCombobox", padding=8, fieldbackground=COLORS["input_bg"], foreground=COLORS["text"])
    style.map("TCombobox", fieldbackground=[("readonly", COLORS["input_bg"])])
    style.configure("Treeview", rowheight=30, font=FONT, background=COLORS["card"], fieldbackground=COLORS["card"], foreground=COLORS["text"])
    style.configure("Treeview.Heading", font=FONT_BOLD, background=COLORS["primary_light"], foreground=COLORS["text"])
    style.map("Treeview", background=[("selected", COLORS["primary_light"])], foreground=[("selected", COLORS["text"])])
    return style


class CategoryPicker(tk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        db: FinanceDB,
        kind: str,
        on_change: Optional[Callable[[], None]] = None,
        *,
        card_bg: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(master, bg=card_bg or COLORS["bg"], **kwargs)
        self.db = db
        self.kind = kind
        self.on_change = on_change
        self._card_bg = card_bg or COLORS["bg"]
        self._map: dict[str, int] = {}

        labeled(self, "Κατηγορία", self._card_bg).pack(anchor="w")

        row = tk.Frame(self, bg=self._card_bg)
        row.pack(fill="x", pady=(6, 0))

        self.combo = ttk.Combobox(row, state="readonly", width=26, font=FONT)
        self.combo.pack(side="left", fill="x", expand=True)
        self.combo.bind("<<ComboboxSelected>>", self._on_select)

        modern_button(row, "➕ Νέα", self._add_new, primary=False).pack(side="left", padx=(8, 0))
        self.refresh()

    def refresh(self) -> None:
        cats = self.db.list_categories(self.kind)
        names = [c["name"] for c in cats]
        self._map = {c["name"]: c["id"] for c in cats}
        self.combo["values"] = names + [NEW_CATEGORY]
        current = self.combo.get()
        if current in self._map:
            self.combo.set(current)
        elif names:
            self.combo.set(names[0])
        else:
            self.combo.set(NEW_CATEGORY)

    def get_category_id(self) -> Optional[int]:
        name = self.combo.get().strip()
        if name == NEW_CATEGORY or not name:
            return self._prompt_new()
        cid = self._map.get(name)
        if cid is None:
            messagebox.showwarning("Κατηγορία", "Επιλέξτε έγκυρη κατηγορία ή δημιουργήστε νέα.")
            return None
        return cid

    def set_by_name(self, name: str) -> None:
        cats = self.db.list_categories(self.kind)
        names = [c["name"] for c in cats]
        self._map = {c["name"]: c["id"] for c in cats}
        self.combo["values"] = names + [NEW_CATEGORY]
        if name in self._map:
            self.combo.set(name)
        elif names:
            self.combo.set(names[0])
        else:
            self.combo.set(NEW_CATEGORY)

    def _add_new(self) -> None:
        self._prompt_new()

    def _on_select(self, _event: tk.Event) -> None:
        if self.combo.get() == NEW_CATEGORY:
            self._prompt_new()
        if self.on_change:
            self.on_change()

    def _prompt_new(self) -> Optional[int]:
        dialog = tk.Toplevel(self.winfo_toplevel())
        dialog.title("Νέα κατηγορία")
        dialog.geometry("380x200")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        dialog.configure(bg=COLORS["bg"])

        card = shadow_card(dialog, inner_padx=24, inner_pady=20, fill="both", expand=True, padx=20, pady=20)

        labeled(card, "Όνομα κατηγορίας", COLORS["card"]).pack(anchor="w")
        entry = modern_entry(card, width=32)
        entry.pack(fill="x", pady=(6, 12))
        entry.focus_set()
        result: dict[str, Optional[int]] = {"id": None}

        def save() -> None:
            name = entry.get().strip()
            if not name:
                messagebox.showwarning("Σφάλμα", "Δώστε όνομα κατηγορίας.", parent=dialog)
                return
            try:
                cid = self.db.create_category(name, self.kind)
                result["id"] = cid
                self.refresh()
                self.combo.set(name)
                dialog.destroy()
            except FinanceDBError as e:
                messagebox.showerror("Σφάλμα", str(e), parent=dialog)

        btn_row = tk.Frame(card, bg=COLORS["card"])
        btn_row.pack(fill="x")
        modern_button(btn_row, "Ακύρωση", dialog.destroy).pack(side="left", padx=(0, 8))
        modern_button(btn_row, "Αποθήκευση", save, primary=True).pack(side="left")
        dialog.wait_window()
        return result["id"]


class MonthYearPicker(ttk.Frame):
    def __init__(self, master: tk.Misc, *, label: str = "", **kwargs: Any) -> None:
        super().__init__(master, **kwargs)
        self.year_var = tk.StringVar(value=str(default_year()))
        self.month_var = tk.StringVar(value=MONTH_NAMES[default_month() - 1])
        col = 0
        if label:
            ttk.Label(self, text=label).grid(row=0, column=col, sticky="w", padx=(0, 8))
            col += 1
        ttk.Label(self, text="Έτος").grid(row=0, column=col, sticky="w", padx=(0, 4))
        col += 1
        ttk.Combobox(
            self, textvariable=self.year_var, width=7,
            values=[str(y) for y in range(2020, 2031)], state="readonly",
        ).grid(row=0, column=col, padx=(0, 10))
        col += 1
        ttk.Label(self, text="Μήνας").grid(row=0, column=col, sticky="w", padx=(0, 4))
        col += 1
        ttk.Combobox(
            self, textvariable=self.month_var, width=12,
            values=MONTH_NAMES, state="readonly",
        ).grid(row=0, column=col)

    def get_year(self) -> int:
        return int(self.year_var.get())

    def get_month(self) -> int:
        return MONTH_NAMES.index(self.month_var.get()) + 1

    def set_year_month(self, year: int, month: int) -> None:
        self.year_var.set(str(year))
        self.month_var.set(MONTH_NAMES[month - 1])


class DateRangePicker(ttk.Frame):
    def __init__(self, master: tk.Misc, **kwargs: Any) -> None:
        super().__init__(master, **kwargs)
        today = date.today()
        self.from_picker = MonthYearPicker(self, label="Από")
        self.from_picker.pack(side="left", padx=(0, 16))
        self.to_picker = MonthYearPicker(self, label="Έως")
        self.to_picker.pack(side="left")
        self.to_picker.set_year_month(today.year, today.month)

    def get_range(self) -> tuple[int, int, int, int]:
        return (
            self.from_picker.get_year(),
            self.from_picker.get_month(),
            self.to_picker.get_year(),
            self.to_picker.get_month(),
        )

    @staticmethod
    def validate_range(sy: int, sm: int, ey: int, em: int) -> bool:
        return (sy * 100 + sm) <= (ey * 100 + em)


class FinanceApp:
    def __init__(self, root: tk.Tk, db: FinanceDB) -> None:
        self.root = root
        self.db = db
        self.user: Optional[dict[str, Any]] = None
        self.view_scope = tk.StringVar(value="family")
        self.style = setup_theme(root)
        self.nav_buttons: dict[str, tk.Button] = {}
        self.nav_indicators: dict[str, tk.Frame] = {}
        self.chart_panel = ChartPanel(None)

        root.title("Οικογενειακά Οικονομικά")
        root.geometry("1150x740")
        root.minsize(980, 620)

        self.container = tk.Frame(root, bg=COLORS["bg"])
        self.container.pack(fill="both", expand=True)
        self._gradient = GradientBackground(self.container)
        self.content_layer = tk.Frame(self.container, bg=COLORS["bg"])
        self.content_layer.pack(fill="both", expand=True)
        self._gradient.send_to_back()
        self._show_auth()

    def _scope_user_id(self) -> Optional[int]:
        if self.view_scope.get() == "family":
            return None
        return self.user["id"] if self.user else None

    def _is_family_view(self) -> bool:
        return self.view_scope.get() == "family"

    def _build_scope_bar(self, parent: tk.Misc, on_change: Optional[Callable[[], None]] = None) -> ttk.Frame:
        bar = ttk.Frame(parent)
        ttk.Label(bar, text="Προβολή:").pack(side="left", padx=(0, 8))
        ttk.Radiobutton(
            bar, text="Όλη η οικογένεια", variable=self.view_scope, value="family",
            command=on_change,
        ).pack(side="left", padx=(0, 8))
        ttk.Radiobutton(
            bar, text="Μόνο εγώ", variable=self.view_scope, value="mine",
            command=on_change,
        ).pack(side="left")
        return bar

    def _clear_container(self) -> None:
        for w in self.content_layer.winfo_children():
            w.destroy()

    def _show_auth(self) -> None:
        self._clear_container()
        self.user = None

        frame = tk.Frame(self.content_layer, bg=COLORS["bg"])
        frame.place(relx=0.5, rely=0.5, anchor="center")

        card = shadow_card(frame, inner_padx=40, inner_pady=36, fill="x")

        tk.Label(card, text="Οικογενειακά Οικονομικά", font=FONT_TITLE, bg=COLORS["card"], fg=COLORS["text"]).pack(pady=(0, 6))
        tk.Label(card, text="Διαχείριση εσόδων & εξόδων", font=FONT_SMALL, bg=COLORS["card"], fg=COLORS["text"]).pack(pady=(0, 24))

        self.auth_mode = tk.StringVar(value="login")
        tabs = tk.Frame(card, bg=COLORS["card"])
        tabs.pack(fill="x", pady=(0, 16))
        ttk.Radiobutton(tabs, text="Σύνδεση", variable=self.auth_mode, value="login").pack(side="left", padx=8)
        ttk.Radiobutton(tabs, text="Εγγραφή", variable=self.auth_mode, value="register").pack(side="left", padx=8)

        labeled(card, "Όνομα χρήστη", COLORS["card"]).pack(anchor="w")
        self.auth_user = modern_entry(card, width=32)
        self.auth_user.pack(fill="x", pady=(4, 12))

        labeled(card, "Κωδικός", COLORS["card"]).pack(anchor="w")
        self.auth_pass = modern_entry(card, width=32, show="•")
        self.auth_pass.pack(fill="x", pady=(4, 20))
        self.auth_pass.bind("<Return>", lambda _: self._do_auth())

        modern_button(card, "Συνέχεια", self._do_auth, primary=True, fill_x=True)
        self._gradient.send_to_back()

    def _do_auth(self) -> None:
        username = self.auth_user.get().strip()
        password = self.auth_pass.get()
        if not username or not password:
            messagebox.showwarning("Σφάλμα", "Συμπληρώστε όνομα και κωδικό.")
            return
        try:
            if self.auth_mode.get() == "register":
                if self.db.username_exists(username):
                    messagebox.showerror("Σφάλμα", "Το όνομα χρήστη υπάρχει ήδη.")
                    return
                self.db.create_user(username, password)
                messagebox.showinfo("Επιτυχία", "Ο λογαριασμός δημιουργήθηκε. Συνδεθείτε τώρα.")
                self.auth_mode.set("login")
                self.auth_pass.delete(0, tk.END)
                return
            self.user = self.db.verify_user(username, password)
            today = date.today()
            self.db.sync_recurring_for_month(today.year, today.month)
            self.view_scope.set("family")
            self._show_dashboard()
        except DuplicateUsernameError:
            messagebox.showerror("Σφάλμα", "Το όνομα χρήστη υπάρχει ήδη.")
        except InvalidCredentialsError:
            messagebox.showerror("Σφάλμα", "Λάθος στοιχεία σύνδεσης.")
        except FinanceDBError as e:
            messagebox.showerror("Σφάλμα", str(e))

    def _show_dashboard(self) -> None:
        self._clear_container()

        shell = tk.Frame(self.content_layer, bg=COLORS["bg"])
        shell.pack(fill="both", expand=True)

        sidebar = tk.Frame(shell, bg=COLORS["sidebar"], width=240, highlightbackground=COLORS["border"], highlightthickness=1)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(
            sidebar, text="Οικονομικά", font=("Helvetica Neue", 15, "bold"),
            bg=COLORS["sidebar"], fg=COLORS["text"], pady=22, padx=18,
        ).pack(anchor="w")
        tk.Label(
            sidebar, text=self.user["username"], font=FONT_SMALL,
            bg=COLORS["sidebar"], fg=COLORS["text"], padx=18,
        ).pack(anchor="w", pady=(0, 16))

        nav_items = [
            ("home", "Αρχική"),
            ("transactions", "Συναλλαγές"),
            ("recurring", "Μηνιαία"),
            ("categories", "Κατηγορίες"),
            ("analytics", "Στατιστικά"),
            ("export", "Εξαγωγή"),
            ("account", "Λογαριασμός"),
        ]
        self.nav_buttons = {}
        self.nav_indicators = {}
        for key, label in nav_items:
            row = tk.Frame(sidebar, bg=COLORS["sidebar"])
            row.pack(fill="x", pady=1)
            indicator = tk.Frame(row, width=4, bg=COLORS["sidebar"])
            indicator.pack(side="left", fill="y")
            btn = tk.Button(
                row, text=f"  {label}", anchor="w", relief="flat", bd=0,
                bg=COLORS["sidebar"], fg=COLORS["text"], font=FONT,
                activebackground=COLORS["sidebar_hover"], activeforeground=COLORS["text"],
                padx=14, pady=11, cursor="hand2",
                command=lambda k=key: self._navigate(k),
            )
            btn.pack(side="left", fill="x", expand=True)
            self.nav_buttons[key] = btn
            self.nav_indicators[key] = indicator

        tk.Button(
            sidebar, text="  Αποσύνδεση", anchor="w", relief="flat", bd=0,
            bg=COLORS["sidebar"], fg=COLORS["text"], font=FONT,
            activebackground=COLORS["sidebar_hover"], activeforeground=COLORS["text"],
            padx=18, pady=12,
            command=self._show_auth,
        ).pack(fill="x", side="bottom", pady=18)

        self.content = tk.Frame(shell, bg=COLORS["bg"], padx=28, pady=24)
        self.content.pack(side="left", fill="both", expand=True)
        self._gradient.send_to_back()
        self._navigate("home")

    def _set_active_nav(self, key: str) -> None:
        for k, btn in self.nav_buttons.items():
            active = k == key
            bg = COLORS["sidebar_active_bg"] if active else COLORS["sidebar"]
            btn.configure(bg=bg, fg=COLORS["text"], font=FONT_BOLD if active else FONT)
            self.nav_indicators[k].configure(bg=COLORS["sidebar_active_bar"] if active else COLORS["sidebar"])
            btn.master.configure(bg=bg)

    def _navigate(self, key: str) -> None:
        self._set_active_nav(key)
        for w in self.content.winfo_children():
            w.destroy()
        {
            "home": self._page_home,
            "transactions": self._page_transactions,
            "recurring": self._page_recurring,
            "categories": self._page_categories,
            "analytics": self._page_analytics,
            "export": self._page_export,
            "account": self._page_account,
        }[key]()

    def _card(self, parent: tk.Misc, title: str, value: str, color: str) -> tk.Frame:
        wrap = tk.Frame(parent, bg=COLORS["bg"])
        card = shadow_card(wrap, inner_padx=20, inner_pady=14, fill="both", expand=True)
        tk.Label(card, text=title, font=FONT_SMALL, bg=COLORS["card"], fg=COLORS["text"]).pack(anchor="w")
        tk.Label(card, text=value, font=("Helvetica Neue", 22, "bold"), bg=COLORS["card"], fg=color).pack(anchor="w", pady=(4, 0))
        return wrap

    def _totals(self, year: int, month: int) -> dict[str, float]:
        return self.db.monthly_totals(year, month, user_id=self._scope_user_id())

    def _page_home(self) -> None:
        tk.Label(self.content, text="Αρχική", font=FONT_TITLE, bg=COLORS["bg"], fg=COLORS["text"]).pack(anchor="w")
        header = tk.Frame(self.content, bg=COLORS["bg"])
        header.pack(fill="x", pady=(12, 8))
        picker = MonthYearPicker(header)
        picker.pack(side="left")

        cards_row = tk.Frame(self.content, bg=COLORS["bg"])
        cards_row.pack(fill="x", pady=(0, 12))
        tree_card = shadow_card(self.content, inner_padx=8, inner_pady=8, fill="both", expand=True)
        tree_frame = tk.Frame(tree_card, bg=COLORS["card"])
        tree_frame.pack(fill="both", expand=True)

        cols = ["user", "title", "category", "kind", "amount"]
        tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=12)
        headings = {"user": "Χρήστης", "title": "Τίτλος", "category": "Κατηγορία", "kind": "Τύπος", "amount": "Ποσό (€)"}
        for c in cols:
            tree.heading(c, text=headings[c])
            tree.column(c, width=120 if c != "title" else 180)
        tree.column("amount", anchor="e", width=90)
        scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        def refresh() -> None:
            y, m = picker.get_year(), picker.get_month()
            totals = self._totals(y, m)
            for w in cards_row.winfo_children():
                w.destroy()
            self._card(cards_row, "Έσοδα", f"{totals['income']:.2f} €", COLORS["income"]).pack(side="left", padx=(0, 12))
            self._card(cards_row, "Έξοδα", f"{totals['expense']:.2f} €", COLORS["expense"]).pack(side="left", padx=(0, 12))
            net_color = COLORS["income"] if totals["net"] >= 0 else COLORS["expense"]
            self._card(cards_row, "Καθαρό", f"{totals['net']:.2f} €", net_color).pack(side="left")
            for item in tree.get_children():
                tree.delete(item)
            for t in self.db.list_transactions(y, m, user_id=self._scope_user_id()):
                kind = "Έσοδο" if t["category_kind"] == "income" else "Έξοδο"
                row = (t.get("username", ""), t["title"], t["category_name"], kind, f"{t['amount']:.2f}")
                tree.insert("", "end", iid=str(t["id"]), values=row)

        scope = self._build_scope_bar(self.content, refresh)
        scope.pack(anchor="w", pady=(0, 8))
        modern_button(header, "Ανανέωση", refresh).pack(side="left", padx=12)
        refresh()

    def _page_transactions(self) -> None:
        tk.Label(self.content, text="Συναλλαγές", font=FONT_TITLE, bg=COLORS["bg"], fg=COLORS["text"]).pack(anchor="w")

        header = tk.Frame(self.content, bg=COLORS["bg"])
        header.pack(fill="x", pady=(8, 8))
        picker = MonthYearPicker(header)
        picker.pack(side="left")

        form_wrap = tk.Frame(self.content, bg=COLORS["bg"])
        form_wrap.pack(fill="x", pady=(0, 12))
        form_card = shadow_card(form_wrap, inner_padx=22, inner_pady=18, fill="x")

        tk.Label(form_card, text="Νέα συναλλαγή", font=FONT_BOLD, bg=COLORS["card"], fg=COLORS["text"]).pack(anchor="w", pady=(0, 12))

        kind_var = tk.StringVar(value="expense")
        kf = tk.Frame(form_card, bg=COLORS["card"])
        kf.pack(anchor="w", pady=(0, 10))
        ttk.Radiobutton(kf, text="Έξοδο", variable=kind_var, value="expense", style="Card.TRadiobutton").pack(side="left", padx=(0, 14))
        ttk.Radiobutton(kf, text="Έσοδο", variable=kind_var, value="income", style="Card.TRadiobutton").pack(side="left")

        row1 = tk.Frame(form_card, bg=COLORS["card"])
        row1.pack(fill="x", pady=4)
        col_l = tk.Frame(row1, bg=COLORS["card"])
        col_l.pack(side="left", fill="x", expand=True, padx=(0, 12))
        labeled(col_l, "Τίτλος", COLORS["card"]).pack(anchor="w")
        title_entry = modern_entry(col_l, width=32)
        title_entry.pack(fill="x", pady=(4, 0))

        col_r = tk.Frame(row1, bg=COLORS["card"])
        col_r.pack(side="left")
        labeled(col_r, "Ποσό (€)", COLORS["card"]).pack(anchor="w")
        amount_entry = modern_entry(col_r, width=14)
        amount_entry.pack(pady=(4, 0))

        cat_picker = CategoryPicker(form_card, self.db, "expense", card_bg=COLORS["card"])
        cat_picker.pack(anchor="w", fill="x", pady=8)

        monthly_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(form_card, text="Μηνιαία (επαναλαμβανόμενη)", variable=monthly_var, style="Card.TCheckbutton").pack(anchor="w", pady=(0, 8))

        def on_kind_change(*_a: Any) -> None:
            cat_picker.kind = kind_var.get()
            cat_picker.refresh()

        kind_var.trace_add("write", on_kind_change)

        btn_row = tk.Frame(form_card, bg=COLORS["card"])
        btn_row.pack(fill="x", pady=(8, 0))

        def load_list() -> None:
            for item in tree.get_children():
                tree.delete(item)
            y, m = picker.get_year(), picker.get_month()
            for t in self.db.list_transactions(y, m, user_id=self._scope_user_id()):
                kind = "Έσοδο" if t["category_kind"] == "income" else "Έξοδο"
                monthly = "Ναι" if t.get("recurring_template_id") else "Όχι"
                row = (t.get("username", ""), t["title"], t["category_name"], kind, f"{t['amount']:.2f}", monthly)
                tree.insert("", "end", iid=str(t["id"]), values=row)

        scope = self._build_scope_bar(self.content, load_list)
        try:
            scope.pack(anchor="w", pady=(0, 8), before=header)
        except tk.TclError:
            scope.pack(anchor="w", pady=(0, 8))
        modern_button(header, "Ανανέωση λίστας", load_list).pack(side="left", padx=12)

        def add_txn() -> None:
            try:
                raw_amount = amount_entry.get().strip().replace(",", ".")
                if not raw_amount:
                    messagebox.showwarning("Σφάλμα", "Δώστε ποσό.")
                    return
                amount = float(raw_amount)
                if amount <= 0:
                    messagebox.showwarning("Σφάλμα", "Το ποσό πρέπει να είναι θετικό.")
                    return
                cid = cat_picker.get_category_id()
                if cid is None:
                    return
                title = title_entry.get().strip()
                if not title:
                    messagebox.showwarning("Σφάλμα", "Δώστε τίτλο.")
                    return
                y, m = picker.get_year(), picker.get_month()
                self.db.create_transaction(cid, self.user["id"], title, amount, y, m, is_monthly=monthly_var.get())
                title_entry.delete(0, tk.END)
                amount_entry.delete(0, tk.END)
                monthly_var.set(False)
                load_list()
                messagebox.showinfo("Επιτυχία", "Η συναλλαγή καταχωρήθηκε.")
            except ValueError:
                messagebox.showerror("Σφάλμα", "Μη έγκυρο ποσό.")
            except FinanceDBError as e:
                messagebox.showerror("Σφάλμα", str(e))

        def edit_txn() -> None:
            sel = tree.selection()
            if not sel:
                messagebox.showinfo("Επιλογή", "Επιλέξτε εγγραφή.")
                return
            txn = self.db.get_transaction(int(sel[0]))
            cat = self.db.get_category(txn["category_id"])
            self._edit_transaction_dialog(txn, cat, load_list)

        def delete_txn() -> None:
            sel = tree.selection()
            if not sel:
                return
            if messagebox.askyesno("Διαγραφή", "Διαγραφή επιλεγμένης εγγραφής;"):
                self.db.delete_transaction(int(sel[0]))
                load_list()

        modern_button(btn_row, "Προσθήκη συναλλαγής", add_txn, primary=True).pack(side="left")

        list_card = shadow_card(self.content, inner_padx=8, inner_pady=8, fill="both", expand=True)
        list_header = tk.Frame(list_card, bg=COLORS["card"])
        list_header.pack(fill="x", pady=(0, 8))
        tk.Label(list_header, text="Καταχωρημένες συναλλαγές", font=FONT_BOLD, bg=COLORS["card"], fg=COLORS["text"]).pack(side="left")
        list_actions = tk.Frame(list_header, bg=COLORS["card"])
        list_actions.pack(side="right")

        list_frame = tk.Frame(list_card, bg=COLORS["card"])
        list_frame.pack(fill="both", expand=True)
        cols = ["user", "title", "category", "kind", "amount", "monthly"]
        tree = ttk.Treeview(list_frame, columns=cols, show="headings")
        heads = {"user": "Χρήστης", "title": "Τίτλος", "category": "Κατηγορία", "kind": "Τύπος", "amount": "Ποσό (€)", "monthly": "Μηνιαίο"}
        for c in cols:
            tree.heading(c, text=heads[c])
        tree.column("amount", anchor="e", width=90)
        tree.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(list_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        tree.bind("<Double-1>", lambda _e: edit_txn())

        modern_button(list_actions, "Επεξεργασία", edit_txn, primary=True).pack(side="left", padx=(0, 8))
        modern_button(list_actions, "Διαγραφή", delete_txn).pack(side="left")

        load_list()

    def _edit_transaction_dialog(
        self, txn: dict[str, Any], cat: dict[str, Any], on_save: Callable[[], None],
    ) -> None:
        dialog = tk.Toplevel(self.root)
        dialog.title("Επεξεργασία συναλλαγής")
        dialog.geometry("460x500")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=COLORS["bg"])

        card = shadow_card(dialog, inner_padx=24, inner_pady=20, fill="both", expand=True, padx=16, pady=16)

        tk.Label(card, text="Επεξεργασία συναλλαγής", font=FONT_BOLD, bg=COLORS["card"], fg=COLORS["text"]).pack(anchor="w", pady=(0, 12))

        labeled(card, "Τίτλος", COLORS["card"]).pack(anchor="w")
        title_e = modern_entry(card, width=36)
        title_e.insert(0, txn["title"])
        title_e.pack(fill="x", pady=(4, 12))

        labeled(card, "Ποσό (€)", COLORS["card"]).pack(anchor="w")
        amount_e = modern_entry(card, width=36)
        amount_e.insert(0, str(txn["amount"]))
        amount_e.pack(fill="x", pady=(4, 12))

        cat_picker = CategoryPicker(card, self.db, cat["kind"], card_bg=COLORS["card"])
        cat_picker.pack(anchor="w", fill="x", pady=(4, 12))
        cat_picker.set_by_name(cat["name"])

        my = MonthYearPicker(card)
        my.set_year_month(txn["year"], txn["month"])
        my.pack(anchor="w", pady=(0, 12))

        monthly_var = tk.BooleanVar(value=bool(txn.get("recurring_template_id")))
        ttk.Checkbutton(card, text="Μηνιαία (επαναλαμβανόμενη)", variable=monthly_var, style="Card.TCheckbutton").pack(anchor="w", pady=(0, 12))

        def save() -> None:
            try:
                cid = cat_picker.get_category_id()
                if cid is None:
                    return
                raw = amount_e.get().strip().replace(",", ".")
                amount = float(raw)
                if amount <= 0:
                    messagebox.showwarning("Σφάλμα", "Το ποσό πρέπει να είναι θετικό.", parent=dialog)
                    return
                self.db.update_transaction_with_monthly(
                    txn["id"],
                    category_id=cid,
                    user_id=txn["user_id"],
                    title=title_e.get().strip(),
                    amount=amount,
                    year=my.get_year(),
                    month=my.get_month(),
                    is_monthly=monthly_var.get(),
                )
                dialog.destroy()
                on_save()
            except ValueError:
                messagebox.showerror("Σφάλμα", "Μη έγκυρα δεδομένα.", parent=dialog)
            except FinanceDBError as e:
                messagebox.showerror("Σφάλμα", str(e), parent=dialog)

        btn_row = tk.Frame(card, bg=COLORS["card"])
        btn_row.pack(fill="x")
        modern_button(btn_row, "Ακύρωση", dialog.destroy).pack(side="left", padx=(0, 8))
        modern_button(btn_row, "Αποθήκευση", save, primary=True).pack(side="left")

    def _page_recurring(self) -> None:
        ttk.Label(self.content, text="Μηνιαία ποσά", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            self.content,
            text="Σταθερά έσοδα/έξοδα που δημιουργούνται αυτόματα κάθε μήνα (π.χ. μισθός, δόση δανείου).",
            style="Muted.TLabel",
        ).pack(anchor="w", pady=(4, 12))

        list_frame = ttk.Frame(self.content)
        list_frame.pack(fill="both", expand=True)
        cols = ("title", "category", "kind", "amount", "user", "active")
        tree = ttk.Treeview(list_frame, columns=cols, show="headings")
        for c, h in zip(cols, ("Τίτλος", "Κατηγορία", "Τύπος", "Ποσό (€)", "Χρήστης", "Ενεργό")):
            tree.heading(c, text=h)
        tree.column("amount", anchor="e", width=90)
        tree.pack(side="left", fill="both", expand=True)
        ttk.Scrollbar(list_frame, orient="vertical", command=tree.yview).pack(side="right", fill="y")

        btn_row = ttk.Frame(self.content)
        btn_row.pack(fill="x", pady=8)

        def load_list() -> None:
            for item in tree.get_children():
                tree.delete(item)
            for r in self.db.list_recurring_templates_detailed(user_id=self._scope_user_id()):
                kind = "Έσοδο" if r["category_kind"] == "income" else "Έξοδο"
                active = "Ναι" if r["is_active"] else "Όχι"
                tree.insert("", "end", iid=str(r["id"]), values=(
                    r["title"], r["category_name"], kind, f"{r['amount']:.2f}",
                    r.get("username", ""), active,
                ))

        def edit_recurring() -> None:
            sel = tree.selection()
            if not sel:
                return
            tmpl = self.db.get_recurring_template(int(sel[0]))
            cat = self.db.get_category(tmpl["category_id"])
            self._edit_recurring_dialog(tmpl, cat, load_list)

        def toggle_active() -> None:
            sel = tree.selection()
            if not sel:
                return
            tid = int(sel[0])
            tmpl = self.db.get_recurring_template(tid)
            self.db.update_recurring_template(tid, is_active=not tmpl["is_active"])
            load_list()

        def delete_recurring() -> None:
            sel = tree.selection()
            if not sel:
                return
            if messagebox.askyesno("Διαγραφή", "Διαγραφή μηνιαίου προτύπου;"):
                self.db.delete_recurring_template(int(sel[0]))
                load_list()

        scope = self._build_scope_bar(self.content, load_list)
        scope.pack(anchor="w", pady=(0, 8))
        ttk.Button(btn_row, text="Ανανέωση", command=load_list).pack(side="left", padx=(0, 8))
        ttk.Button(btn_row, text="Επεξεργασία", command=edit_recurring).pack(side="left", padx=(0, 8))
        ttk.Button(btn_row, text="Ενεργ/Ανενεργ", command=toggle_active).pack(side="left", padx=(0, 8))
        ttk.Button(btn_row, text="Διαγραφή", command=delete_recurring).pack(side="left")
        load_list()

    def _edit_recurring_dialog(
        self, tmpl: dict[str, Any], cat: dict[str, Any], on_save: Callable[[], None],
    ) -> None:
        dialog = tk.Toplevel(self.root)
        dialog.title("Επεξεργασία μηνιαίου ποσού")
        dialog.geometry("400x280")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Τίτλος").pack(anchor="w", padx=20, pady=(16, 4))
        title_e = ttk.Entry(dialog, width=34)
        title_e.insert(0, tmpl["title"])
        title_e.pack(padx=20)

        ttk.Label(dialog, text="Ποσό (€)").pack(anchor="w", padx=20, pady=(12, 4))
        amount_e = ttk.Entry(dialog, width=34)
        amount_e.insert(0, str(tmpl["amount"]))
        amount_e.pack(padx=20)

        ttk.Label(dialog, text="Κατηγορία").pack(anchor="w", padx=20, pady=(12, 4))
        pf = ttk.Frame(dialog)
        pf.pack(padx=20, anchor="w")
        cat_picker = CategoryPicker(pf, self.db, cat["kind"])
        cat_picker.set_by_name(cat["name"])

        def save() -> None:
            try:
                cid = cat_picker.get_category_id()
                if cid is None:
                    return
                self.db.update_recurring_template(
                    tmpl["id"],
                    category_id=cid,
                    title=title_e.get().strip(),
                    amount=float(amount_e.get().replace(",", ".")),
                )
                dialog.destroy()
                on_save()
            except (ValueError, FinanceDBError) as e:
                messagebox.showerror("Σφάλμα", str(e), parent=dialog)

        row = ttk.Frame(dialog)
        row.pack(pady=16)
        ttk.Button(row, text="Ακύρωση", command=dialog.destroy).pack(side="left", padx=8)
        ttk.Button(row, text="Αποθήκευση", style="Primary.TButton", command=save).pack(side="left", padx=8)

    def _page_categories(self) -> None:
        tk.Label(self.content, text="Κατηγορίες", font=FONT_TITLE, bg=COLORS["bg"], fg=COLORS["text"]).pack(anchor="w", pady=(0, 4))
        tk.Label(
            self.content,
            text="Διαχείριση κατηγοριών εσόδων και εξόδων.",
            font=FONT_SMALL,
            bg=COLORS["bg"],
            fg=COLORS["muted"],
        ).pack(anchor="w", pady=(0, 12))

        paned = tk.Frame(self.content, bg=COLORS["bg"])
        paned.pack(fill="both", expand=True)

        for i, (kind, label, accent) in enumerate([
            ("income", "Έσοδα", COLORS["income"]),
            ("expense", "Έξοδα", COLORS["expense"]),
        ]):
            col_wrap = tk.Frame(paned, bg=COLORS["bg"])
            col_wrap.pack(side="left", fill="both", expand=True, padx=(0 if i == 0 else 8, 0))
            col = shadow_card(col_wrap, inner_padx=16, inner_pady=16, fill="both", expand=True)

            header = tk.Frame(col, bg=COLORS["card"])
            header.pack(fill="x", pady=(0, 12))
            tk.Label(header, text=label, font=FONT_BOLD, bg=COLORS["card"], fg=accent).pack(side="left")

            list_frame = tk.Frame(col, bg=COLORS["card"])
            list_frame.pack(fill="both", expand=True, pady=(0, 12))
            lb = tk.Listbox(
                list_frame,
                font=FONT,
                bg=COLORS["input_bg"],
                fg=COLORS["text"],
                selectbackground=COLORS["primary_light"],
                selectforeground=COLORS["text"],
                activestyle="none",
                relief="flat",
                highlightthickness=1,
                highlightbackground=COLORS["border"],
                highlightcolor=COLORS["border_focus"],
                bd=0,
            )
            lb.pack(side="left", fill="both", expand=True)
            sb = ttk.Scrollbar(list_frame, orient="vertical", command=lb.yview)
            lb.configure(yscrollcommand=sb.set)
            sb.pack(side="right", fill="y")

            labeled(col, "Νέα κατηγορία", COLORS["card"]).pack(anchor="w")
            entry = modern_entry(col, width=28)
            entry.pack(fill="x", pady=(4, 12))
            entry.bind("<Return>", lambda _e, k=kind: add_cat(k))

            btn_f = tk.Frame(col, bg=COLORS["card"])
            btn_f.pack(fill="x")

            def reload_list(listbox: tk.Listbox = lb, k: str = kind) -> None:
                listbox.delete(0, tk.END)
                for c in self.db.list_categories(k):
                    listbox.insert(tk.END, c["name"])

            def add_cat(k: str = kind, listbox: tk.Listbox = lb, ent: tk.Entry = entry) -> None:
                name = ent.get().strip()
                if not name:
                    messagebox.showwarning("Σφάλμα", "Δώστε όνομα κατηγορίας.")
                    return
                try:
                    self.db.create_category(name, k)
                    ent.delete(0, tk.END)
                    reload_list(listbox, k)
                except FinanceDBError as e:
                    messagebox.showerror("Σφάλμα", str(e))

            def edit_cat(listbox: tk.Listbox = lb, k: str = kind) -> None:
                sel = listbox.curselection()
                if not sel:
                    messagebox.showinfo("Επιλογή", "Επιλέξτε κατηγορία.")
                    return
                old_name = listbox.get(sel[0])
                cats = {c["name"]: c["id"] for c in self.db.list_categories(k)}

                dialog = tk.Toplevel(self.root)
                dialog.title("Μετονομασία κατηγορίας")
                dialog.geometry("380x200")
                dialog.transient(self.root)
                dialog.grab_set()
                dialog.configure(bg=COLORS["bg"])

                card = shadow_card(dialog, inner_padx=24, inner_pady=20, fill="both", expand=True, padx=16, pady=16)
                labeled(card, "Νέο όνομα", COLORS["card"]).pack(anchor="w")
                rename_e = modern_entry(card, width=30)
                rename_e.insert(0, old_name)
                rename_e.pack(fill="x", pady=(6, 12))
                rename_e.focus_set()

                def save_rename() -> None:
                    new_name = rename_e.get().strip()
                    if not new_name:
                        messagebox.showwarning("Σφάλμα", "Δώστε όνομα κατηγορίας.", parent=dialog)
                        return
                    try:
                        self.db.update_category(cats[old_name], name=new_name)
                        dialog.destroy()
                        reload_list(listbox, k)
                    except FinanceDBError as e:
                        messagebox.showerror("Σφάλμα", str(e), parent=dialog)

                btn_row = tk.Frame(card, bg=COLORS["card"])
                btn_row.pack(fill="x")
                modern_button(btn_row, "Ακύρωση", dialog.destroy).pack(side="left", padx=(0, 8))
                modern_button(btn_row, "Αποθήκευση", save_rename, primary=True).pack(side="left")
                rename_e.bind("<Return>", lambda _e: save_rename())

            def delete_cat(listbox: tk.Listbox = lb, k: str = kind) -> None:
                sel = listbox.curselection()
                if not sel:
                    messagebox.showinfo("Επιλογή", "Επιλέξτε κατηγορία.")
                    return
                name = listbox.get(sel[0])
                if not messagebox.askyesno("Διαγραφή", f"Διαγραφή κατηγορίας «{name}»;"):
                    return
                cats = {c["name"]: c["id"] for c in self.db.list_categories(k)}
                try:
                    self.db.delete_category(cats[name])
                    reload_list(listbox, k)
                except CategoryInUseError:
                    messagebox.showerror("Σφάλμα", "Η κατηγορία χρησιμοποιείται σε εγγραφές.")
                except FinanceDBError as e:
                    messagebox.showerror("Σφάλμα", str(e))

            modern_button(btn_f, "Προσθήκη", lambda k=kind: add_cat(k)).pack(side="left", padx=(0, 8))
            modern_button(btn_f, "Επεξεργασία", edit_cat).pack(side="left", padx=(0, 8))
            modern_button(btn_f, "Διαγραφή", delete_cat).pack(side="left")
            lb.bind("<Double-1>", lambda _e: edit_cat())
            reload_list()

    def _page_account(self) -> None:
        tk.Label(self.content, text="Λογαριασμός", font=FONT_TITLE, bg=COLORS["bg"], fg=COLORS["text"]).pack(anchor="w")
        card = shadow_card(self.content, inner_padx=28, inner_pady=24, fill="x")
        card.pack(fill="x", pady=(16, 0))

        tk.Label(
            card,
            text=f"Συνδεδεμένος ως: {self.user['username']}",
            font=FONT_BOLD,
            bg=COLORS["card"],
            fg=COLORS["text"],
        ).pack(anchor="w", pady=(0, 16))

        labeled(card, "Νέο όνομα χρήστη (κενό = χωρίς αλλαγή)", COLORS["card"]).pack(anchor="w")
        username_e = modern_entry(card, width=36)
        username_e.pack(fill="x", pady=(4, 12))

        labeled(card, "Νέος κωδικός (κενό = χωρίς αλλαγή)", COLORS["card"]).pack(anchor="w")
        password_e = modern_entry(card, width=36, show="•")
        password_e.pack(fill="x", pady=(4, 20))

        def save_account() -> None:
            new_username = username_e.get().strip()
            new_password = password_e.get()
            if not new_username and not new_password:
                messagebox.showinfo("Λογαριασμός", "Δεν υπάρχουν αλλαγές προς αποθήκευση.")
                return
            try:
                self.db.update_user(
                    self.user["id"],
                    username=new_username or None,
                    password=new_password or None,
                )
                if new_username:
                    self.user["username"] = new_username
                username_e.delete(0, tk.END)
                password_e.delete(0, tk.END)
                messagebox.showinfo("Επιτυχία", "Ο λογαριασμός ενημερώθηκε.")
            except DuplicateUsernameError:
                messagebox.showerror("Σφάλμα", "Το όνομα χρήστη υπάρχει ήδη.")
            except ValueError as e:
                messagebox.showerror("Σφάλμα", str(e))
            except FinanceDBError as e:
                messagebox.showerror("Σφάλμα", str(e))

        def delete_account() -> None:
            if not messagebox.askyesno(
                "Διαγραφή λογαριασμού",
                f"Διαγραφή του λογαριασμού «{self.user['username']}»;\n\n"
                "Θα διαγραφούν και όλες οι συναλλαγές και τα μηνιαία πρότυπά σας.",
            ):
                return
            confirm = simpledialog.askstring(
                "Επιβεβαίωση",
                f"Πληκτρολογήστε το όνομα «{self.user['username']}» για επιβεβαίωση:",
                parent=self.root,
            )
            if confirm != self.user["username"]:
                messagebox.showinfo("Ακύρωση", "Η διαγραφή ακυρώθηκε.")
                return
            try:
                self.db.delete_user(self.user["id"])
                messagebox.showinfo("Επιτυχία", "Ο λογαριασμός διαγράφηκε.")
                self._show_auth()
            except FinanceDBError as e:
                messagebox.showerror("Σφάλμα", str(e))

        btn_row = tk.Frame(card, bg=COLORS["card"])
        btn_row.pack(fill="x")
        modern_button(btn_row, "Αποθήκευση αλλαγών", save_account, primary=True).pack(side="left", padx=(0, 8))
        modern_button(btn_row, "Διαγραφή λογαριασμού", delete_account).pack(side="left")

        others = [u for u in self.db.list_users() if u["id"] != self.user["id"]]
        if others:
            family_card = shadow_card(self.content, inner_padx=28, inner_pady=20, fill="x")
            family_card.pack(fill="x", pady=(16, 0))
            tk.Label(
                family_card,
                text="Άλλοι χρήστες οικογένειας",
                font=FONT_BOLD,
                bg=COLORS["card"],
                fg=COLORS["text"],
            ).pack(anchor="w", pady=(0, 8))
            for u in others:
                tk.Label(
                    family_card,
                    text=f"• {u['username']}",
                    font=FONT,
                    bg=COLORS["card"],
                    fg=COLORS["text"],
                ).pack(anchor="w")

    def _page_analytics(self) -> None:
        ttk.Label(self.content, text="Στατιστικά & Γραφήματα", style="Title.TLabel").pack(anchor="w")

        row1 = ttk.Frame(self.content)
        row1.pack(fill="x", pady=(12, 4))
        pie_picker = MonthYearPicker(row1, label="Μήνας (pie)")
        pie_picker.pack(side="left")
        ttk.Label(row1, text="Έτος (bar)").pack(side="left", padx=(16, 4))
        bar_year = ttk.Combobox(row1, width=8, values=[str(y) for y in range(2020, 2031)], state="readonly")
        bar_year.set(str(default_year()))
        bar_year.pack(side="left")

        row2 = ttk.Frame(self.content)
        row2.pack(fill="x", pady=(8, 4))
        range_picker = DateRangePicker(row2)
        range_picker.pack(side="left")
        ttk.Label(row2, text="Κατηγορία (line)").pack(side="left", padx=(16, 4))
        cat_var = tk.StringVar(value="Όλες")
        cat_combo = ttk.Combobox(
            row2, textvariable=cat_var,
            values=["Όλες"] + [c["name"] for c in self.db.list_categories("expense")],
            state="readonly", width=16,
        )
        cat_combo.pack(side="left")

        chart_btns = ttk.Frame(self.content)
        chart_btns.pack(fill="x", pady=(8, 4))
        chart_host = ttk.Frame(self.content)
        chart_host.pack(fill="both", expand=True)
        self.chart_panel = ChartPanel(chart_host)

        def show_pie() -> None:
            y, m = pie_picker.get_year(), pie_picker.get_month()
            fig = expenses_by_category_pie(self.db, y, m, user_id=self._scope_user_id())
            self.chart_panel.show(fig)

        def show_bars() -> None:
            fig = income_vs_expense_bars(self.db, int(bar_year.get()), user_id=self._scope_user_id())
            self.chart_panel.show(fig)

        def show_line() -> None:
            sy, sm, ey, em = range_picker.get_range()
            if not DateRangePicker.validate_range(sy, sm, ey, em):
                messagebox.showwarning("Σφάλμα", "Το εύρος «Από» πρέπει να προηγείται του «Έως».")
                return
            cat_name = cat_var.get()
            cat_id = None
            if cat_name != "Όλες":
                for c in self.db.list_categories("expense"):
                    if c["name"] == cat_name:
                        cat_id = c["id"]
                        break
            fig = expenses_over_time_line(
                self.db, sy, sm, ey, em,
                category_id=cat_id, user_id=self._scope_user_id(),
                category_name=cat_name if cat_id else None,
            )
            self.chart_panel.show(fig)

        scope = self._build_scope_bar(self.content)
        scope.pack(anchor="w", pady=(0, 4))
        ttk.Button(chart_btns, text="Έξοδα ανά κατηγορία (pie)", command=show_pie).pack(side="left", padx=(0, 8))
        ttk.Button(chart_btns, text="Έσοδα vs Έξοδα (bar)", command=show_bars).pack(side="left", padx=(0, 8))
        ttk.Button(chart_btns, text="Έξοδα σε χρονικό εύρος (line)", command=show_line).pack(side="left")
        show_pie()

    def _page_export(self) -> None:
        ttk.Label(self.content, text="Εξαγωγή Excel", style="Title.TLabel").pack(anchor="w")
        ttk.Label(self.content, text="Εξαγωγή συναλλαγών μήνα σε αρχείο .xlsx", style="Muted.TLabel").pack(anchor="w", pady=(4, 12))
        picker = MonthYearPicker(self.content)
        picker.pack(anchor="w", pady=(0, 12))

        def do_export() -> None:
            y, m = picker.get_year(), picker.get_month()
            scope = "oikogeneia" if self._is_family_view() else self.user["username"]
            default_name = f"oikonomika_{scope}_{y}_{m:02d}.xlsx"
            path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel", "*.xlsx")],
                initialfile=default_name,
            )
            if not path:
                return
            try:
                export_month_to_xlsx(self.db, y, m, Path(path), user_id=self._scope_user_id())
                messagebox.showinfo("Επιτυχία", f"Αποθηκεύτηκε:\n{path}")
            except Exception as e:
                messagebox.showerror("Σφάλμα", str(e))

        self._build_scope_bar(self.content).pack(anchor="w", pady=(0, 12))
        ttk.Button(self.content, text="Εξαγωγή .xlsx", style="Primary.TButton", command=do_export).pack(anchor="w")


def run_app(db: FinanceDB) -> None:
    root = tk.Tk()
    FinanceApp(root, db)
    root.mainloop()


if __name__ == "__main__":
    from database import DEFAULT_DB_PATH

    database = FinanceDB(DEFAULT_DB_PATH)
    database.initialize()
    database.seed_default_categories()
    run_app(database)
