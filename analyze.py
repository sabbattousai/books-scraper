"""Clean kitaplar.csv, answer the 3 questions, save minimalist charts to charts/."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ---- one quiet visual language: single blue hue, warm-grey ink, no frames ----
SURFACE, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#898781"
GRID, BASE = "#e1e0d9", "#c3c2b7"
BLUE, BLUE_DARK, BLUE_LIGHT = "#2a78d6", "#184f95", "#b7d3f6"
plt.rcParams.update({
    "font.family": ["Segoe UI", "DejaVu Sans"], "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "axes.edgecolor": BASE, "text.color": INK, "axes.labelcolor": INK2, "xtick.color": MUTED,
    "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
    "axes.spines.left": False, "savefig.facecolor": SURFACE,
})


def frame(fig, title, subtitle):
    """Left-aligned headline + muted subtitle, the same on every chart."""
    fig.text(0.04, 0.95, title, fontsize=16, fontweight="semibold", ha="left", va="top")
    fig.text(0.04, 0.885, subtitle, fontsize=10.5, color=INK2, ha="left", va="top")


def source(fig):
    fig.text(0.04, 0.02, "Source: books.toscrape.com, 1000 books", fontsize=8, color=MUTED, ha="left")


def save(fig, name):
    fig.savefig(f"charts/{name}", dpi=200)
    plt.close(fig)


df = pd.read_csv("kitaplar.csv")

# ---- cleaning -------------------------------------------------------------
print("rows:", len(df))
print("missing values:\n", df.isna().sum().to_string(), "\n")
before = len(df)
df = df.drop_duplicates(subset="url")
df = df.dropna(subset=["fiyat", "puan", "kategori"]).copy()
df["puan"] = df["puan"].astype(int)
print(f"dropped {before - len(df)} duplicate/incomplete rows -> {len(df)} left")
assert df["fiyat"].between(0, 1000).all() and df["puan"].between(1, 5).all()

# ---- Q1: average price per category, 10 most expensive --------------------
cat = (df.groupby("kategori")["fiyat"].agg(ortalama="mean", kitap_sayisi="count")
         .sort_values("ortalama", ascending=False))
top10 = cat.head(10)
print("Top 10 categories by average price:\n", top10.round(2).to_string(), "\n")
top10.round(2).to_csv("sonuc_kategori_ortalama_fiyat.csv")

fig, ax = plt.subplots(figsize=(9, 5.6))
fig.subplots_adjust(left=0.2, right=0.93, top=0.80, bottom=0.12)
rows = top10.iloc[::-1]
small = rows["kitap_sayisi"] < 5  # averages of 1-4 books are not reliable: draw them lighter
colors = [BLUE_LIGHT if s else BLUE for s in small]
bars = ax.barh(rows.index, rows["ortalama"], height=0.62, color=colors)
for y, (v, n) in enumerate(zip(rows["ortalama"], rows["kitap_sayisi"])):
    ax.text(v + 0.8, y, f"{v:.2f}", va="center", fontsize=10, fontweight="semibold", color=INK)
    ax.text(rows["ortalama"].max() * 1.27, y, f"{n} book{'s' if n > 1 else ''}", va="center",
            ha="right", fontsize=8.5, color=MUTED)
ax.set_xlim(0, rows["ortalama"].max() * 1.27)
ax.set_xticks(range(0, 70, 10))  # no gridline under the book-count column
ax.xaxis.grid(True, color=GRID, linewidth=0.8)
ax.set_axisbelow(True)
ax.tick_params(axis="both", length=0, labelsize=10)
ax.set_xlabel("Average price, GBP", fontsize=9, color=MUTED, loc="left")
frame(fig, "Top 10 categories by average price",
      "Light bars rest on fewer than 5 books, so treat them as indicative only")
source(fig)
save(fig, "1_kategori_ortalama_fiyat.png")

# ---- Q2: rating distribution ----------------------------------------------
dist = df["puan"].value_counts().reindex([1, 2, 3, 4, 5], fill_value=0)
print("Rating distribution:\n", dist.to_string(), "\n")
fig, ax = plt.subplots(figsize=(8, 5.4))
fig.subplots_adjust(left=0.08, right=0.95, top=0.80, bottom=0.14)
ax.bar(dist.index, dist.values, width=0.62, color=BLUE)
for x, v in zip(dist.index, dist.values):
    ax.text(x, v + 4, f"{v}", ha="center", fontsize=12, fontweight="semibold")
    ax.text(x, v - 14, f"{v / len(df):.1%}", ha="center", va="top", fontsize=9.5, color="#ffffff")
ax.set_xticks(range(1, 6), [f"{i} star" if i == 1 else f"{i} stars" for i in range(1, 6)])
ax.set_ylim(0, dist.max() * 1.18)
ax.set_yticks([])
ax.spines["bottom"].set_color(BASE)
ax.tick_params(axis="x", length=0, labelsize=10, colors=INK2)
frame(fig, "Ratings are spread almost evenly",
      "Number of books per star rating (an even split would be 200 each)")
source(fig)
save(fig, "2_puan_dagilimi.png")

# ---- Q3: do higher-rated books cost more? ---------------------------------
by_rating = df.groupby("puan")["fiyat"].agg(["mean", "median", "count"]).round(2)
pearson = df["puan"].corr(df["fiyat"])
spearman = df["puan"].rank().corr(df["fiyat"].rank())  # same as method="spearman", without scipy
print("Price by rating:\n", by_rating.to_string())
print(f"Pearson r = {pearson:.3f} | Spearman rho = {spearman:.3f}")
by_rating.to_csv("sonuc_puan_fiyat.csv")

rng = np.random.default_rng(7)
fig, ax = plt.subplots(figsize=(8, 5.4))
fig.subplots_adjust(left=0.09, right=0.95, top=0.80, bottom=0.14)
ax.scatter(df["puan"] + rng.uniform(-0.28, 0.28, len(df)), df["fiyat"],
           s=12, color=BLUE, alpha=0.22, linewidths=0)
ax.plot(by_rating.index, by_rating["median"], color=BLUE_DARK, linewidth=2, zorder=3)
ax.scatter(by_rating.index, by_rating["median"], s=70, color=BLUE_DARK, zorder=4,
           edgecolor=SURFACE, linewidth=2)
for x, v in zip(by_rating.index, by_rating["median"]):
    ax.text(x, v + 3.2, f"{v:.1f}", ha="center", fontsize=10, fontweight="semibold", color=BLUE_DARK, zorder=5)
ax.set_xticks(range(1, 6), [f"{i} star" if i == 1 else f"{i} stars" for i in range(1, 6)])
ax.set_xlim(0.5, 5.5)
ax.set_ylim(8, 64)
ax.yaxis.grid(True, color=GRID, linewidth=0.8)
ax.set_axisbelow(True)
ax.spines["bottom"].set_color(BASE)
ax.tick_params(axis="both", length=0, labelsize=10)
ax.set_ylabel("Price, GBP", fontsize=9, color=MUTED, loc="top")
frame(fig, "A higher rating does not mean a higher price",
      f"Each dot is a book; the line joins median prices. Correlation r = {pearson:.2f}, practically none")
source(fig)
save(fig, "3_puan_vs_fiyat.png")
