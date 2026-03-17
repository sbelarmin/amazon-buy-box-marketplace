# Amazon Buy Box Marketplace Analysis  
## Data Requirements

---

# 1. Purpose of the Data Design

This project uses a synthetic dataset designed to simulate realistic competition in an Amazon-style marketplace.

The dataset must support the analytical goals defined earlier in the project, including:

- analyzing marketplace competition
- estimating how seller attributes influence Buy Box outcomes
- modeling how Buy Box ownership affects demand
- simulating pricing strategies and computing expected profit

The synthetic data will therefore represent **multiple sellers competing to sell the same product over time**, with realistic variation in price, fulfillment characteristics, and marketplace competition.

---

# 2. Entities in the Dataset

The dataset will represent three primary entities.

### Products (ASINs)

Each product corresponds to a unique Amazon listing.

Product-level attributes may include:

- ASIN identifier
- product category
- baseline demand level
- product cost

Each product will be sold by multiple competing sellers.

---

### Sellers

Each seller represents a marketplace participant offering products for sale.

Seller-level attributes may include:

- seller_id
- seller rating
- fulfillment method (FBA or merchant fulfilled)
- shipping speed
- reliability score

These attributes influence Buy Box eligibility and competitiveness.

---

### Time

Marketplace competition evolves over time as sellers adjust prices and demand fluctuates.

Time will be represented as **daily observations**.

Each day captures:

- seller price adjustments
- Buy Box outcomes
- demand variation

---

# 3. Unit of Observation

The dataset will be structured at the level of:

**Seller–ASIN–Day**

Each row represents a seller offering a specific product on a given day.

Example observation:

| seller_id | asin | day | price | shipping_days | rating | buy_box | units_sold |
| --------- | ---- | --- | ----- | ------------- | ------ | ------- | ---------- |

This structure allows the dataset to capture:

- marketplace competition among sellers
- relative price positioning
- Buy Box outcomes
- resulting sales performance

---

# 4. Competition Structure

To simulate realistic marketplace conditions, each ASIN will have **multiple competing sellers**.

Competition characteristics may include:

- 3–10 sellers per product
- variation in price competitiveness
- variation in shipping speed
- variation in seller reputation

Competition intensity may differ across products to reflect different marketplace dynamics.

For example:

| ASIN | Number of Sellers |
| ---- | ----------------- |
| A    | 3                 |
| B    | 6                 |
| C    | 9                 |

---

# 5. Seller Attributes

Each seller will have attributes that influence Buy Box eligibility.

Key attributes include:

### Price

The seller’s listing price for the product.

Price competitiveness will be measured relative to the lowest competitor price.

### Shipping Speed

Estimated delivery time in days.

Faster shipping may improve Buy Box eligibility.

### Fulfillment Method

Binary indicator:

- Fulfilled by Amazon (FBA)
- Merchant Fulfilled (FBM)

FBA sellers often receive preferential Buy Box treatment due to faster and more reliable fulfillment.

### Seller Rating

Percentage of positive customer reviews.

Higher ratings signal stronger seller reliability and may influence Buy Box selection.

---

# 6. Derived Competition Features

Several features will be derived from the competitive marketplace environment.

### Price Rank

The seller’s price rank among competing sellers for a given ASIN.

Example:

- rank 1 = lowest price
- rank 2 = second lowest price

### Price Gap to Lowest Competitor

Difference between the seller’s price and the lowest price offered by any competitor.

This metric captures the degree of price competitiveness.

### Number of Competitors

The number of sellers offering the same product on a given day.

Competition intensity may influence Buy Box outcomes.

---

# 7. Buy Box Assignment Logic

The dataset must include a mechanism that determines which seller wins the Buy Box.

The Buy Box winner will depend on a combination of factors including:

- price competitiveness
- shipping speed
- fulfillment method
- seller rating

While the exact Amazon algorithm is proprietary, the simulation will approximate its behavior by assigning higher Buy Box probability to sellers that are:

- price competitive
- fast shipping
- highly rated
- using FBA fulfillment

Only one seller can win the Buy Box for each ASIN on a given day.

---

# 8. Demand Generation

Demand will be modeled at the product level.

Key demand assumptions include:

- products have different baseline demand levels
- demand varies slightly across days
- Buy Box ownership strongly influences sales

The seller who wins the Buy Box will capture the majority of demand for that product on that day.

Other sellers may receive minimal sales.

---

# 9. Profit Mechanics

Each sale generates revenue and contribution profit for the seller.

Revenue:

Revenue = Price × Units Sold

Contribution profit per unit:

Contribution Profit =  
Price  
− Product Cost  
− Amazon Referral Fee  
− Fulfillment Cost

Where:

Amazon Referral Fee = Commission Rate × Price

The project assumes:

Commission Rate = 15%

These cost components allow the analysis to evaluate how pricing decisions influence profitability.

---

# 10. Dataset Size

The synthetic dataset should be large enough to capture meaningful variation in marketplace competition.

A reasonable scale for the dataset may include:

- 100–300 products
- 3–10 sellers per product
- 60–120 days of observations

This will produce a dataset with tens of thousands of rows, sufficient for modeling marketplace dynamics.

---

# 11. Role of the Dataset in the Project

This synthetic dataset will support all subsequent analytical steps in the project:

1. Exploring marketplace competition  
2. Modeling Buy Box outcomes  
3. Estimating demand effects  
4. Simulating pricing strategies  
5. Identifying profit-maximizing prices  

The dataset therefore serves as the foundation for the **decision science workflow of the project.**

---