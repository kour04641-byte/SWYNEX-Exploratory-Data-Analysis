"""Exploratory data analysis of the cleaned cafe sales data (output of Task 1).

Run:  python eda.py
Creates: charts/*.png, outputs/summary_statistics.csv, outputs/key_findings.md
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

DATA, CHARTS, OUT = Path("data/cleaned_cafe_sales.csv"), Path("charts"), Path("outputs")
ACCENT, GREY, INK = "#3b3ee8", "#c9ced8", "#14163a"
DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "font.size": 11,
                     "axes.titleweight": "bold", "axes.titlesize": 14, "axes.titlelocation": "left"})


def save(fig: plt.Figure, name: str) -> None:
    fig.tight_layout()
    fig.savefig(CHARTS / name, dpi=150)
    plt.close(fig)


def load() -> pd.DataFrame:
    return pd.read_csv(DATA, parse_dates=["transaction_date"])


def item_summary(sales: pd.DataFrame) -> pd.DataFrame:
    g = sales[sales["item"] != "Unknown"].groupby("item").agg(
        revenue=("total_spent", "sum"), orders=("total_spent", "size"),
        units=("quantity", "sum"), price=("price_per_unit", "first"))
    g["revenue_share_pct"] = 100 * g["revenue"] / sales["total_spent"].sum()
    return g.sort_values("revenue", ascending=False)


def chart_items(items: pd.DataFrame) -> None:
    order = items.index[::-1]
    fig, ax = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
    ax[0].barh(order, items.loc[order, "orders"], color=GREY)
    ax[0].set_title("Orders per item")
    for i, v in enumerate(items.loc[order, "orders"]):
        ax[0].text(v + 10, i, f"{v:,}", va="center")
    ax[1].barh(order, items.loc[order, "revenue"], color=ACCENT)
    ax[1].set_title("Revenue per item ($)")
    for i, (v, s) in enumerate(zip(items.loc[order, "revenue"], items.loc[order, "revenue_share_pct"])):
        ax[1].text(v + 150, i, f"${v:,.0f} ({s:.1f}%)", va="center")
    ax[0].set_xlim(0, 1550); ax[1].set_xlim(0, 25000)
    save(fig, "1_items_orders_vs_revenue.png")


def chart_monthly(dated: pd.DataFrame) -> pd.Series:
    daily = dated.groupby("transaction_date")["total_spent"].sum()
    monthly = daily.groupby(daily.index.to_period("M")).mean()
    fig, ax = plt.subplots(figsize=(10, 4.6))
    ax.plot(monthly.index.strftime("%b"), monthly.values, marker="o", color=ACCENT, linewidth=2.5)
    ax.set_ylim(0, monthly.max() * 1.3); ax.set_ylabel("Average daily revenue ($)")
    ax.set_title("Daily revenue is flat across 2023 (no seasonality)")
    for x, y in zip(monthly.index.strftime("%b"), monthly.values):
        ax.text(x, y + 12, f"{y:,.0f}", ha="center", fontsize=9)
    save(fig, "2_monthly_daily_revenue.png")
    return monthly


def chart_weekday(dated: pd.DataFrame) -> pd.Series:
    daily = dated.groupby("transaction_date")["total_spent"].sum()
    wd = daily.groupby(daily.index.day_name()).mean().reindex(DAYS)
    fig, ax = plt.subplots(figsize=(9, 4.6))
    colors = [ACCENT if d == wd.idxmax() else GREY for d in DAYS]
    ax.bar(DAYS, wd.values, color=colors)
    ax.set_ylim(0, wd.max() * 1.2); ax.set_ylabel("Average daily revenue ($)")
    ax.set_title("Average daily revenue by weekday")
    for i, v in enumerate(wd.values):
        ax.text(i, v + 4, f"{v:,.0f}", ha="center")
    save(fig, "3_weekday_revenue.png")
    return wd


def chart_channels(sales: pd.DataFrame) -> None:
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.6))
    for a, col, title in ((ax[0], "location", "Revenue by location"), (ax[1], "payment_method", "Revenue by payment method")):
        known = sales[sales[col] != "Unknown"].groupby(col)["total_spent"].sum().sort_values()
        a.barh(known.index, known.values, color=ACCENT)
        a.set_title(title)
        for i, v in enumerate(known.values):
            a.text(v + 200, i, f"${v:,.0f} ({100 * v / known.sum():.1f}%)", va="center")
        a.set_xlim(0, known.max() * 1.45)
        a.text(0, -0.2, f"{100 * (sales[col] == 'Unknown').mean():.1f}% of orders have an unknown {col.replace('_', ' ')}",
               transform=a.transAxes, fontsize=9, color="#667085")
    save(fig, "4_location_and_payment.png")


def chart_order_value(sales: pd.DataFrame, items: pd.DataFrame) -> int:
    order = list(items.sort_values("price").index)
    data = [sales.loc[sales["item"] == i, "total_spent"].dropna() for i in order]
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.boxplot(data, tick_labels=[f"{i}\n(${items.loc[i, 'price']:g})" for i in order], patch_artist=True,
               boxprops=dict(facecolor="#dfe0fb", color=ACCENT), medianprops=dict(color=INK), whiskerprops=dict(color=ACCENT),
               capprops=dict(color=ACCENT), flierprops=dict(marker="o", markerfacecolor="#d6334a"))
    ax.set_ylabel("Order value ($)"); ax.set_title("Order value by item: no outliers beyond each item's range")
    outliers = 0
    for s in data:
        q1, q3 = s.quantile([.25, .75]); outliers += int(((s < q1 - 1.5 * (q3 - q1)) | (s > q3 + 1.5 * (q3 - q1))).sum())
    save(fig, "5_order_value_by_item.png")
    return outliers


def chart_completeness(df: pd.DataFrame) -> pd.Series:
    known = pd.Series({
        "Quantity": df["quantity"].notna().mean(), "Price": df["price_per_unit"].notna().mean(),
        "Total spent": df["total_spent"].notna().mean(), "Item": (df["item"] != "Unknown").mean(),
        "Date": df["transaction_date"].notna().mean(), "Payment method": (df["payment_method"] != "Unknown").mean(),
        "Location": (df["location"] != "Unknown").mean()}).sort_values() * 100
    fig, ax = plt.subplots(figsize=(8, 4.6))
    ax.barh(known.index, known.values, color=[ACCENT if v >= 90 else "#d6334a" for v in known.values])
    ax.set_xlim(0, 112); ax.set_title("Share of orders with a known value")
    for i, v in enumerate(known.values):
        ax.text(v + 1, i, f"{v:.1f}%", va="center")
    save(fig, "6_data_completeness.png")
    return known


def main() -> None:
    CHARTS.mkdir(exist_ok=True); OUT.mkdir(exist_ok=True)
    df = load()
    sales = df.dropna(subset=["total_spent"])
    dated = sales.dropna(subset=["transaction_date"])

    stats = df[["quantity", "price_per_unit", "total_spent"]].describe().T
    stats["median"] = df[["quantity", "price_per_unit", "total_spent"]].median()
    stats.round(2).to_csv(OUT / "summary_statistics.csv")

    items = item_summary(sales)
    chart_items(items)
    monthly = chart_monthly(dated)
    weekday = chart_weekday(dated)
    chart_channels(sales)
    outliers = chart_order_value(sales, items)
    known = chart_completeness(df)

    loc = sales[sales["location"] != "Unknown"].groupby("location")["total_spent"].sum()
    pay = sales[sales["payment_method"] != "Unknown"].groupby("payment_method")["total_spent"].sum()
    corr = sales[["quantity", "price_per_unit", "total_spent"]].corr().round(2)
    lines = [
        f"Orders with a total: {len(sales):,} | revenue: ${sales['total_spent'].sum():,.0f}",
        f"Average order value: ${sales['total_spent'].mean():.2f} | median: ${sales['total_spent'].median():.2f} | max: ${sales['total_spent'].max():.2f}",
        f"Top 3 items share: {items['revenue_share_pct'].head(3).sum():.1f}% | bottom 3: {items['revenue_share_pct'].tail(3).sum():.1f}%",
        f"Most orders: {items['orders'].idxmax()} ({items['orders'].max():,}) | fewest: {items['orders'].idxmin()} ({items['orders'].min():,})",
        f"Avg daily revenue by month: min {monthly.min():.0f} ({monthly.idxmin()}) max {monthly.max():.0f} ({monthly.idxmax()})",
        f"Avg daily revenue by weekday: min {weekday.min():.0f} ({weekday.idxmin()}) max {weekday.max():.0f} ({weekday.idxmax()})",
        f"Location revenue split: {(100 * loc / loc.sum()).round(1).to_dict()}",
        f"Payment revenue split: {(100 * pay / pay.sum()).round(1).to_dict()}",
        f"IQR outliers in order value within items: {outliers}",
        f"Correlation with total_spent: quantity {corr.loc['quantity', 'total_spent']}, price {corr.loc['price_per_unit', 'total_spent']}",
        f"Known-value share (%): {known.round(1).to_dict()}",
    ]
    (OUT / "key_findings.md").write_text("\n".join(f"- {l}" for l in lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
