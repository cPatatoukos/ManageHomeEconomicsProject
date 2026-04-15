from __future__ import annotations

import hashlib
import hmac
import secrets
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Generator, Iterable, Optional

DEFAULT_DB_PATH = Path(__file__).resolve().parent / "finance.db"
_SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"

_ITERATIONS = 120_000


class FinanceDBError(Exception):
    pass


class NotFoundError(FinanceDBError):
    pass


class DuplicateUsernameError(FinanceDBError):
    pass


class CategoryInUseError(FinanceDBError):
    pass


class InvalidCredentialsError(FinanceDBError):
    pass


def _hash_password(password: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _ITERATIONS)


def _connect(path: Path | str) -> sqlite3.Connection:
    conn = sqlite3.connect(str(path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@dataclass
class FinanceDB:
    db_path: Path = DEFAULT_DB_PATH

    def __post_init__(self) -> None:
        self.db_path = Path(self.db_path)

    @contextmanager
    def connection(self) -> Generator[sqlite3.Connection, None, None]:
        conn = _connect(self.db_path)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def initialize(self, *, force_reload_schema: bool = False) -> None:
        # --- Καθαρή επανεκκίνηση ---
        if force_reload_schema and self.db_path.exists():
            self.db_path.unlink()
        sql = _SCHEMA_PATH.read_text(encoding="utf-8")
        with self.connection() as conn:
            conn.executescript(sql)

    # --- Χρήστες ---
    def create_user(self, username: str, password: str) -> int:
        username = username.strip()
        if not username:
            raise ValueError("Username cannot be empty.")
        salt = secrets.token_bytes(16)
        phash = _hash_password(password, salt)
        try:
            with self.connection() as conn:
                cur = conn.execute(
                    "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
                    (username, phash, salt),
                )
                return int(cur.lastrowid)
        except sqlite3.IntegrityError as e:
            if "username" in str(e).lower() or "unique" in str(e).lower():
                raise DuplicateUsernameError(username) from e
            raise

    def verify_user(self, username: str, password: str) -> dict[str, Any]:
        with self.connection() as conn:
            row = conn.execute(
                "SELECT id, username, password_hash, salt, created_at FROM users WHERE username = ?",
                (username.strip(),),
            ).fetchone()
        if row is None:
            raise InvalidCredentialsError()
        computed = _hash_password(password, row["salt"])
        stored = row["password_hash"]
        try:
            if not hmac.compare_digest(computed, bytes(stored)):
                raise InvalidCredentialsError()
        except TypeError:
            raise InvalidCredentialsError()
        return {
            "id": row["id"],
            "username": row["username"],
            "created_at": row["created_at"],
        }

    def get_user(self, user_id: int) -> dict[str, Any]:
        with self.connection() as conn:
            row = conn.execute(
                "SELECT id, username, created_at FROM users WHERE id = ?", (user_id,)
            ).fetchone()
        if row is None:
            raise NotFoundError(f"user id={user_id}")
        return dict(row)

    def list_users(self) -> list[dict[str, Any]]:
        with self.connection() as conn:
            rows = conn.execute(
                "SELECT id, username, created_at FROM users ORDER BY username"
            ).fetchall()
        return [dict(r) for r in rows]

    def update_user(
        self,
        user_id: int,
        *,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None:
        sets: list[str] = []
        args: list[Any] = []
        if username is not None:
            u = username.strip()
            if not u:
                raise ValueError("Username cannot be empty.")
            sets.append("username = ?")
            args.append(u)
        if password is not None:
            salt = secrets.token_bytes(16)
            sets.append("password_hash = ?")
            sets.append("salt = ?")
            args.extend([_hash_password(password, salt), salt])
        if not sets:
            return
        args.append(user_id)
        try:
            with self.connection() as conn:
                cur = conn.execute(
                    f"UPDATE users SET {', '.join(sets)} WHERE id = ?", args
                )
                if cur.rowcount == 0:
                    raise NotFoundError(f"user id={user_id}")
        except sqlite3.IntegrityError as e:
            raise DuplicateUsernameError(username or "") from e

    def delete_user(self, user_id: int) -> None:
        with self.connection() as conn:
            cur = conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
            if cur.rowcount == 0:
                raise NotFoundError(f"user id={user_id}")

    # --- Κατηγορίες ---
    def create_category(self, name: str, kind: str) -> int:
        kind = kind.strip().lower()
        if kind not in ("income", "expense"):
            raise ValueError("kind must be 'income' or 'expense'.")
        name = name.strip()
        if not name:
            raise ValueError("Category name cannot be empty.")
        try:
            with self.connection() as conn:
                cur = conn.execute(
                    "INSERT INTO categories (name, kind) VALUES (?, ?)",
                    (name, kind),
                )
                return int(cur.lastrowid)
        except sqlite3.IntegrityError as e:
            raise FinanceDBError(f"Category '{name}' ({kind}) already exists.") from e

    def get_category(self, category_id: int) -> dict[str, Any]:
        with self.connection() as conn:
            row = conn.execute("SELECT * FROM categories WHERE id = ?", (category_id,)).fetchone()
        if row is None:
            raise NotFoundError(f"category id={category_id}")
        return dict(row)

    def list_categories(self, kind: Optional[str] = None) -> list[dict[str, Any]]:
        if kind:
            kind = kind.strip().lower()
            if kind not in ("income", "expense"):
                raise ValueError("kind must be income/expense.")
            q = "SELECT * FROM categories WHERE kind = ? ORDER BY name"
            params: tuple[Any, ...] = (kind,)
        else:
            q = "SELECT * FROM categories ORDER BY kind, name"
            params = ()
        with self.connection() as conn:
            rows = conn.execute(q, params).fetchall()
        return [dict(r) for r in rows]

    def update_category(
        self,
        category_id: int,
        *,
        name: Optional[str] = None,
        kind: Optional[str] = None,
    ) -> None:
        sets: list[str] = []
        args: list[Any] = []
        if name is not None:
            n = name.strip()
            if not n:
                raise ValueError("Category name cannot be empty.")
            sets.append("name = ?")
            args.append(n)
        if kind is not None:
            k = kind.strip().lower()
            if k not in ("income", "expense"):
                raise ValueError("Invalid kind.")
            sets.append("kind = ?")
            args.append(k)
        if not sets:
            return
        args.append(category_id)
        try:
            with self.connection() as conn:
                cur = conn.execute(
                    f"UPDATE categories SET {', '.join(sets)} WHERE id = ?", args
                )
                if cur.rowcount == 0:
                    raise NotFoundError(f"category id={category_id}")
        except sqlite3.IntegrityError as e:
            raise FinanceDBError("Category name/kind conflict.") from e

    def delete_category(self, category_id: int) -> None:
        self._ensure_category_unused(category_id)
        with self.connection() as conn:
            cur = conn.execute("DELETE FROM categories WHERE id = ?", (category_id,))
            if cur.rowcount == 0:
                raise NotFoundError(f"category id={category_id}")

    def _ensure_category_unused(self, category_id: int) -> None:
        with self.connection() as conn:
            t = conn.execute(
                "SELECT COUNT(*) AS c FROM transactions WHERE category_id = ?", (category_id,)
            ).fetchone()["c"]
            r = conn.execute(
                "SELECT COUNT(*) AS c FROM recurring_templates WHERE category_id = ?", (category_id,)
            ).fetchone()["c"]
        if t or r:
            raise CategoryInUseError(
                f"Category {category_id} is in use ({t} transactions, {r} templates)."
            )

    # --- Μηνιαία πρότυπα ---
    def create_recurring_template(
        self,
        category_id: int,
        user_id: int,
        title: str,
        amount: float,
        *,
        is_active: bool = True,
    ) -> int:
        self._require_category(category_id)
        title = title.strip()
        if not title:
            raise ValueError("Title cannot be empty.")
        if amount <= 0:
            raise ValueError("Amount must be positive.")
        with self.connection() as conn:
            cur = conn.execute(
                """
                INSERT INTO recurring_templates (category_id, user_id, title, amount, is_active)
                VALUES (?, ?, ?, ?, ?)
                """,
                (category_id, user_id, title, float(amount), 1 if is_active else 0),
            )
            return int(cur.lastrowid)

    def get_recurring_template(self, template_id: int) -> dict[str, Any]:
        with self.connection() as conn:
            row = conn.execute(
                "SELECT * FROM recurring_templates WHERE id = ?", (template_id,)
            ).fetchone()
        if row is None:
            raise NotFoundError(f"recurring_template id={template_id}")
        return dict(row)

    def list_recurring_templates(
        self,
        *,
        user_id: Optional[int] = None,
        active_only: bool = False,
    ) -> list[dict[str, Any]]:
        q = "SELECT * FROM recurring_templates WHERE 1=1"
        args: list[Any] = []
        if user_id is not None:
            q += " AND user_id = ?"
            args.append(user_id)
        if active_only:
            q += " AND is_active = 1"
        q += " ORDER BY id"
        with self.connection() as conn:
            rows = conn.execute(q, args).fetchall()
        return [dict(r) for r in rows]

    def update_recurring_template(
        self,
        template_id: int,
        *,
        category_id: Optional[int] = None,
        title: Optional[str] = None,
        amount: Optional[float] = None,
        is_active: Optional[bool] = None,
    ) -> None:
        sets: list[str] = []
        args: list[Any] = []
        if category_id is not None:
            self._require_category(category_id)
            sets.append("category_id = ?")
            args.append(category_id)
        if title is not None:
            t = title.strip()
            if not t:
                raise ValueError("Title cannot be empty.")
            sets.append("title = ?")
            args.append(t)
        if amount is not None:
            if amount <= 0:
                raise ValueError("Invalid amount.")
            sets.append("amount = ?")
            args.append(float(amount))
        if is_active is not None:
            sets.append("is_active = ?")
            args.append(1 if is_active else 0)
        if not sets:
            return
        args.append(template_id)
        with self.connection() as conn:
            cur = conn.execute(
                f"UPDATE recurring_templates SET {', '.join(sets)} WHERE id = ?", args
            )
            if cur.rowcount == 0:
                raise NotFoundError(f"recurring_template id={template_id}")

    def delete_recurring_template(self, template_id: int) -> None:
        with self.connection() as conn:
            cur = conn.execute("DELETE FROM recurring_templates WHERE id = ?", (template_id,))
            if cur.rowcount == 0:
                raise NotFoundError(f"recurring_template id={template_id}")

    def _require_category(self, category_id: int) -> None:
        with self.connection() as conn:
            row = conn.execute(
                "SELECT id FROM categories WHERE id = ?", (category_id,)
            ).fetchone()
        if row is None:
            raise NotFoundError(f"category id={category_id}")

    # --- Συναλλαγές ---
    def create_transaction(
        self,
        category_id: int,
        user_id: int,
        title: str,
        amount: float,
        year: int,
        month: int,
        *,
        is_monthly: bool = False,
    ) -> int:
        title = title.strip()
        if not title:
            raise ValueError("Title cannot be empty.")
        if amount <= 0:
            raise ValueError("Amount must be positive.")
        self._require_category(category_id)
        y, m = int(year), int(month)
        if m < 1 or m > 12:
            raise ValueError("Invalid month.")

        with self.connection() as conn:
            if not is_monthly:
                cur = conn.execute(
                    """
                    INSERT INTO transactions
                    (category_id, user_id, title, amount, year, month, recurring_template_id)
                    VALUES (?, ?, ?, ?, ?, ?, NULL)
                    """,
                    (category_id, user_id, title, float(amount), y, m),
                )
                return int(cur.lastrowid)

            cur_t = conn.execute(
                """
                INSERT INTO recurring_templates (category_id, user_id, title, amount, is_active)
                VALUES (?, ?, ?, ?, 1)
                """,
                (category_id, user_id, title, float(amount)),
            )
            tid = int(cur_t.lastrowid)
            cur = conn.execute(
                """
                INSERT INTO transactions
                (category_id, user_id, title, amount, year, month, recurring_template_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (category_id, user_id, title, float(amount), y, m, tid),
            )
            return int(cur.lastrowid)

    def get_transaction(self, transaction_id: int) -> dict[str, Any]:
        with self.connection() as conn:
            row = conn.execute(
                "SELECT * FROM transactions WHERE id = ?", (transaction_id,)
            ).fetchone()
        if row is None:
            raise NotFoundError(f"transaction id={transaction_id}")
        return dict(row)

    def list_transactions(
        self,
        year: int,
        month: int,
        *,
        category_id: Optional[int] = None,
        user_id: Optional[int] = None,
    ) -> list[dict[str, Any]]:
        q = """
            SELECT t.*, c.kind AS category_kind, c.name AS category_name
            FROM transactions t
            JOIN categories c ON c.id = t.category_id
            WHERE t.year = ? AND t.month = ?
        """
        args: list[Any] = [year, month]
        if category_id is not None:
            q += " AND t.category_id = ?"
            args.append(category_id)
        if user_id is not None:
            q += " AND t.user_id = ?"
            args.append(user_id)
        q += " ORDER BY c.kind DESC, c.name, t.title"
        with self.connection() as conn:
            rows = conn.execute(q, args).fetchall()
        return [dict(r) for r in rows]

    def update_transaction(
        self,
        transaction_id: int,
        *,
        category_id: Optional[int] = None,
        title: Optional[str] = None,
        amount: Optional[float] = None,
        year: Optional[int] = None,
        month: Optional[int] = None,
    ) -> None:
        if category_id is not None:
            self._require_category(category_id)
        sets: list[str] = []
        args: list[Any] = []
        if category_id is not None:
            sets.append("category_id = ?")
            args.append(category_id)
        if title is not None:
            t = title.strip()
            if not t:
                raise ValueError("Title cannot be empty.")
            sets.append("title = ?")
            args.append(t)
        if amount is not None:
            if amount <= 0:
                raise ValueError("Invalid amount.")
            sets.append("amount = ?")
            args.append(float(amount))
        if year is not None:
            sets.append("year = ?")
            args.append(int(year))
        if month is not None:
            mo = int(month)
            if mo < 1 or mo > 12:
                raise ValueError("Invalid month.")
            sets.append("month = ?")
            args.append(mo)
        if not sets:
            return
        args.append(transaction_id)
        with self.connection() as conn:
            cur = conn.execute(
                f"UPDATE transactions SET {', '.join(sets)} WHERE id = ?", args
            )
            if cur.rowcount == 0:
                raise NotFoundError(f"transaction id={transaction_id}")

    def delete_transaction(self, transaction_id: int) -> None:
        with self.connection() as conn:
            cur = conn.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
            if cur.rowcount == 0:
                raise NotFoundError(f"transaction id={transaction_id}")

    # --- Συγχρονισμός μήνα ---
    def sync_recurring_for_month(self, year: int, month: int) -> int:
        y, m = int(year), int(month)
        if m < 1 or m > 12:
            raise ValueError("Invalid month.")
        inserted = 0
        with self.connection() as conn:
            templates = conn.execute(
                """
                SELECT id, category_id, user_id, title, amount
                FROM recurring_templates
                WHERE is_active = 1
                """
            ).fetchall()
            for t in templates:
                exists = conn.execute(
                    """
                    SELECT 1 FROM transactions
                    WHERE recurring_template_id = ? AND year = ? AND month = ?
                    LIMIT 1
                    """,
                    (t["id"], y, m),
                ).fetchone()
                if exists:
                    continue
                conn.execute(
                    """
                    INSERT INTO transactions
                    (category_id, user_id, title, amount, year, month, recurring_template_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        t["category_id"],
                        t["user_id"],
                        t["title"],
                        t["amount"],
                        y,
                        m,
                        t["id"],
                    ),
                )
                inserted += 1
        return inserted

    # --- Αναφορές ---
    def monthly_totals(self, year: int, month: int) -> dict[str, float]:
        with self.connection() as conn:
            row = conn.execute(
                """
                SELECT
                    COALESCE(SUM(CASE WHEN c.kind = 'income' THEN t.amount END), 0) AS income,
                    COALESCE(SUM(CASE WHEN c.kind = 'expense' THEN t.amount END), 0) AS expense
                FROM transactions t
                JOIN categories c ON c.id = t.category_id
                WHERE t.year = ? AND t.month = ?
                """,
                (year, month),
            ).fetchone()
        income = float(row["income"])
        expense = float(row["expense"])
        return {"income": income, "expense": expense, "net": income - expense}

    def sum_by_category(
        self,
        year: int,
        month: int,
        *,
        kind: str,
    ) -> list[dict[str, Any]]:
        kind = kind.strip().lower()
        if kind not in ("income", "expense"):
            raise ValueError("kind must be income/expense.")
        with self.connection() as conn:
            rows = conn.execute(
                """
                SELECT c.id AS category_id, c.name AS category_name,
                       SUM(t.amount) AS total
                FROM transactions t
                JOIN categories c ON c.id = t.category_id
                WHERE t.year = ? AND t.month = ? AND c.kind = ?
                GROUP BY c.id, c.name
                ORDER BY total DESC
                """,
                (year, month, kind),
            ).fetchall()
        return [dict(r) for r in rows]

    def transactions_for_category_range(
        self,
        category_id: int,
        start_year: int,
        start_month: int,
        end_year: int,
        end_month: int,
    ) -> list[dict[str, Any]]:
        with self.connection() as conn:
            rows = conn.execute(
                """
                SELECT t.*, c.kind AS category_kind
                FROM transactions t
                JOIN categories c ON c.id = t.category_id
                WHERE t.category_id = ?
                  AND (t.year * 100 + t.month) >= (? * 100 + ?)
                  AND (t.year * 100 + t.month) <= (? * 100 + ?)
                ORDER BY t.year, t.month, t.id
                """,
                (category_id, start_year, start_month, end_year, end_month),
            ).fetchall()
        return [dict(r) for r in rows]


# --- Γεννήτρια (έτος, μήνας) σε κλειστό διάστημα ---
def month_range_iter(
    start_year: int, start_month: int, end_year: int, end_month: int
) -> Iterable[tuple[int, int]]:
    y, m = start_year, start_month
    while (y, m) <= (end_year, end_month):
        yield y, m
        m += 1
        if m > 12:
            m = 1
            y += 1


__all__ = [
    "FinanceDB",
    "FinanceDBError",
    "NotFoundError",
    "DuplicateUsernameError",
    "CategoryInUseError",
    "InvalidCredentialsError",
    "month_range_iter",
    "DEFAULT_DB_PATH",
]
