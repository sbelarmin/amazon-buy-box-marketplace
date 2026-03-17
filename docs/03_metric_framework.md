# Amazon Buy Box Marketplace Analysis  
## Metric Framework

---

# 1. Purpose of the Metric Framework

The purpose of this metric framework is to define how marketplace performance and pricing strategies will be evaluated in this project.

Clear metric definitions are necessary to ensure that the analysis focuses on **economically meaningful outcomes** rather than intermediate marketplace signals alone.

In particular, winning the Buy Box is not the final business objective. Instead, Buy Box ownership is one of several factors that influence **profitability**.

The metric framework therefore separates:

- **primary decision metrics**
- **supporting marketplace metrics**
- **demand and revenue metrics**
- **guardrail metrics**

---

# 2. Unit of Analysis

The primary unit of analysis in this project is:

**Seller–ASIN–Day**

Each observation represents a specific seller offering a specific product on a given day.

This unit captures:

- marketplace competition among sellers
- daily pricing adjustments
- Buy Box outcomes
- sales performance

Using a daily unit of analysis allows the model to capture **dynamic marketplace competition**.

---

# 3. Primary Decision Metric

The primary objective of the seller is to **maximize expected contribution profit**.

Contribution profit represents the profit remaining after accounting for the major variable costs associated with marketplace sales.

### Contribution Profit Formula

Contribution Profit per Unit is defined as:

Contribution Profit =  
Price  
− Product Cost  
− Amazon Referral Fee  
− Fulfillment Cost

Where:

**Amazon Referral Fee**

Amazon Referral Fee = Commission Rate × Price

For simplicity, this project assumes a constant commission rate:

Commission Rate = 15%

### Expected Profit

Total expected profit for a listing-period is therefore:

Expected Profit =  
Expected Units Sold × Contribution Profit per Unit

This metric captures the core tradeoff between:

- higher margin per unit (higher price)
- higher expected demand (lower price and higher Buy Box probability)

The pricing strategy that maximizes **expected profit** is considered optimal.

---

# 4. Supporting Marketplace Metrics

While profit is the ultimate objective, several intermediate marketplace metrics help explain marketplace dynamics.

### Buy Box Win Indicator

Binary indicator:

BuyBox = 1 if seller wins Buy Box  
BuyBox = 0 otherwise

### Buy Box Win Probability

Estimated probability that a seller wins the Buy Box based on:

- price competitiveness
- shipping speed
- fulfillment method
- seller rating
- marketplace competition

This metric connects seller attributes to marketplace visibility.

---

# 5. Demand Metrics

Demand metrics capture the downstream impact of Buy Box ownership and price competitiveness.

### Units Sold

Number of units sold by a seller for a given ASIN and day.

Units sold are influenced by:

- Buy Box ownership
- price competitiveness
- marketplace demand

### Revenue

Revenue = Price × Units Sold

Revenue reflects gross sales but does not account for costs.

---

# 6. Guardrail Metrics

Guardrail metrics ensure that pricing strategies remain operationally viable.

### Minimum Margin Rate

A minimum acceptable margin rate may be required to maintain profitability.

Margin Rate = Contribution Profit / Price

Pricing strategies that fall below a defined margin threshold may be considered infeasible.

### Buy Box Competitiveness

Pricing strategies that effectively eliminate Buy Box eligibility may be undesirable even if margins are high.

Maintaining a reasonable probability of Buy Box ownership ensures the seller remains competitive in the marketplace.

---

# 7. Diagnostic Marketplace Metrics

Several diagnostic metrics will be used to better understand marketplace competition.

### Price Rank

The seller's price rank relative to competing sellers for the same ASIN.

Example:

- Rank 1 = lowest price
- Rank 2 = second lowest price

### Price Gap to Lowest Competitor

Difference between the seller’s price and the lowest competitor price.

This metric captures price competitiveness more precisely than price rank alone.

### Number of Competitors

Total number of sellers competing for the same ASIN on a given day.

Competition intensity can influence Buy Box dynamics.

---

# 8. Measurement Window

The project models marketplace behavior across multiple simulated days.

This allows the analysis to capture:

- variation in competitor pricing
- changes in Buy Box ownership
- variation in demand

Using multiple days improves the stability of estimated relationships between price, Buy Box outcomes, and demand.

---

# 9. Role of Metrics in the Project

These metrics support different stages of the analysis:

| Metric Type             | Role                             |
| ----------------------- | -------------------------------- |
| Primary Decision Metric | Evaluate pricing strategies      |
| Marketplace Metrics     | Model Buy Box outcomes           |
| Demand Metrics          | Estimate sales impact            |
| Guardrail Metrics       | Ensure viable pricing strategies |
| Diagnostic Metrics      | Understand competition dynamics  |

Together, these metrics allow the project to move from **marketplace observation** to **pricing optimization**.

---