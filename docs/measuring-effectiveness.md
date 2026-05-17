# Measuring Phishing Simulation Program Effectiveness

A phishing simulation program is only as useful as the data it generates. Running campaigns without tracking the right metrics is like doing fire drills without checking whether employees made it out. This guide covers the four metrics that matter most, how to calculate them, and what good looks like.

---

## The Four Metrics That Matter

### 1. Click Rate

**What it measures:** The percentage of recipients who clicked the phishing link in a given campaign.

**How to calculate:**
```
Click Rate = (Number of clicks ÷ Number of emails delivered) × 100
```

**What good looks like:**
- Baseline (first campaign): 20–35% is typical for organizations with no prior training
- After 6 months of regular simulations: target below 10%
- Mature program (18+ months): target below 5%

**Why it matters:** Click rate is your headline susceptibility number. Track it per department and per campaign difficulty level so you can identify high-risk teams and measure training impact accurately.

**Watch out for:** A single aggregate click rate hides the distribution. A 10% average with one department at 40% is a crisis hiding behind a decent number.

---

### 2. Report Rate

**What it measures:** The percentage of recipients who reported the simulated phishing email to IT/Security rather than clicking it or ignoring it.

**How to calculate:**
```
Report Rate = (Number of reports ÷ Number of emails delivered) × 100
```

**What good looks like:**
- Year 1 target: >25% of non-clickers reporting
- Mature program: >80% of recipients reporting suspicious emails

**Why it matters:** Click rate tells you how many people failed. Report rate tells you how many people actively helped defend the organization. High report rates compress the time your security team has to respond to real attacks.

**Watch out for:** Make it easy to report. If your reporting mechanism is buried in a menu or requires a help desk ticket, report rates will be suppressed regardless of employee awareness.

---

### 3. Time-to-Report

**What it measures:** The average elapsed time between when a phishing email lands and when a user reports it.

**How to calculate:**
Track the timestamp of delivery and the timestamp of each report submission. Average the delta across all reports in the campaign.

**What good looks like:**
- Year 1 target: median report within 4 hours
- Mature program: median report within 30 minutes

**Why it matters:** In real attacks, every minute the phishing email is live in inboxes is a minute another employee might click it. Fast reporting triggers quarantine workflows that protect the rest of the organization. Time-to-report is the most direct measure of your human detection layer's speed.

**Watch out for:** Outliers from people who report on Monday morning what arrived Friday afternoon will skew this metric. Segment by day of week for honest analysis.

---

### 4. Repeat Offender Tracking

**What it measures:** The number and identity of employees who click on phishing simulations across multiple campaigns despite prior training.

**How to calculate:**
Track click events at the individual level across campaigns. Flag anyone who clicks in two or more campaigns within a rolling 6-month window.

**What good looks like:**
- Repeat offenders should represent less than 3% of your total workforce in a mature program
- No individual should click in three or more consecutive campaigns without a targeted intervention

**Why it matters:** Repeat offenders are high-risk individuals who have not responded to standard training. They need a different intervention — one-on-one coaching, role-specific training, or privileged access review — not just another simulation.

**Watch out for:** Avoid public shaming or punitive action. Research consistently shows that punitive approaches reduce reporting rates as employees become afraid to be caught. Focus on coaching, not consequences.

---

## Building a Reporting Dashboard

At minimum, track these metrics per campaign and aggregate them over time:

| Metric | Per Campaign | Trend (6-month rolling) |
|--------|-------------|------------------------|
| Click rate | ✅ | ✅ |
| Report rate | ✅ | ✅ |
| Median time-to-report | ✅ | ✅ |
| Repeat offender count | ✅ | ✅ |
| Department breakdown | ✅ | Optional |
| Template difficulty vs. click rate | ✅ | Optional |

Present trends to leadership quarterly. Month-over-month noise is high; quarterly trends show real program impact.

---

## From Metrics to Action

| Metric Signal | Action |
|---|---|
| Click rate plateau after 3+ campaigns | Increase template difficulty; vary delivery timing |
| Low report rate despite low click rate | Improve reporting UX; run internal awareness campaign about the report button |
| High time-to-report | Send simulations on varied days/times; run a "fastest reporter" recognition program |
| Specific department persistently high click rate | Schedule targeted, role-specific campaign + live training session |
| Individual repeat offender (3+ campaigns) | One-on-one coaching; consider privileged access review if in a high-risk role |

---

## Industry Benchmarks

Based on aggregated data from enterprise security awareness programs:

| Maturity Level | Click Rate | Report Rate | Time-to-Report |
|---|---|---|---|
| Baseline (no prior training) | 25–35% | <5% | N/A |
| Year 1 | 10–20% | 15–30% | 2–6 hours |
| Year 2 | 5–10% | 30–60% | 30–120 min |
| Mature (3+ years) | <5% | >70% | <30 min |

---

## HailBytes SAT tracks all of these automatically

Manually pulling click data from GoPhish exports, cross-referencing report emails, and building trend charts in spreadsheets is time-consuming and error-prone. HailBytes SAT captures every metric above in real time — click events, report button submissions, time deltas, and repeat offender flags — and surfaces them in a live dashboard your security team and leadership can access without any data wrangling.

**[See it live — HailBytes SAT demo →](https://hailbytes.com/sat-demo?utm_source=github&utm_medium=repo_readme&utm_campaign=gophish-training-templates&utm_content=measuring_effectiveness_doc)**
