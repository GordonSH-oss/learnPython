"""Small pandas data-cleaning workflow.

Run:
    python 13-data-science/pandas_workflow.py
"""

from __future__ import annotations


try:
    import pandas as pd
except ImportError as exc:  # pragma: no cover - educational dependency hint
    raise SystemExit("Install dependencies with: python -m pip install -r requirements/data.txt") from exc


def build_orders() -> "pd.DataFrame":
    return pd.DataFrame(
        [
            {"user_id": "u1", "amount": "19.9", "paid": "yes"},
            {"user_id": "u2", "amount": "88", "paid": "yes"},
            {"user_id": "u1", "amount": None, "paid": "no"},
            {"user_id": "u3", "amount": "-5", "paid": "yes"},
        ]
    )


def clean_orders(df: "pd.DataFrame") -> "pd.DataFrame":
    cleaned = df.copy()
    cleaned["amount"] = pd.to_numeric(cleaned["amount"], errors="coerce").fillna(0)
    cleaned["paid"] = cleaned["paid"].map({"yes": True, "no": False})
    cleaned = cleaned[cleaned["amount"] >= 0]
    return cleaned


def summarize_by_user(df: "pd.DataFrame") -> "pd.DataFrame":
    return (
        df.groupby("user_id", as_index=False)
        .agg(total_amount=("amount", "sum"), order_count=("amount", "size"), paid_orders=("paid", "sum"))
        .sort_values("total_amount", ascending=False)
    )


def main() -> None:
    orders = build_orders()
    cleaned = clean_orders(orders)
    summary = summarize_by_user(cleaned)
    print(summary)


if __name__ == "__main__":
    main()
