# SWYNEX Exploratory Data Analysis: Cafe Sales

Exploratory analysis of the cleaned cafe sales dataset from Task 1 ([SWYNEX-Data-Cleaning-Preparation](https://github.com/kour04641-byte/SWYNEX-Data-Cleaning-Preparation)). The dataset is synthetic practice data from Kaggle, so some patterns are flatter than real-world sales would be.

## Dataset at a glance
- 9,999 cleaned transactions in 2023 (1 Jan to 31 Dec); 9,977 have an order total
- **Total revenue: $89,096** | **average order value: $8.93** | median: $8.00 | range: $1.00 to $25.00
- Summary statistics: `outputs/summary_statistics.csv` | all key numbers: `outputs/key_findings.md`

## Five insights

### 1. Revenue is driven by price, not popularity
Every item sells a similar number of orders (1,094 to 1,286), but revenue differs a lot. Coffee has the **most orders (1,286)** yet only **8.8%** of revenue. Salad has about the same number of orders (1,270) but brings **21.4% ($19,095)** because it costs $5.

![items](charts/1_items_orders_vs_revenue.png)

### 2. Three items carry half the revenue
Salad, Sandwich and Smoothie make up **51.8%** of revenue. Coffee, Tea and Cookie make up **39% of orders but only 18.9% of revenue**. Selling more low-priced items does not move revenue much; selling a higher-priced item does.

### 3. Sales are steady all year, with no seasonality
Average daily revenue stays between **$222 (July) and $245 (June)** across months, and between **$225 (Wednesday) and $238 (Thursday)** across weekdays, a spread of only about 6%. There is no peak season or weak day to plan around, so staffing and stock can be steady.

![monthly](charts/2_monthly_daily_revenue.png)
![weekday](charts/3_weekday_revenue.png)

### 4. In-store and takeaway are balanced, and so are payment methods
In-store brings 50.6% of revenue and takeaway 49.4%. Cash, credit card and digital wallet each bring about one third (33.3%, 33.4%, 33.3%). No channel dominates, so none can be cut without losing a large share of sales.

![channels](charts/4_location_and_payment.png)

### 5. No anomalies, and both quantity and price drive order value
Order values range from $1 to $25. Within each item there are **0 statistical outliers** (IQR rule), and the largest order, $25, is simply 5 salads at $5. Quantity is spread evenly from 1 to 5, and it is unrelated to price (correlation 0.01), so order value depends equally on how many you buy (correlation 0.70) and what you buy (0.65).

![box](charts/5_order_value_by_item.png)

## Data quality limit
Location is unknown for 39.6% of orders and payment method for 31.8%, so insight 4 is based on the known orders only. Capturing these two fields at checkout would make channel analysis far more reliable.

![complete](charts/6_data_completeness.png)

## Recommendations
- Feature and promote Salad, Sandwich and Smoothie, since price makes them the revenue leaders.
- Bundle low-priced items (Cookie, Tea) with high-priced ones to lift the $8.93 average order.
- Record location and payment method on every sale.

## Method
Python (pandas and matplotlib). Rows without an order total were excluded from revenue figures, and rows without a date from the monthly and weekday views (about 4.6% of rows). Daily averages are used instead of totals so months and weekdays with different numbers of days compare fairly.

## Run it
```bash
pip install -r requirements.txt
python eda.py
```
This recreates every chart in `charts/` and the files in `outputs/`.
