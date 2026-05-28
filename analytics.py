from __future__ import annotations

from datetime import date
from typing import Any, Optional

import matplotlib

matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from database import FinanceDB, month_range_iter

MONTH_LABELS = [
    "Ιαν", "Φεβ", "Μαρ", "Απρ", "Μάι", "Ιουν",
    "Ιουλ", "Αυγ", "Σεπ", "Οκτ", "Νοε", "Δεκ",
]

CHART_COLORS = {
    "income": "#059669",
    "expense": "#dc2626",
    "accent": "#0d9488",
    "pie": ["#6366f1", "#8b5cf6", "#ec4899", "#f97316", "#14b8a6", "#eab308", "#64748b"],
}


def _style_figure(fig: Figure) -> None:
    fig.patch.set_facecolor("#ffffff")
    for ax in fig.axes:
        ax.set_facecolor("#fafafa")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(colors="#475569")
        ax.title.set_color("#1e293b")
        ax.xaxis.label.set_color("#475569")
        ax.yaxis.label.set_color("#475569")


class ChartPanel:
    def __init__(self, parent: Any) -> None:
        self.parent = parent
        self._canvas: FigureCanvasTkAgg | None = None
        self._figure: Figure | None = None

    def clear(self) -> None:
        if self._canvas is not None:
            self._canvas.get_tk_widget().destroy()
            self._canvas = None
        if self._figure is not None:
            plt.close(self._figure)
            self._figure = None

    def show(self, fig: Figure) -> None:
        self.clear()
        _style_figure(fig)
        fig.tight_layout()
        self._figure = fig
        self._canvas = FigureCanvasTkAgg(fig, master=self.parent)
        self._canvas.draw()
        self._canvas.get_tk_widget().pack(fill="both", expand=True)


def expenses_by_category_pie(
    db: FinanceDB,
    year: int,
    month: int,
    *,
    user_id: Optional[int] = None,
) -> Figure:
    rows = db.sum_by_category(year, month, kind="expense", user_id=user_id)
    labels = [r["category_name"] for r in rows]
    values = [float(r["total"]) for r in rows]

    fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
    if not values:
        ax.text(0.5, 0.5, "Δεν υπάρχουν έξοδα", ha="center", va="center", fontsize=12, color="#64748b")
        ax.set_axis_off()
        ax.set_title(f"Έξοδα ανά κατηγορία — {MONTH_LABELS[month - 1]} {year}")
        return fig

    colors = CHART_COLORS["pie"][: len(values)]
    ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=140, colors=colors, textprops={"fontsize": 9})
    ax.set_title(f"Έξοδα ανά κατηγορία — {MONTH_LABELS[month - 1]} {year}")
    return fig


def income_vs_expense_bars(
    db: FinanceDB,
    year: int,
    *,
    user_id: Optional[int] = None,
) -> Figure:
    summary = db.yearly_monthly_summary(year, user_id=user_id)
    months = [MONTH_LABELS[s["month"] - 1] for s in summary]
    income = [s["income"] for s in summary]
    expense = [s["expense"] for s in summary]

    fig, ax = plt.subplots(figsize=(7, 4), dpi=100)
    x = range(len(months))
    width = 0.35
    ax.bar([i - width / 2 for i in x], income, width, label="Έσοδα", color=CHART_COLORS["income"])
    ax.bar([i + width / 2 for i in x], expense, width, label="Έξοδα", color=CHART_COLORS["expense"])
    ax.set_xticks(list(x))
    ax.set_xticklabels(months, rotation=45, ha="right")
    ax.set_ylabel("Ποσό (€)")
    ymax = max(income + expense + [1])
    ax.set_ylim(0, ymax * 1.15)
    ax.legend(loc="upper right")
    ax.set_title(f"Έσοδα vs Έξοδα — {year}")
    ax.grid(axis="y", alpha=0.3)
    return fig


def expenses_over_time_line(
    db: FinanceDB,
    start_year: int,
    start_month: int,
    end_year: int,
    end_month: int,
    *,
    category_id: Optional[int] = None,
    user_id: Optional[int] = None,
    category_name: Optional[str] = None,
) -> Figure:
    series = db.expense_series_by_month(
        start_year, start_month, end_year, end_month,
        category_id=category_id, user_id=user_id,
    )
    lookup = {(r["year"], r["month"]): r["total"] for r in series}
    labels: list[str] = []
    values: list[float] = []
    for y, m in month_range_iter(start_year, start_month, end_year, end_month):
        labels.append(f"{MONTH_LABELS[m - 1]} {y}")
        values.append(lookup.get((y, m), 0.0))

    fig, ax = plt.subplots(figsize=(7, 4), dpi=100)
    if not any(values):
        ax.text(0.5, 0.5, "Δεν υπάρχουν έξοδα στο διάστημα", ha="center", va="center", fontsize=12, color="#64748b")
        ax.set_axis_off()
        ax.set_title("Έξοδα σε χρονικό εύρος")
        return fig

    ax.plot(labels, values, marker="o", linewidth=2, color=CHART_COLORS["accent"], markersize=5)
    ax.fill_between(range(len(labels)), values, alpha=0.12, color=CHART_COLORS["accent"])
    ax.set_ylabel("Ποσό (€)")
    cat_label = category_name or "Όλες οι κατηγορίες"
    ax.set_title(f"Έξοδα — {cat_label}\n{MONTH_LABELS[start_month - 1]} {start_year} – {MONTH_LABELS[end_month - 1]} {end_year}")
    ax.tick_params(axis="x", rotation=45)
    ax.grid(axis="y", alpha=0.3)
    plt.setp(ax.get_xticklabels(), ha="right")
    return fig


def default_year() -> int:
    return date.today().year


def default_month() -> int:
    return date.today().month
