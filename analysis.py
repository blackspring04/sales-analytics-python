"""
=============================================================
  Sales Performance & Revenue Insights — Full Analysis
  Author : Harikrishna P P
  Tools  : Python, pandas, NumPy, matplotlib, seaborn
=============================================================
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import warnings, os

warnings.filterwarnings('ignore')
os.makedirs('charts', exist_ok=True)

# ── Colour palette ────────────────────────────────────────────────────────────
BLUE    = '#2C5F9E'
RED     = '#E05C3A'
GREEN   = '#2E9E6B'
YELLOW  = '#F5A623'
PURPLE  = '#7B5EA7'
GREY    = '#AAAAAA'
BG      = '#F8F9FB'
PALETTE = [BLUE, GREEN, YELLOW, RED, PURPLE, '#48B0D5', '#E8884A']

sns.set_theme(style='whitegrid', font='DejaVu Sans')
plt.rcParams.update({
    'axes.facecolor':  BG,
    'figure.facecolor': 'white',
    'axes.spines.top':   False,
    'axes.spines.right': False,
    'font.size': 10,
})

# ─────────────────────────────────────────────────────────────────────────────
# 1. LOAD & CLEAN
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("  STEP 1 — Loading & Cleaning Data")
print("="*60)

df = pd.read_csv('superstore_sales.csv', parse_dates=['Order Date','Ship Date'])

print(f"\nDataset shape  : {df.shape[0]:,} rows × {df.shape[1]} columns")
print(f"Date range     : {df['Order Date'].min().date()} → {df['Order Date'].max().date()}")
print(f"Missing values :\n{df.isnull().sum()[df.isnull().sum()>0]}")
print(f"Duplicate rows : {df.duplicated().sum()}")

# Derived columns
df['Year']          = df['Order Date'].dt.year
df['Month']         = df['Order Date'].dt.month
df['Month_Name']    = df['Order Date'].dt.strftime('%b')
df['YearMonth']     = df['Order Date'].dt.to_period('M')
df['Profit_Margin'] = (df['Profit'] / df['Sales'] * 100).round(2)
df['Ship_Days']     = (df['Ship Date'] - df['Order Date']).dt.days

print(f"\nDerived columns added: Year, Month, YearMonth, Profit_Margin, Ship_Days")
print(f"\nData types after cleaning:\n{df.dtypes}")

# ─────────────────────────────────────────────────────────────────────────────
# 2. EXECUTIVE SUMMARY METRICS
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("  STEP 2 — Executive Summary Metrics")
print("="*60)

total_sales   = df['Sales'].sum()
total_profit  = df['Profit'].sum()
total_orders  = df['Order ID'].nunique()
avg_order_val = df.groupby('Order ID')['Sales'].sum().mean()
overall_margin= (total_profit / total_sales * 100)
total_qty     = df['Quantity'].sum()

print(f"\n  Total Revenue     : ${total_sales:>12,.2f}")
print(f"  Total Profit      : ${total_profit:>12,.2f}")
print(f"  Overall Margin    : {overall_margin:>11.1f}%")
print(f"  Total Orders      : {total_orders:>12,}")
print(f"  Avg Order Value   : ${avg_order_val:>12,.2f}")
print(f"  Total Units Sold  : {total_qty:>12,}")

# ─────────────────────────────────────────────────────────────────────────────
# CHART 1 — Category Revenue vs Profit (side-by-side bar)
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("  CHART 1 — Category: Revenue vs Profit")
print("="*60)

cat_summary = df.groupby('Category').agg(
    Sales=('Sales','sum'), Profit=('Profit','sum')
).reset_index().sort_values('Sales', ascending=False)
cat_summary['Margin'] = (cat_summary['Profit']/cat_summary['Sales']*100).round(1)

print(cat_summary.to_string(index=False))

fig, ax = plt.subplots(figsize=(9,5))
x = np.arange(len(cat_summary))
w = 0.38
bars1 = ax.bar(x - w/2, cat_summary['Sales']/1000, w, label='Revenue ($K)', color=BLUE, zorder=3)
bars2 = ax.bar(x + w/2, cat_summary['Profit']/1000, w, label='Profit ($K)',  color=GREEN, zorder=3)

for bar, margin in zip(bars2, cat_summary['Margin']):
    ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+2,
            f'{margin}%', ha='center', va='bottom', fontsize=9, color=GREEN, fontweight='bold')

ax.set_xticks(x); ax.set_xticklabels(cat_summary['Category'], fontsize=11)
ax.set_ylabel('Amount ($K)', fontsize=10)
ax.set_title('Revenue vs Profit by Category\n(% labels = profit margin)', fontsize=13, fontweight='bold', pad=12)
ax.legend(fontsize=10); ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f'${v:,.0f}K'))
ax.grid(axis='y', alpha=0.4, zorder=0)
plt.tight_layout()
plt.savefig('charts/01_category_revenue_profit.png', dpi=150, bbox_inches='tight')
plt.close()
print("  -> Saved: charts/01_category_revenue_profit.png")

# ─────────────────────────────────────────────────────────────────────────────
# CHART 2 — Sub-Category Profit Margin (horizontal bar, highlight negatives)
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("  CHART 2 — Sub-Category Profit Margins")
print("="*60)

sub_summary = df.groupby(['Category','Sub-Category']).agg(
    Sales=('Sales','sum'), Profit=('Profit','sum')
).reset_index()
sub_summary['Margin'] = (sub_summary['Profit']/sub_summary['Sales']*100).round(1)
sub_summary = sub_summary.sort_values('Margin')

print(sub_summary[['Sub-Category','Sales','Profit','Margin']].to_string(index=False))

# Insight print
loss_makers = sub_summary[sub_summary['Margin'] < 0]
print(f"\n  INSIGHT: {len(loss_makers)} sub-categories operate at a LOSS:")
for _, r in loss_makers.iterrows():
    print(f"    {r['Sub-Category']:15s} margin = {r['Margin']:.1f}%  profit = ${r['Profit']:,.0f}")

fig, ax = plt.subplots(figsize=(10, 7))
colors_bar = [RED if m < 0 else (YELLOW if m < 8 else GREEN) for m in sub_summary['Margin']]
bars = ax.barh(sub_summary['Sub-Category'], sub_summary['Margin'], color=colors_bar, zorder=3)
ax.axvline(0, color='black', linewidth=0.8, linestyle='--')
for bar, val in zip(bars, sub_summary['Margin']):
    ax.text(val + (0.3 if val >= 0 else -0.3), bar.get_y()+bar.get_height()/2,
            f'{val:.1f}%', va='center', ha='left' if val >= 0 else 'right', fontsize=8.5)
ax.set_xlabel('Profit Margin (%)', fontsize=10)
ax.set_title('Profit Margin by Sub-Category\n(Red = loss-making, Yellow = low margin, Green = healthy)',
             fontsize=12, fontweight='bold', pad=12)
ax.grid(axis='x', alpha=0.3, zorder=0)
plt.tight_layout()
plt.savefig('charts/02_subcategory_margins.png', dpi=150, bbox_inches='tight')
plt.close()
print("  -> Saved: charts/02_subcategory_margins.png")

# ─────────────────────────────────────────────────────────────────────────────
# CHART 3 — Monthly Revenue Trend (line, all 4 years)
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("  CHART 3 — Monthly Revenue Trend by Year")
print("="*60)

monthly = df.groupby(['Year','Month'])['Sales'].sum().reset_index()
month_labels = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

fig, ax = plt.subplots(figsize=(12, 5))
year_colors = {2020: GREY, 2021: BLUE, 2022: YELLOW, 2023: RED}
for yr, grp in monthly.groupby('Year'):
    grp = grp.sort_values('Month')
    ax.plot(grp['Month'], grp['Sales']/1000, marker='o', linewidth=2.2,
            label=str(yr), color=year_colors[yr], markersize=5)
    # annotate Nov & Dec for 2023
    if yr == 2023:
        for _, row in grp[grp['Month'].isin([11,12])].iterrows():
            ax.annotate(f"${row['Sales']/1000:.0f}K",
                        (row['Month'], row['Sales']/1000),
                        textcoords='offset points', xytext=(0,8),
                        ha='center', fontsize=8, color=RED)

ax.set_xticks(range(1,13)); ax.set_xticklabels(month_labels)
ax.set_ylabel('Revenue ($K)', fontsize=10)
ax.set_title('Monthly Revenue Trend 2020–2023\n(Q4 seasonality clearly visible)', fontsize=13, fontweight='bold', pad=12)
ax.legend(title='Year', fontsize=10); ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f'${v:,.0f}K'))
ax.grid(alpha=0.3, zorder=0)
plt.tight_layout()
plt.savefig('charts/03_monthly_revenue_trend.png', dpi=150, bbox_inches='tight')
plt.close()

q4_pct = df[df['Month'].isin([10,11,12])]['Sales'].sum() / total_sales * 100
print(f"\n  INSIGHT: Q4 (Oct–Dec) contributes {q4_pct:.1f}% of annual revenue")
print("  -> Saved: charts/03_monthly_revenue_trend.png")

# ─────────────────────────────────────────────────────────────────────────────
# CHART 4 — Regional Performance (Sales, Profit, Margin)
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("  CHART 4 — Regional Performance")
print("="*60)

region_summary = df.groupby('Region').agg(
    Sales=('Sales','sum'), Profit=('Profit','sum'), Orders=('Order ID','nunique')
).reset_index()
region_summary['Margin'] = (region_summary['Profit']/region_summary['Sales']*100).round(1)
region_summary['AOV']    = (region_summary['Sales']/region_summary['Orders']).round(0)
region_summary = region_summary.sort_values('Sales', ascending=False)
print(region_summary.to_string(index=False))

fig, axes = plt.subplots(1, 3, figsize=(13, 5))
metrics = [('Sales','Revenue ($K)', BLUE), ('Profit','Profit ($K)', GREEN), ('Margin','Profit Margin (%)', YELLOW)]
for ax, (col, label, color) in zip(axes, metrics):
    vals = region_summary[col] / (1000 if col != 'Margin' else 1)
    bars = ax.bar(region_summary['Region'], vals, color=color, zorder=3, edgecolor='white')
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.3,
                f'{"$" if col!="Margin" else ""}{v:.1f}{"%" if col=="Margin" else "K"}',
                ha='center', va='bottom', fontsize=9, fontweight='bold')
    ax.set_title(label, fontsize=11, fontweight='bold'); ax.set_xlabel('')
    ax.grid(axis='y', alpha=0.3, zorder=0); ax.tick_params(axis='x', labelsize=9)

fig.suptitle('Regional Performance: Revenue, Profit & Margin', fontsize=13, fontweight='bold', y=1.01)
plt.tight_layout()
plt.savefig('charts/04_regional_performance.png', dpi=150, bbox_inches='tight')
plt.close()
print("  -> Saved: charts/04_regional_performance.png")

# ─────────────────────────────────────────────────────────────────────────────
# CHART 5 — Discount vs Profit Scatter
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("  CHART 5 — Discount Impact on Profit")
print("="*60)

disc_profit = df.groupby('Discount').agg(
    Avg_Profit=('Profit','mean'), Count=('Sales','count')
).reset_index()
print(disc_profit.to_string(index=False))

corr = df['Discount'].corr(df['Profit'])
print(f"\n  INSIGHT: Pearson correlation Discount vs Profit = {corr:.3f}")
print(f"  Orders with discount > 0.2 have avg profit: ${df[df['Discount']>0.2]['Profit'].mean():.2f}")
print(f"  Orders with no discount have avg profit:     ${df[df['Discount']==0]['Profit'].mean():.2f}")

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# Scatter sample
sample = df.sample(2000, random_state=42)
cat_color_map = {'Furniture': BLUE, 'Office Supplies': GREEN, 'Technology': YELLOW}
for cat, grp in sample.groupby('Category'):
    axes[0].scatter(grp['Discount'], grp['Profit'], alpha=0.25, s=15,
                    color=cat_color_map[cat], label=cat)
axes[0].axhline(0, color='red', linewidth=1, linestyle='--')
axes[0].set_xlabel('Discount Rate', fontsize=10); axes[0].set_ylabel('Profit ($)', fontsize=10)
axes[0].set_title(f'Discount vs Profit per Transaction\n(correlation = {corr:.2f})', fontsize=11, fontweight='bold')
axes[0].legend(fontsize=9)

# Bar: avg profit by discount tier
disc_profit_sorted = disc_profit.sort_values('Discount')
bar_colors = [GREEN if v >= 0 else RED for v in disc_profit_sorted['Avg_Profit']]
axes[1].bar(disc_profit_sorted['Discount'].astype(str), disc_profit_sorted['Avg_Profit'],
            color=bar_colors, zorder=3)
axes[1].axhline(0, color='black', linewidth=0.8, linestyle='--')
axes[1].set_xlabel('Discount Rate', fontsize=10); axes[1].set_ylabel('Avg Profit ($)', fontsize=10)
axes[1].set_title('Average Profit by Discount Level\n(Red bars = avg loss per order)', fontsize=11, fontweight='bold')
axes[1].grid(axis='y', alpha=0.3, zorder=0)

plt.tight_layout()
plt.savefig('charts/05_discount_profit_impact.png', dpi=150, bbox_inches='tight')
plt.close()
print("  -> Saved: charts/05_discount_profit_impact.png")

# ─────────────────────────────────────────────────────────────────────────────
# CHART 6 — Customer Segment Analysis
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("  CHART 6 — Customer Segment Analysis")
print("="*60)

seg_summary = df.groupby('Segment').agg(
    Sales=('Sales','sum'), Profit=('Profit','sum'),
    Orders=('Order ID','nunique'), Qty=('Quantity','sum')
).reset_index()
seg_summary['Margin'] = (seg_summary['Profit']/seg_summary['Sales']*100).round(1)
seg_summary['AOV']    = (seg_summary['Sales']/seg_summary['Orders']).round(0)
seg_summary['Revenue_Share'] = (seg_summary['Sales']/seg_summary['Sales'].sum()*100).round(1)
print(seg_summary.to_string(index=False))

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
seg_colors = [BLUE, GREEN, YELLOW]

# Pie — revenue share
wedges, texts, autotexts = axes[0].pie(
    seg_summary['Revenue_Share'], labels=seg_summary['Segment'],
    autopct='%1.1f%%', colors=seg_colors, startangle=140,
    wedgeprops={'edgecolor':'white','linewidth':2})
for at in autotexts: at.set_fontsize(10); at.set_fontweight('bold')
axes[0].set_title('Revenue Share by Segment', fontsize=12, fontweight='bold')

# Bar — margin comparison
bars = axes[1].bar(seg_summary['Segment'], seg_summary['Margin'], color=seg_colors, zorder=3)
for bar, v in zip(bars, seg_summary['Margin']):
    axes[1].text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.2,
                 f'{v:.1f}%', ha='center', fontsize=10, fontweight='bold')
axes[1].set_ylabel('Profit Margin (%)', fontsize=10)
axes[1].set_title('Profit Margin by Segment', fontsize=12, fontweight='bold')
axes[1].grid(axis='y', alpha=0.3, zorder=0)

plt.suptitle('Customer Segment Performance', fontsize=13, fontweight='bold', y=1.01)
plt.tight_layout()
plt.savefig('charts/06_segment_analysis.png', dpi=150, bbox_inches='tight')
plt.close()
print("  -> Saved: charts/06_segment_analysis.png")

# ─────────────────────────────────────────────────────────────────────────────
# CHART 7 — YoY Revenue Growth + Profit Trend
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("  CHART 7 — Year-over-Year Growth")
print("="*60)

yoy = df.groupby('Year').agg(Sales=('Sales','sum'), Profit=('Profit','sum')).reset_index()
yoy['Sales_Growth'] = yoy['Sales'].pct_change()*100
yoy['Profit_Growth']= yoy['Profit'].pct_change()*100
yoy['Margin']       = (yoy['Profit']/yoy['Sales']*100).round(1)
print(yoy.to_string(index=False))

fig, ax1 = plt.subplots(figsize=(10, 5))
ax2 = ax1.twinx()

bars = ax1.bar(yoy['Year'], yoy['Sales']/1000, color=BLUE, alpha=0.7, zorder=3, label='Revenue ($K)')
ax2.plot(yoy['Year'], yoy['Profit']/1000, color=GREEN, marker='o',
         linewidth=2.5, markersize=8, label='Profit ($K)', zorder=4)
ax2.plot(yoy['Year'], yoy['Margin'], color=RED, marker='s',
         linewidth=2, markersize=7, linestyle='--', label='Margin (%)', zorder=4)

for bar, row in zip(bars, yoy.itertuples()):
    ax1.text(bar.get_x()+bar.get_width()/2, bar.get_height()+3,
             f'${row.Sales/1000:.0f}K', ha='center', fontsize=9, fontweight='bold', color=BLUE)

ax1.set_ylabel('Revenue ($K)', fontsize=10, color=BLUE)
ax2.set_ylabel('Profit ($K) / Margin (%)', fontsize=10, color=GREEN)
ax1.set_title('Year-over-Year Revenue, Profit & Margin (2020–2023)',
              fontsize=13, fontweight='bold', pad=12)
ax1.set_xticks(yoy['Year'])
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1+lines2, labels1+labels2, loc='upper left', fontsize=9)
ax1.grid(axis='y', alpha=0.3, zorder=0)
plt.tight_layout()
plt.savefig('charts/07_yoy_growth.png', dpi=150, bbox_inches='tight')
plt.close()
print("  -> Saved: charts/07_yoy_growth.png")

# ─────────────────────────────────────────────────────────────────────────────
# CHART 8 — DASHBOARD (hero image — all key visuals in one figure)
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("  CHART 8 — Master Dashboard")
print("="*60)

fig = plt.figure(figsize=(18, 14), facecolor='white')
fig.suptitle('Sales Performance & Revenue Insights Dashboard\nHarikrishna P P  |  Python Data Analysis Project',
             fontsize=16, fontweight='bold', y=0.98)

gs = fig.add_gridspec(3, 3, hspace=0.52, wspace=0.38)

# ── KPI tiles (top row) ──────────────────────────────────────────────────────
kpi_ax = fig.add_subplot(gs[0, :])
kpi_ax.set_xlim(0,1); kpi_ax.set_ylim(0,1); kpi_ax.axis('off')
kpis = [
    ('Total Revenue',  f'${total_sales/1e6:.2f}M',  BLUE),
    ('Total Profit',   f'${total_profit/1000:.0f}K', GREEN),
    ('Profit Margin',  f'{overall_margin:.1f}%',      YELLOW),
    ('Total Orders',   f'{total_orders:,}',            PURPLE),
    ('Avg Order Value',f'${avg_order_val:.0f}',        RED),
]
for idx, (label, val, col) in enumerate(kpis):
    x = 0.08 + idx * 0.21
    kpi_ax.add_patch(plt.Rectangle((x-0.075, 0.1), 0.16, 0.8,
        facecolor=col, alpha=0.12, edgecolor=col, linewidth=1.5, transform=kpi_ax.transAxes))
    kpi_ax.text(x, 0.68, val,   ha='center', va='center', fontsize=17, fontweight='bold',
                color=col, transform=kpi_ax.transAxes)
    kpi_ax.text(x, 0.28, label, ha='center', va='center', fontsize=9, color='#444',
                transform=kpi_ax.transAxes)

# ── Category Revenue vs Profit ───────────────────────────────────────────────
ax1 = fig.add_subplot(gs[1, 0])
x = np.arange(len(cat_summary)); w = 0.38
ax1.bar(x-w/2, cat_summary['Sales']/1000, w, color=BLUE, label='Revenue', zorder=3)
ax1.bar(x+w/2, cat_summary['Profit']/1000, w, color=GREEN, label='Profit', zorder=3)
ax1.set_xticks(x); ax1.set_xticklabels(cat_summary['Category'], fontsize=8)
ax1.set_title('Category Revenue vs Profit', fontsize=10, fontweight='bold')
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f'${v:.0f}K'))
ax1.legend(fontsize=8); ax1.grid(axis='y', alpha=0.3, zorder=0)

# ── Monthly Trend ────────────────────────────────────────────────────────────
ax2 = fig.add_subplot(gs[1, 1])
for yr, grp in monthly.groupby('Year'):
    grp = grp.sort_values('Month')
    ax2.plot(grp['Month'], grp['Sales']/1000, marker='o', linewidth=1.8,
             label=str(yr), color=year_colors[yr], markersize=3)
ax2.set_xticks(range(1,13)); ax2.set_xticklabels(['J','F','M','A','M','J','J','A','S','O','N','D'], fontsize=8)
ax2.set_title('Monthly Revenue by Year', fontsize=10, fontweight='bold')
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f'${v:.0f}K'))
ax2.legend(fontsize=7); ax2.grid(alpha=0.3, zorder=0)

# ── Regional Performance ─────────────────────────────────────────────────────
ax3 = fig.add_subplot(gs[1, 2])
bars = ax3.bar(region_summary['Region'], region_summary['Sales']/1000,
               color=PALETTE[:4], zorder=3)
for bar, margin in zip(bars, region_summary['Margin']):
    ax3.text(bar.get_x()+bar.get_width()/2, bar.get_height()+1,
             f'{margin:.1f}%', ha='center', fontsize=8, color='#333', fontweight='bold')
ax3.set_title('Revenue by Region\n(label = margin)', fontsize=10, fontweight='bold')
ax3.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f'${v:.0f}K'))
ax3.grid(axis='y', alpha=0.3, zorder=0)

# ── Sub-category Margins ─────────────────────────────────────────────────────
ax4 = fig.add_subplot(gs[2, 0])
colors_bar = [RED if m < 0 else (YELLOW if m < 8 else GREEN) for m in sub_summary['Margin']]
ax4.barh(sub_summary['Sub-Category'], sub_summary['Margin'], color=colors_bar, zorder=3)
ax4.axvline(0, color='black', linewidth=0.7, linestyle='--')
ax4.set_title('Profit Margin by Sub-Category\n(Red=loss)', fontsize=10, fontweight='bold')
ax4.tick_params(axis='y', labelsize=7); ax4.grid(axis='x', alpha=0.3, zorder=0)

# ── Segment Pie ──────────────────────────────────────────────────────────────
ax5 = fig.add_subplot(gs[2, 1])
ax5.pie(seg_summary['Revenue_Share'], labels=seg_summary['Segment'],
        autopct='%1.1f%%', colors=[BLUE, GREEN, YELLOW],
        startangle=140, wedgeprops={'edgecolor':'white','linewidth':1.5},
        textprops={'fontsize':9})
ax5.set_title('Revenue Share by Segment', fontsize=10, fontweight='bold')

# ── YoY Bar ──────────────────────────────────────────────────────────────────
ax6 = fig.add_subplot(gs[2, 2])
ax6b = ax6.twinx()
ax6.bar(yoy['Year'], yoy['Sales']/1000, color=BLUE, alpha=0.7, zorder=3)
ax6b.plot(yoy['Year'], yoy['Margin'], color=RED, marker='s',
          linewidth=2, markersize=6, linestyle='--', zorder=4)
ax6.set_title('YoY Revenue & Margin', fontsize=10, fontweight='bold')
ax6.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v,_: f'${v:.0f}K'))
ax6b.set_ylabel('Margin %', fontsize=8, color=RED)
ax6.set_xticks(yoy['Year']); ax6.grid(axis='y', alpha=0.3, zorder=0)

plt.savefig('charts/00_dashboard.png', dpi=150, bbox_inches='tight')
plt.close()
print("  -> Saved: charts/00_dashboard.png")

# ─────────────────────────────────────────────────────────────────────────────
# FINAL INSIGHTS SUMMARY
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print("  BUSINESS INSIGHTS SUMMARY")
print("="*60)

top_region  = region_summary.iloc[0]
low_margin_sub = sub_summary[sub_summary['Margin']<0]['Sub-Category'].tolist()
best_segment   = seg_summary.sort_values('Margin',ascending=False).iloc[0]
disc_loss_pct  = (df[df['Discount']>=0.3]['Profit']<0).mean()*100

print(f"""
  1. REVENUE vs PROFIT GAP — Technology is the most profitable category
     ({cat_summary[cat_summary['Category']=='Technology']['Margin'].values[0]:.1f}% margin) despite Furniture
     generating comparable revenue with significantly lower margins.

  2. LOSS-MAKING SUB-CATEGORIES — {', '.join(low_margin_sub)} operate at negative
     profit margins and collectively represent a strategic risk worth reviewing.

  3. SEASONALITY — Q4 (Oct–Dec) drives {q4_pct:.1f}% of annual revenue. November and
     December consistently outperform all other months across all 4 years.

  4. DISCOUNT DAMAGE — Orders with discounts >=30% result in losses {disc_loss_pct:.1f}%
     of the time. The correlation between discount rate and profit is {corr:.2f},
     indicating heavy discounting actively destroys margin.

  5. BEST SEGMENT — {best_segment['Segment']} delivers the highest profit margin at
     {best_segment['Margin']:.1f}%, making it the most valuable customer group by profitability.

  6. REGIONAL LEADER — {top_region['Region']} leads in total revenue (${top_region['Sales']/1000:.0f}K)
     with a {top_region['Margin']:.1f}% margin, making it both the largest and most
     efficient region.
""")

print("="*60)
print("  ALL CHARTS SAVED TO: ./charts/")
print("  Run complete. Ready for GitHub upload.")
print("="*60)
