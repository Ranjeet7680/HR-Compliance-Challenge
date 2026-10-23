# Emirates Group HR Continuous Compliance Intelligence Platform
### Continuous 100% Transaction Auditing • Explainable AI • Human-in-the-Loop Governance

[![Emirates Group](https://img.shields.io/badge/Emirates%20Group-HR%20Governance-D71921?style=for-the-badge)](https://www.emirates.com)
[![Coverage](https://img.shields.io/badge/Audit%20Coverage-100%25%20(Zero%20Sampling)-10B981?style=for-the-badge)](#)
[![Explainable AI](https://img.shields.io/badge/Explainability-English%20%26%20Arabic%20(العربية)-C5A059?style=for-the-badge)](#)
[![Human in the Loop](https://img.shields.io/badge/Governance-Human%20in%20the%20Loop-4F46E5?style=for-the-badge)](#)
[![UAE PDPL](https://img.shields.io/badge/Data%20Privacy-UAE%20PDPL%20%26%20GDPR-0284C7?style=for-the-badge)](#)

---

## ✈️ Executive Overview

Emirates Group processes a very high volume of HR transactions every month across **Emirates Airline, dnata, Emirates Flight Catering, and Corporate Headquarters**—including new hires, salary adjustments, housing allowances, flight crew certifications, lateral transfers, and separations. Many start with manual input or self-service workflows. 

Auditing by periodic manual sampling (e.g., 5% to 10%) leaves major gaps: **issues surface late, coverage is uneven, and audit readiness takes heavy effort**.

**This platform replaces manual sampling with continuous 100% automated auditing.** It evaluates every transaction against 18 formal Emirates Group policy rules and unsupervised machine learning behavioral models, explains every exception in plain conversational language (English and Arabic), provides exact cited evidence, routes exceptions to accountable owners with corrective actions, and preserves human approval authority.

---

## 🏆 Key Features & Innovations

| Feature | Description | Status |
| :--- | :--- | :--- |
| **100% Population Coverage** | Audits every transaction across 12 months with sub-3-second batch evaluation. Zero sampling blind spots. | ✅ Production Ready |
| **Bilingual Explainable AI** | Translates complex policy clauses into clear English and Arabic (`العربية`) with native RTL direction support. | ✅ Production Ready |
| **Cited Evidence & Audit Proof** | Displays exact key-value mathematical discrepancies (e.g. `amount=AED 18,500; limit=AED 10,000; excess=AED 8,500`). | ✅ Production Ready |
| **Human-in-the-Loop (HITL)** | Inviolable guardrail: The tool recommends; an authorized human decides. Zero automatic mutations to master records. | ✅ Guardrail Enforced |
| **No-Code NLP Rule Studio** | Allows HR compliance analysts to type new rules in plain English (e.g. *"Flag housing allowance exceeding 12,000 AED for Grade 6 or below"*), compiles into executable AST logic, simulates impact, and activates with one click. | ✅ Implemented |
| **Unsupervised Anomaly Detector** | Uses scikit-learn Isolation Forest and Z-scores to flag behavioral outliers beyond written rules (velocity surges, off-hour filings). | ✅ 150 Patterns Isolated |
| **Procedural Justice & Fairness** | Generates empathetic, non-punitive "Fair Notices" for employees, monitors Adverse Impact Ratios across Grade Bands, and provides a 1-click appeal channel. | ✅ Fully Integrated |
| **Official Submission Output** | Pre-generated `audit_findings_output.csv` matching `data/finding_format.csv` with 100% schema alignment. | ✅ Verified & Ready |

---

## 📂 Project Repository Structure

```
calm-babbage/
├── data/
│   ├── transactions.csv          # 10,000 synthetic HR transactions spanning 12 months
│   ├── employees.csv             # 2,000 synthetic employee master records
│   ├── policy_rules.md           # 18 formal Emirates Group policy specifications
│   ├── finding_format.csv        # Official schema with 5 worked examples
│   ├── test_transactions.csv     # Unlabelled test dataset for evaluation
│   └── detected_anomalies.csv    # 150 unsupervised ML pattern anomalies
├── engine/
│   ├── rule_engine.py            # High-performance 100% compliance audit engine
│   ├── nlp_rule_parser.py        # Natural language to executable AST compiler
│   ├── anomaly_detector.py       # Unsupervised Isolation Forest & Z-Score scanner
│   ├── fairness_module.py        # Procedural justice, Fair Notice & equity analytics
│   └── generator.py              # Realistic Emirates HR dataset synthesizer
├── backend/
│   └── app.py                    # FastAPI server exposing continuous audit APIs
├── frontend/                     # Interactive React 19 + Tailwind UI Dashboard
│   ├── src/
│   │   ├── App.jsx               # Triage Workbench, Hotspots, NLP Studio, Anomaly Hub
│   │   └── main.jsx
│   ├── index.html                # Bilingual font config (Cairo + Inter)
│   ├── package.json
│   └── vite.config.js
├── docs/
│   ├── SOLUTION_NOTE.md          # 2-page executive & technical note + Responsible AI
│   ├── DEMO_VIDEO_SCRIPT.md      # 3-minute video walkthrough storyboard & narration
│   └── EMIRATES_DEPLOYMENT_GUIDE.md # Azure UAE / Oracle HCM sovereign deployment guide
├── audit_findings_output.csv     # Official findings output (2,761 exceptions)
├── test_audit_findings_output.csv# Flagged exceptions on the unlabelled test file
└── README.md                     # Comprehensive platform documentation
```

---

## 🚀 Quickstart & Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+ & npm

### 1. Run the Entire Full-Stack Application (One Command)
```bash
# Run the FastAPI server (automatically serves the compiled React dashboard at http://localhost:8000)
python backend/app.py
```
Open **[http://localhost:8000](http://localhost:8000)** in your browser!

### 2. (Optional) Run Frontend in Development Mode
```bash
cd frontend
npm run dev
```
Open **[http://localhost:5173](http://localhost:5173)** in your browser.

### 3. Re-generate Synthetic Data or Re-run the Audit Engine
```bash
# 1. Synthesize 2,000 employees & 10,000 transactions
python engine/generator.py

# 2. Run the 100% compliance rule engine & export audit_findings_output.csv
python engine/rule_engine.py

# 3. Run unsupervised anomaly detection
python engine/anomaly_detector.py
```

---

## 📋 The 18 Emirates Policy Rules Enforced

| Rule ID | Policy Name | Severity | Owner | Enforcement Summary |
| :--- | :--- | :--- | :--- | :--- |
| `POL-DOA-001` | Financial Approval Limits | HIGH/CRITICAL | Comp & Benefits Lead | Approver grade limits: Gr 8 max 10k, Gr 10 max 25k, Gr 12 max 60k AED. |
| `POL-SOD-001` | Self-Approval Prohibition | CRITICAL | Internal Audit - Fraud | Employees cannot approve personal benefits, leave, or remuneration. |
| `POL-SOD-002` | Subordinate Inversion Approval | HIGH | HR Compliance Lead | Subordinates cannot approve transactions for senior supervisors. |
| `POL-DOC-001` | Sick Leave Medical Certificate | MEDIUM | Employee Shared Services | DHA medical certificate required for sick leave > 2 consecutive days. |
| `POL-DOC-002` | Attested Dependent Proof | HIGH | Benefits Administration | Attested birth/marriage certificates required for dependent allowances. |
| `POL-DOC-003` | Mandatory Separation Clearance | HIGH | Offboarding Specialist | Resignation letter and handover clearance checklist mandatory for exits. |
| `POL-DOC-004` | Flight Crew GCAA Medical | CRITICAL | Aviation Regulatory Lead | Valid GCAA Class 1 Medical Fitness certificate required for flight crew. |
| `POL-TIM-001` | Retrospective Effective Window | HIGH | Enterprise Internal Audit | Backdating > 30 calendar days prohibited without Group HR SVP waiver. |
| `POL-TIM-002` | Minimum Service In-Role | MEDIUM | Talent Mobility Lead | Minimum 12 months tenure in role required prior to lateral transfer. |
| `POL-TIM-003` | Grade Exit Notice Period | MEDIUM | Payroll Operations Lead | Voluntary notice: 30 days for Gr 1–6; 90 days for Gr 7+ without buyout. |
| `POL-ALLOW-001`| Education Allowance Cap | HIGH | Comp & Benefits Lead | Capped at AED 45,000/year per child; restricted to Grade 8 and above. |
| `POL-ALLOW-002`| Grade Housing Ceilings | HIGH | Payroll Operations Lead | Monthly ceilings: Gr 1-5: 4.5k, Gr 6-8: 9.5k, Gr 9-11: 16k, Gr 12+: 25k AED. |
| `POL-SAL-001` | Off-Cycle Salary Cap (15%) | CRITICAL | Executive Comp Lead | Ad-hoc increments cannot exceed 15% without Promotion Committee. |
| `POL-DUP-001` | Duplicate Allowance Claims | CRITICAL | Payroll Operations Lead | Multiple identical claims for same employee within 30 days prohibited. |
| `POL-LEAVE-001`| Leave Overdraft Ceiling | LOW | Leave Desk | Leave request cannot exceed accrued balance by > 5 emergency days. |
| `POL-PROB-001` | Probationary Mobility Cap | HIGH | Onboarding & Probation | No discretionary increments or transfers during initial 6 months. |
| `POL-SEC-001` | Airside Security Clearance | CRITICAL | Aviation Security Manager | Airport/Ramp/Engineering transfers require active Dubai Airports pass. |
| `POL-REL-001` | Relative Approval Conflict | CRITICAL | Internal Audit & Legal | Approvers cannot authorize benefits for declared relatives or spouses. |

---

## 🛡️ Responsible AI & Guardrail Compliance

1. **Human Authority Preservation:**
   The tool only flags, explains, and recommends; it never mutates master transaction tables. Analysts record explicit decisions (`APPROVED_WITH_WAIVER`, `RETURNED_TO_ORIGINATOR`, `REMEDIATED`, `ESCALATED_TO_AUDIT`) with mandatory audit notes.
2. **Zero Hallucination Guarantee:**
   Explanations and evidence citations are deterministically mapped to verified transaction data fields and codified policy articles.
3. **UAE PDPL & Air-Gapped Readiness:**
   Built on synthetic data. Production architecture deploys inside **Microsoft Azure UAE North (Dubai)** or on-premises within Emirates' private virtual network (VNet) with zero internet data egress.

---

## 👥 Built for Emirates Group Stakeholders

- **HR Compliance Analyst:** Reviews flagged exceptions, inspects bilingual plain-language reasoning, reviews cited data evidence, and takes action.
- **HR Operations Team Lead:** Owns the prioritized operational queue with SLA tracking and workload balancing.
- **Enterprise Internal Audit Lead:** Monitors systemic hotspots, views 12-month compliance curves, and exports complete audit packs in 1 click.
- **Employees (Fairness & Trust):** Receives dignified, non-punitive "Fair Notices" and accesses a 1-click dispute/appeal channel with a 3-day resolution SLA.
