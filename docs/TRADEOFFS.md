# Tradeoffs: What We Deliberately Did Not Build

Three significant features deliberately excluded from MVP, and the reasoning.

---

## 1. Supplier/Scope 3 Supply Chain Module

**What It Would Do**:
- Ingest emissions from suppliers' own reports (Tier 1, Tier 2 suppliers)
- Match purchases (from SAP procurement data) to supplier emissions factors
- Calculate indirect Scope 3: "we bought $1M of widgets from Widget Corp, who emits X kg CO2 per $ revenue"
- Enable product-level carbon footprinting

**Example Workflow**:
```
SAP: Bought 100 units of Component XYZ from Vendor ABC ($50,000)
  ↓
Scope 3 Module: Widget Corp reports 0.5 kg CO2 per $1 of revenue
  ↓
Result: Component XYZ contributes $50k × 0.5 = 25,000 kg CO2 to our Scope 3
```

**Why Not Built**:
1. **Data Availability**: Suppliers rarely report emissions data. Most small/medium vendors don't have sustainability teams.
2. **Verification Complexity**: How do we verify Vendor ABC's emissions claim? Different emission factors from different sources?
3. **Scope Creep**: SAP procurement → vendor lookup → emissions calculation → product costing. This is a supply chain accounting system, not a data ingestion dashboard.
4. **Materiality**: Scope 1 + 2 are usually <50% of total emissions for most companies; it's a feature, not a blocker.

**When to Build**:
- Client has existing supplier sustainability program (e.g., Dow Jones Sustainability Index requirement)
- Majority of Scope 3 is supply chain (e.g., manufacturing company, not service company)
- Supplier data sources exist (e.g., CDP responses, industry databases like Trucost)

---

## 2. Reconciliation & Variance Analysis

**What It Would Do**:
- Compare this month's electricity to last month. Highlight if >10% variance.
- Cross-check: SAP fuel quantity vs. Fleet Management System (FMS) odometer readings
- Identify missing data: "we always get utility bills for 5 facilities; we're missing Denver this month"
- Trend analysis: flag if emissions spiking or dipping unexpectedly

**Example**:
```
Facility A Electricity:
  Jan 2024: 50,000 kWh
  Feb 2024: 47,000 kWh (–6%, OK)
  Mar 2024: 200,000 kWh (+326%, FLAG)
  ↓
Trigger: "Unusual consumption detected. Is there new equipment? Billing error?"
```

**Why Not Built**:
1. **Domain-Specific Thresholds**: What's "unusual" varies by industry and season. A cold winter justifies higher heating; we can't set one rule for all.
2. **Requires Historical Baseline**: Can't compare to "last year" if this is the first year of data collection.
3. **Can Introduce False Positives**: Flagging 326% variance that turns out to be a billing correction is noise.
4. **Analyst Can Do This**: Loading last month's report in Excel and checking is fast. Automating it doesn't save much for MVP.

**When to Build**:
- 3+ years of historical data (enough to establish patterns)
- Industry-specific baselines (calibrate thresholds per sector)
- Integration with FMS, SAP reporting (cross-validate data)
- Real-time ingestion (daily meter reads, not monthly reports)

---

## 3. Role-Based Access Control (RBAC) & Approval Workflows

**What It Would Do**:
- Roles: Viewer, Analyst, Manager, Admin
- Approval workflow: Analyst flags records, Manager approves, Admin locks for audit
- Delegated authority: "only Manager A can approve > 1M kg CO2 records"
- Audit trail includes user roles at time of action

**Example Workflow**:
```
Analyst reviews 50 Scope 1 records
  → Analyst flags 3 as "suspicious"
  → Manager gets notification: "3 records flagged, please review"
  → Manager approves flagged records
  → Records locked, sent to auditors
```

**Why Not Built**:
1. **Unknown Team Structure**: Does the client have 2 people or 20? Are there manager gatekeepers or is everyone an analyst?
2. **Overkill for MVP**: Most companies doing ESG for the first time have a tiny team (1-3 people). RBAC is bureaucracy they don't need.
3. **Adds Complexity**: Every endpoint needs permission checks. Harder to debug. More test cases.
4. **Django Admin Sufficient**: Admin interface already supports user/group permissions if needed.

**When to Build**:
- Client is large (>1000 employees) with formal governance
- Multiple departments submit data independently
- Audit requirement mandates "segregation of duties" (submitter ≠ approver)
- Multi-geography (different managers per region)

---

## Why These Three?

**Pattern**: Each is a "next level up" in sophistication:
1. **Supply Chain**: Extends beyond company boundary (supplier data)
2. **Reconciliation**: Requires historical analytics and domain rules
3. **RBAC**: Requires org structure knowledge and permission matrix

All three are common in mature ESG systems. But for a PM saying "build a prototype in 4 days," they add complexity without addressing the core problem: *get data in, get it reviewed, get it locked for audit*.

---

## What We Kept Instead

- **Simplicity**: Analyst uploads file, sees records, approves/rejects. Done.
- **Transparency**: Source data visible. Calculations transparent. Audit trail complete.
- **Defensibility**: Can explain every design choice to skeptical auditors.

**Trade-off Philosophy**: 

> "A PM asked for a prototype. Shipping a tightly-scoped app with confident design decisions is better than shipping a sprawling app where 60% of the code handles edge cases that haven't been specified."

If the client loves the core platform, these three features are natural extensions. If the client says "actually we don't need Scope 3 supply chain," we didn't waste effort on it.
