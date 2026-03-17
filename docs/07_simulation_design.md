
# Amazon Buy Box Marketplace Analysis
## Simulation Design

---

# 1. Purpose of the Simulation

This project uses a synthetic dataset to simulate competition among sellers in an Amazon-style marketplace.

The simulation must generate realistic relationships between:

- seller pricing
- fulfillment characteristics
- Buy Box ownership
- demand allocation
- seller profitability

The dataset will allow the project to estimate how marketplace factors influence Buy Box outcomes and evaluate pricing strategies that maximize expected profit.

---

# 2. Simulation Dimensions

The simulation operates across three dimensions:

| Dimension | Description |
|---|---|
| Products (ASINs) | Individual product listings |
| Sellers | Marketplace participants selling products |
| Time | Daily marketplace competition |

---

# 3. Simulation Size

The synthetic dataset will include approximately:

| Component | Value |
|---|---|
| Number of ASINs | 150 |
| Number of Sellers | 40 |
| Simulation Days | 90 |
| Sellers per ASIN | 3–8 |

Expected final dataset size:

**~40,000–60,000 rows**

Each row represents:

**Seller × ASIN × Day**

---

# 4. Core Tables

The simulation will generate several intermediate tables.

## Product Table (`dim_products`)

Product-level attributes.

| Column | Description |
|---|---|
| asin | Product identifier |
| category | Product category |
| base_demand | Average daily demand |
| product_cost | Cost of goods sold |
| target_price | Typical market price |
| competition_tier | Low / Medium / High competition |

Example:

| asin | base_demand | product_cost | target_price |
|---|---|---|---|
| A1 | 20 | 35 | 75 |

---

## Seller Table (`dim_sellers`)

Seller-level attributes.

| Column | Description |
|---|---|
| seller_id | Seller identifier |
| seller_rating | % positive reviews |
| fulfillment_type | FBA or FBM |
| shipping_days | Delivery time |
| seller_quality_score | composite seller quality |

Example:

| seller_id | rating | fulfillment | shipping_days |
|---|---|---|---|
| S1 | 98.7 | FBA | 2 |

---

## Seller-ASIN Table (`bridge_seller_asin`)

Defines which sellers sell which products.

| Column | Description |
|---|---|
| seller_id | Seller |
| asin | Product |
| base_markup_pct | Typical markup |
| inventory_capacity | Maximum daily inventory |

Each ASIN will randomly select **3–8 sellers** from the seller pool.

---

# 5. Daily Marketplace Panel

The final analytical dataset will contain:

| Column | Description |
|---|---|
| day | Simulation day |
| asin | Product |
| seller_id | Seller |
| price | Listing price |
| shipping_days | Delivery time |
| fulfillment_type | FBA/FBM |
| seller_rating | Seller reputation |
| num_competitors | Sellers for that ASIN |
| price_rank | Rank among sellers |
| lowest_price | Lowest price that day |
| price_gap_to_lowest | Price difference |
| buy_box_probability | Modeled probability |
| buy_box_winner | Indicator |
| market_demand_units | Total product demand |
| units_sold | Units allocated to seller |
| revenue | Price × Units |
| amazon_referral_fee | 15% × price |
| fulfillment_cost | Shipping/handling cost |
| contribution_profit_per_unit | Unit profit |
| contribution_profit | Total profit |

---

# 6. Price Generation Logic

Prices will be generated around the product’s **target price**.

Each seller has a markup tendency.

Example:

```
price = target_price × (1 + seller_markup + daily_noise)
```

Where:

```
seller_markup ~ Normal(0, 0.05)
daily_noise ~ Normal(0, 0.02)
```

This produces:

- persistent seller pricing differences
- daily price variation
- realistic price dispersion

---

# 7. Buy Box Probability Model

Buy Box probability is determined by a latent score.

Each seller receives a **Buy Box score**:

```
score =
    β0
  + β1 * (-price_gap_to_lowest)
  + β2 * (-shipping_days)
  + β3 * FBA_indicator
  + β4 * seller_rating_scaled
  + ε
```

Where:

- lower price improves score
- faster shipping improves score
- FBA receives a boost
- higher ratings improve score

The scores are converted to probabilities using a **softmax function** within each ASIN-day group.

One seller is then sampled as the Buy Box winner.

---

# 8. Demand Generation

Daily demand for each ASIN is simulated as:

```
market_demand =
    base_demand
  + daily_demand_noise
```

Where:

```
daily_demand_noise ~ Normal(0, base_demand × 0.2)
```

---

# 9. Demand Allocation

Demand is allocated based on Buy Box ownership.

Example rule:

| Seller Type | Demand Share |
|---|---|
| Buy Box Winner | 75–90% |
| Other Sellers | Remaining share |

Non-winning sellers receive small residual demand.

---

# 10. Profit Model

Revenue:

```
revenue = price × units_sold
```

Amazon referral fee:

```
amazon_referral_fee = 0.15 × price
```

Contribution profit per unit:

```
contribution_profit_per_unit =
    price
  − product_cost
  − amazon_referral_fee
  − fulfillment_cost
```

Total contribution profit:

```
contribution_profit =
    units_sold × contribution_profit_per_unit
```

---

# 11. Key Behavioral Patterns

The simulation is designed to reproduce realistic marketplace dynamics:

- lowest price wins the Buy Box often but not always
- faster shipping improves Buy Box probability
- FBA sellers have an advantage
- higher seller ratings increase competitiveness
- Buy Box winners capture most demand
- lowest price is not always profit-optimal

These dynamics enable the project to analyze pricing strategies under competitive conditions.
