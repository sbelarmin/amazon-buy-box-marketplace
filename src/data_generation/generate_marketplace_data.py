"""
Synthetic data generator for Project 3:
Amazon Buy Box Marketplace Analysis

This script creates a compact, reproducible marketplace panel at the
seller x ASIN x day level. It is intentionally simple so the project
can focus on decision science, causal thinking, and pricing strategy.

Output:
    data/synthetic/marketplace_panel.csv
"""

from __future__ import annotations

from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------
SEED = 42
N_ASINS = 150
N_SELLERS = 40
N_DAYS = 90
MIN_SELLERS_PER_ASIN = 3
MAX_SELLERS_PER_ASIN = 8
REFERRAL_FEE_RATE = 0.15


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def softmax(x: np.ndarray) -> np.ndarray:
    """Numerically stable softmax."""
    shifted = x - np.max(x)
    exp_x = np.exp(shifted)
    return exp_x / exp_x.sum()


def ensure_output_dir() -> Path:
    """Create output directory if it does not exist."""
    output_dir = Path("data/synthetic")
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


# ---------------------------------------------------------------------
# Dimension generators
# ---------------------------------------------------------------------
def generate_products(
    n_asins: int,
    rng: np.random.Generator,
) -> pd.DataFrame:
    """Generate product-level attributes."""
    categories = ["Tools", "Home", "Kitchen", "Electronics", "Pet", "Outdoors"]

    df = pd.DataFrame({
        "asin": [f"A{i:04d}" for i in range(1, n_asins + 1)],
        "category": rng.choice(categories, size=n_asins, replace=True),
        "base_demand": rng.integers(12, 45, size=n_asins),
        "target_price": rng.uniform(25, 140, size=n_asins).round(2),
    })

    # Cost of goods sold: roughly 45% to 75% of target price
    cost_pct = rng.uniform(0.45, 0.75, size=n_asins)
    df["product_cost"] = (df["target_price"] * cost_pct).round(2)

    return df


def generate_sellers(
    n_sellers: int,
    rng: np.random.Generator,
) -> pd.DataFrame:
    """Generate seller-level attributes."""
    fulfillment = rng.choice(["FBA", "FBM"], size=n_sellers, p=[0.60, 0.40])

    shipping_days = np.where(
        fulfillment == "FBA",
        rng.integers(1, 3, size=n_sellers),   # 1-2 days
        rng.integers(3, 7, size=n_sellers),   # 3-6 days
    )

    df = pd.DataFrame({
        "seller_id": [f"S{i:03d}" for i in range(1, n_sellers + 1)],
        "seller_rating": rng.uniform(85.0, 99.5, size=n_sellers).round(1),
        "fulfillment_type": fulfillment,
        "shipping_days": shipping_days,
    })

    # Composite quality score used only as a stable latent seller trait
    df["seller_quality_score"] = (
        (df["seller_rating"] - 85.0) / (99.5 - 85.0)
        + np.where(df["fulfillment_type"] == "FBA", 0.15, 0.0)
        - 0.03 * (df["shipping_days"] - 1)
    ).round(3)

    return df


def generate_seller_asin_links(
    products: pd.DataFrame,
    sellers: pd.DataFrame,
    rng: np.random.Generator,
    min_sellers: int = MIN_SELLERS_PER_ASIN,
    max_sellers: int = MAX_SELLERS_PER_ASIN,
) -> pd.DataFrame:
    """Assign a subset of sellers to each ASIN."""
    rows = []

    seller_ids = sellers["seller_id"].to_numpy()

    for asin in products["asin"]:
        n_comp = int(rng.integers(min_sellers, max_sellers + 1))
        selected = rng.choice(seller_ids, size=n_comp, replace=False)

        for seller_id in selected:
            rows.append({
                "asin": asin,
                "seller_id": seller_id,
                # Stable seller-specific pricing tendency
                "base_markup_pct": rng.normal(0.00, 0.05),
                # Not used heavily yet, but useful for future extension
                "inventory_capacity": int(rng.integers(20, 120)),
            })

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------
# Simulation core
# ---------------------------------------------------------------------
def simulate_daily_marketplace(
    products: pd.DataFrame,
    sellers: pd.DataFrame,
    seller_asin: pd.DataFrame,
    n_days: int,
    rng: np.random.Generator,
) -> pd.DataFrame:
    """Create seller x ASIN x day records with daily prices and outcomes."""
    base = (
        seller_asin
        .merge(products, on="asin", how="left")
        .merge(sellers, on="seller_id", how="left")
        .copy()
    )

    # Expand across days
    day_frames = []
    for day in range(1, n_days + 1):
        day_df = base.copy()
        day_df["day"] = day

        # Daily price variation around product target price
        daily_noise = rng.normal(0.0, 0.02, size=len(day_df))
        raw_price = day_df["target_price"] * (1 + day_df["base_markup_pct"] + daily_noise)

        # Make sure prices stay economically plausible
        min_price = day_df["product_cost"] * 1.08
        day_df["price"] = np.maximum(raw_price, min_price).round(2)

        # Competitor-relative features
        day_df["num_competitors"] = day_df.groupby(["day", "asin"])["seller_id"].transform("count")
        day_df["lowest_price"] = day_df.groupby(["day", "asin"])["price"].transform("min")
        day_df["price_gap_to_lowest"] = (day_df["price"] - day_df["lowest_price"]).round(2)
        day_df["price_rank"] = (
            day_df.groupby(["day", "asin"])["price"]
            .rank(method="dense", ascending=True)
            .astype(int)
        )

        # Daily total demand shock at ASIN-day level
        asin_day = day_df[["day", "asin", "base_demand"]].drop_duplicates().copy()
        demand_noise = rng.normal(0.0, asin_day["base_demand"] * 0.20)
        asin_day["market_demand_units"] = np.maximum(
            1,
            np.round(asin_day["base_demand"] + demand_noise)
        ).astype(int)

        day_df = day_df.merge(
            asin_day[["day", "asin", "market_demand_units"]],
            on=["day", "asin"],
            how="left",
        )

        day_frames.append(day_df)

    panel = pd.concat(day_frames, ignore_index=True)

    # Assign Buy Box probabilities and winner
    panel = assign_buy_box(panel, rng)

    # Allocate units sold
    panel = allocate_demand(panel, rng)

    # Profit metrics
    panel = compute_profit_metrics(panel)

    # Keep a compact final schema
    final_cols = [
        "day",
        "asin",
        "seller_id",
        "seller_rating",
        "fulfillment_type",
        "shipping_days",
        "product_cost",
        "target_price",
        "base_demand",
        "price",
        "num_competitors",
        "lowest_price",
        "price_rank",
        "price_gap_to_lowest",
        "buy_box_probability",
        "buy_box_winner",
        "market_demand_units",
        "units_sold",
        "revenue",
        "amazon_referral_fee",
        "fulfillment_cost",
        "contribution_profit_per_unit",
        "contribution_profit",
    ]
    return panel[final_cols].sort_values(["day", "asin", "price_rank", "seller_id"]).reset_index(drop=True)


def assign_buy_box(
    panel: pd.DataFrame,
    rng: np.random.Generator,
) -> pd.DataFrame:
    """Assign Buy Box probabilities and a single winner per ASIN-day."""
    df = panel.copy()

    # Standardized rating roughly on 0-1 scale
    rating_scaled = (df["seller_rating"] - 85.0) / (99.5 - 85.0)
    fba_flag = (df["fulfillment_type"] == "FBA").astype(int)

    # Simple latent score:
    # - lower price gap is better
    # - faster shipping is better
    # - FBA helps
    # - better rating helps
    noise = rng.normal(0.0, 0.15, size=len(df))
    df["buy_box_score"] = (
        -0.60 * df["price_gap_to_lowest"]
        -0.35 * df["shipping_days"]
        +0.90 * fba_flag
        +0.80 * rating_scaled
        +noise
    )

    probs = np.zeros(len(df), dtype=float)
    winners = np.zeros(len(df), dtype=int)

    for _, idx in df.groupby(["day", "asin"]).groups.items():
        idx = np.asarray(list(idx))
        p = softmax(df.loc[idx, "buy_box_score"].to_numpy())
        probs[idx] = p
        winner_local = rng.choice(len(idx), p=p)
        winners[idx[winner_local]] = 1

    df["buy_box_probability"] = probs.round(4)
    df["buy_box_winner"] = winners
    return df.drop(columns=["buy_box_score"])


def allocate_demand(
    panel: pd.DataFrame,
    rng: np.random.Generator,
) -> pd.DataFrame:
    """Allocate most demand to the Buy Box winner and residual demand to others."""
    df = panel.copy()
    units = np.zeros(len(df), dtype=int)

    for _, idx in df.groupby(["day", "asin"]).groups.items():
        idx = np.asarray(list(idx))
        group = df.loc[idx]

        total_demand = int(group["market_demand_units"].iloc[0])

        winner_mask = group["buy_box_winner"].to_numpy() == 1
        winner_idx = idx[winner_mask][0]

        # Winner gets 75-90% of demand
        winner_share = float(rng.uniform(0.75, 0.90))
        winner_units = int(round(total_demand * winner_share))
        residual_units = max(0, total_demand - winner_units)

        units[np.where(idx == winner_idx)[0][0] + 0]  # no-op; keep shape logic explicit
        units[winner_idx] = winner_units

        other_idx = idx[idx != winner_idx]
        if len(other_idx) > 0 and residual_units > 0:
            # Split residual demand using inverse-price weighting
            price_gaps = df.loc[other_idx, "price_gap_to_lowest"].to_numpy()
            attractiveness = 1.0 / (1.0 + price_gaps)
            attractiveness = attractiveness / attractiveness.sum()

            split = rng.multinomial(residual_units, attractiveness)
            for pos, seller_row_idx in enumerate(other_idx):
                units[seller_row_idx] = split[pos]

    df["units_sold"] = units
    return df


def compute_profit_metrics(panel: pd.DataFrame) -> pd.DataFrame:
    """Compute revenue and contribution profit metrics."""
    df = panel.copy()

    # Simple fulfillment cost structure
    df["fulfillment_cost"] = np.where(
        df["fulfillment_type"] == "FBA",
        5.50 + 0.20 * df["shipping_days"],
        4.50 + 0.35 * df["shipping_days"],
    ).round(2)

    df["amazon_referral_fee"] = (REFERRAL_FEE_RATE * df["price"]).round(2)
    df["contribution_profit_per_unit"] = (
        df["price"]
        - df["product_cost"]
        - df["amazon_referral_fee"]
        - df["fulfillment_cost"]
    ).round(2)

    df["revenue"] = (df["price"] * df["units_sold"]).round(2)
    df["contribution_profit"] = (
        df["contribution_profit_per_unit"] * df["units_sold"]
    ).round(2)

    return df


# ---------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------
def generate_marketplace_data(
    n_asins: int = N_ASINS,
    n_sellers: int = N_SELLERS,
    n_days: int = N_DAYS,
    seed: int = SEED,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Generate all tables and the final marketplace panel."""
    rng = np.random.default_rng(seed)

    products = generate_products(n_asins=n_asins, rng=rng)
    sellers = generate_sellers(n_sellers=n_sellers, rng=rng)
    seller_asin = generate_seller_asin_links(
        products=products,
        sellers=sellers,
        rng=rng,
    )
    panel = simulate_daily_marketplace(
        products=products,
        sellers=sellers,
        seller_asin=seller_asin,
        n_days=n_days,
        rng=rng,
    )
    return products, sellers, seller_asin, panel


def main() -> None:
    """Generate marketplace data and save the final modeling table."""
    output_dir = ensure_output_dir()
    products, sellers, seller_asin, panel = generate_marketplace_data()

    panel_path = output_dir / "marketplace_panel.csv"
    products_path = output_dir / "dim_products.csv"
    sellers_path = output_dir / "dim_sellers.csv"
    links_path = output_dir / "bridge_seller_asin.csv"

    panel.to_csv(panel_path, index=False)
    products.to_csv(products_path, index=False)
    sellers.to_csv(sellers_path, index=False)
    seller_asin.to_csv(links_path, index=False)

    print(f"Saved main panel to: {panel_path}")
    print(f"Rows: {len(panel):,}")
    print(f"ASINs: {panel['asin'].nunique():,}")
    print(f"Sellers: {panel['seller_id'].nunique():,}")
    print(f"Days: {panel['day'].nunique():,}")

    # Quick validation checks
    buy_box_per_group = panel.groupby(["day", "asin"])["buy_box_winner"].sum()
    print(f"One Buy Box winner per ASIN-day: {(buy_box_per_group == 1).all()}")

    summary = (
        panel.groupby("price_rank")["buy_box_winner"]
        .mean()
        .reset_index(name="buy_box_win_rate")
        .head(5)
    )
    print("\nBuy Box win rate by price rank (first 5 ranks):")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
