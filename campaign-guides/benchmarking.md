# Community Benchmarking Guide

A reference for understanding and contextualizing your phishing simulation results. Use these benchmarks to evaluate your program's maturity, set realistic goals, and track improvement over time.

> **Privacy note:** All benchmarks below are derived from published industry research and aggregated community data. No individual organization data is collected or shared through this repository.

---

## Template Difficulty & Expected Click Rates

Each template in this repository is rated on a three-tier difficulty scale based on observed click rates in security awareness programs.

### Beginner (Expected click rate: 45–75%)

Beginner templates use broad, universal lures with little prior knowledge required. These are excellent for initial baseline assessments and work across nearly all employee populations.

| Template | Category | Avg Click Rate | Primary Tactic |
|----------|----------|---------------|----------------|
| DHL Package Delivery | Delivery/Shipping | 60–75% | Package anxiety |
| Package Pickup Notice | Delivery/Shipping | 55–70% | Delivery failure |
| USPS Smishing (SMS) | Smishing | 55–70% | Universal delivery |
| Email Server Migration | IT Security | 55–70% | IT authority + urgency |
| Webmail Upgrade | IT Security | 50–65% | Account access fear |
| Financial Aid Urgent | Education | 50–65% | Financial anxiety |
| Benefits Enrollment | HR/Payroll | 45–65% | Enrollment deadline |
| Loyalty Rewards Expiring | Retail | 45–65% | FOMO (points loss) |
| Insurance Verification | Healthcare | 45–60% | Health/coverage fear |
| Power Outage Credit | Utilities | 40–60% | Free money lure |
| New Office WiFi QR Code | Quishing | 40–60% | IT legitimacy |
| Student Portal Lockout | Education | 45–60% | Account access |
| Starbucks Gift Card | Entertainment | 45–60% | Reward scarcity |

### Intermediate (Expected click rate: 25–55%)

Intermediate templates require recipients to make a judgment call. They use more specific context, authority figures, or platform impersonation that requires some familiarity with the service being spoofed.

| Template | Category | Avg Click Rate | Primary Tactic |
|----------|----------|---------------|----------------|
| Zoom Recording Ready | Collaboration | 40–55% | Storage + expiry |
| Slack Account Audit | Collaboration | 35–55% | Admin authority |
| DocuSign NDA | E-Signature | 40–55% | Legal obligation |
| Adobe Sign Amendment | E-Signature | 35–50% | HR authority |
| Bank Alert Smishing | Smishing | 40–55% | Financial fear |
| Payroll Direct Deposit | HR/Payroll | 40–55% | Financial impact |
| Microsoft Account Alert | Microsoft | 35–50% | Security threat |
| Teams Guest Access | Collaboration | 30–50% | Auto-approve pressure |
| Hotel Reservation | Hospitality | 35–50% | Travel anxiety |
| Mailbox Compromised | IT Security | 40–55% | Security fear |
| Patient Portal Alert | Healthcare | 40–55% | Health privacy |
| HIPAA Compliance | Healthcare | 35–50% | Regulatory fear |
| MFA Re-enrollment QR | Quishing | 30–50% | IT authority |
| LinkedIn Alert | Social Media | 35–50% | Professional anxiety |
| Supplier Portal Update | Manufacturing | 35–50% | Access expiry |

### Advanced (Expected click rate: 15–40%)

Advanced templates require recipients to overcome one or more learned defenses. Lower click rates are expected — the goal is to catch the most security-conscious employees and test your most vigilant staff.

| Template | Category | Avg Click Rate | Primary Tactic |
|----------|----------|---------------|----------------|
| Okta Suspicious Sign-In | Identity | 25–45% | Identity provider fear |
| ServiceNow Change Approval | ITSM | 20–40% | SLA pressure + approval authority |
| API Key Expiration | Technology | 30–50% | Production urgency |
| Wire Transfer Alert | Financial | 20–40% | Financial + regulatory |
| Legal Case Documents | Legal | 25–45% | Lawsuit fear |
| BBB Complaint | Government | 30–50% | Business authority |

---

## Industry Benchmarks

Based on published research from Proofpoint, KnowBe4, and Cofense (2022–2024):

### Click Rates by Industry (Simulated Phishing)

| Industry | Baseline (Year 1) | Mature Program (Year 3+) |
|----------|-------------------|--------------------------|
| Healthcare | 32–45% | 8–15% |
| Financial Services | 25–38% | 5–12% |
| Technology | 20–35% | 4–10% |
| Manufacturing | 28–42% | 8–14% |
| Education | 35–50% | 10–18% |
| Government | 22–38% | 6–12% |
| Retail/Hospitality | 30–45% | 9–16% |
| Legal | 20–32% | 5–10% |

### Reporting Rates by Maturity

The reporting rate (employees who report phishing to IT rather than clicking) is a more meaningful metric than click rate alone.

| Program Maturity | Reporting Rate | Avg Time to Report |
|-----------------|---------------|--------------------|
| Year 1 | 10–25% | 4–8 hours |
| Year 2 | 30–50% | 1–3 hours |
| Year 3+ | 60–80% | < 30 minutes |

---

## Program Maturity Model

### Level 1 — Baseline (0–12 months)
- Click rate: 35–60% on beginner templates
- Reporting rate: < 20%
- **Goal:** Establish baseline, begin consistent training cadence
- **Recommended templates:** Delivery, IT Security (beginner), HR/Payroll
- **Campaign frequency:** Monthly

### Level 2 — Building Awareness (12–24 months)
- Click rate: 15–35% on intermediate templates
- Reporting rate: 30–50%
- **Goal:** Shift from clicking to reporting; introduce difficulty progression
- **Recommended templates:** Intermediate across all categories
- **Campaign frequency:** 2× monthly with immediate education on click

### Level 3 — Mature Program (24+ months)
- Click rate: < 10% on advanced templates
- Reporting rate: > 60%
- **Goal:** Maintain vigilance, target advanced scenarios, identify repeat offenders
- **Recommended templates:** Advanced (Okta, ITSM, QR/quishing, wire transfer)
- **Campaign frequency:** Ongoing; blend real reported threats into training

---

## Measuring Real Improvement

Track these metrics over time to quantify program effectiveness:

```
Click Rate Reduction:     (baseline_rate - current_rate) / baseline_rate × 100
Reporting Rate:           reports / campaign_recipients × 100
Mean Time to Report:      avg(report_timestamp - send_timestamp)
Repeat Clicker Rate:      employees_clicked_2+_times / total_employees × 100
Training Completion:      completed_training / total_employees × 100
```

### Example OKR Framework

**Objective:** Reduce phishing susceptibility across the organization

| Key Result | Q1 Target | Q2 Target | Year End |
|-----------|-----------|-----------|----------|
| Click rate on intermediate templates | < 30% | < 20% | < 12% |
| Reporting rate | > 25% | > 40% | > 65% |
| Mean time to report | < 4 hours | < 2 hours | < 45 min |
| Training completion within 24h of click | > 80% | > 90% | > 95% |
| Repeat clickers (2+ campaigns) | Track only | < 15% | < 8% |

---

## Segment-Specific Benchmarks

### By Department

Some departments are higher-risk due to their access levels or exposure:

| Department | Risk Level | Recommended Template Categories |
|-----------|-----------|--------------------------------|
| Finance/Accounting | 🔴 Critical | Wire transfer, HR/Payroll, e-signature |
| HR | 🔴 Critical | HR/Payroll, e-signature, IT security |
| IT/Engineering | 🟡 High | API/Developer, Identity (Okta), ITSM |
| Executive/Leadership | 🟡 High | Legal, government, corporate, wire transfer |
| Operations | 🟡 High | ITSM, cloud services, delivery |
| Sales/Customer Success | 🟠 Medium | DocuSign, Salesforce/CRM alerts, social media |
| General Staff | 🟢 Standard | Delivery, HR, cloud services, entertainment |

### By Role Seniority

| Seniority | Pattern | Appropriate Difficulty |
|-----------|---------|----------------------|
| Individual Contributors | Higher click rates, faster reporters after training | Beginner → Intermediate |
| Managers | Lower click rates but higher authority targets | Intermediate → Advanced |
| Directors/VP | Lowest click rates; targeted by nation-state tactics | Advanced only |
| C-Suite | Extreme targeting (whaling) outside scope of this tool | Advanced + custom |

---

## Contributing Benchmark Data

If your organization uses these templates and would like to contribute anonymized click rate data to improve the benchmarks above:

1. Open a GitHub Issue with the label `benchmark-data`
2. Include: template name, employee count, click rate, reporting rate, approximate industry
3. **Do not include** any PII, company names, or identifiable information

All contributed data will be aggregated and used to improve the benchmark ranges above. See [CONTRIBUTING.md](../CONTRIBUTING.md) for details.

---

## References

- Proofpoint State of the Phish 2024
- KnowBe4 Phishing Industry Benchmarks 2023
- Cofense Annual Phishing Intelligence Report 2023
- Verizon DBIR 2024 (Human Element findings)
- SANS Security Awareness Report 2023
