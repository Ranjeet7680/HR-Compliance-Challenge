# Emirates Group HR Compliance Policy Rules Specification
**Document ID:** `EGR-POL-COMP-2026-V3`  
**Governance Scope:** Emirates Airline, dnata, Emirates Group IT, and Subsidiary Business Units  
**Authority:** Emirates Group Internal Audit & HR Governance Directorate  
**Application Posture:** Continuous 100% Pre-Payroll & Post-Transaction Auditing  

---

## 1. Approval Authority & Delegation (DOA)

### POL-DOA-001: Grade-Based Financial Approval Limits
- **Category:** Delegation of Authority (DOA)
- **Rule Description:** Approval of financial HR transactions (salary adjustments, special allowances, retention bonuses) must strictly comply with the designated financial threshold of the approving manager's corporate grade.
- **Enforcement Logic:**
  - Approver Grade `07` - `08` (Manager): Max allowable amount = **AED 10,000**
  - Approver Grade `09` - `10` (Vice President / Head of Dept): Max allowable amount = **AED 25,000**
  - Approver Grade `11` - `12` (Senior Vice President): Max allowable amount = **AED 60,000**
  - Approver Grade `13+` (Executive Vice President / Chief Officer): Required for amounts **> AED 60,000**
- **Exception Severity:** `HIGH` (if exceeded by < 50%), `CRITICAL` (if exceeded by >= 50% or unapproved by Executive)
- **Assigned Action Owner:** HR Operations - Compensation & Benefits Lead
- **Corrective Action:** Route back for secondary counter-approval by an authorized Grade VP/SVP or revoke transaction pending Executive authorization.

---

## 2. Segregation of Duties (SoD)

### POL-SOD-001: Self-Approval Prohibition
- **Category:** Segregation of Duties (SoD)
- **Rule Description:** An employee or manager is strictly prohibited from approving transactions where they are the beneficiary (`requester_id == approver_id` or `employee_id == approver_id`).
- **Enforcement Logic:** Flag whenever `approver_id == employee_id` or `approver_id == requester_id` for personal benefits.
- **Exception Severity:** `CRITICAL`
- **Assigned Action Owner:** Internal Audit - Fraud Risk & HR Governance
- **Corrective Action:** Freeze transaction immediately; initiate audit inquiry into bypass of system workflow segregation controls; re-assign approval to neutral department head.

### POL-SOD-002: Subordinate Inversion Approval
- **Category:** Segregation of Duties (SoD)
- **Rule Description:** An employee cannot approve any compensation, transfer, or leave transaction for an individual who is their administrative manager or who holds a senior corporate grade.
- **Enforcement Logic:** Flag if `approver_grade < employee_grade` or if `approver.manager_id == employee_id`.
- **Exception Severity:** `HIGH`
- **Assigned Action Owner:** HR Compliance Operations Lead
- **Corrective Action:** Nullify approval and re-route to the supervisor of the employee's reporting line (N+2 level).

---

## 3. Mandatory Documentation & Evidence

### POL-DOC-001: Medical Certificate for Extended Sick Leave
- **Category:** Required Documentation
- **Rule Description:** Any sick leave request exceeding two (2) consecutive calendar days must have a DHA (Dubai Health Authority) or licensed medical practitioner sick leave certificate attached.
- **Enforcement Logic:** If `type == "Sick Leave"` and `duration_days > 2` and `documents_attached` does not contain `"Medical_Certificate"`.
- **Exception Severity:** `MEDIUM`
- **Assigned Action Owner:** HR Operations - Employee Shared Services
- **Corrective Action:** Issue notification to employee requesting valid medical certificate within 5 business days; if unsubmitted, reclassify leave as unpaid leave.

### POL-DOC-002: Attested Proof for Dependent Allowances
- **Category:** Required Documentation
- **Rule Description:** Any addition or upward adjustment of dependent child education or family medical allowance must include attested government certificates (Birth Certificate, Marriage Certificate, or Legal Guardianship).
- **Enforcement Logic:** If `type in ["Education Allowance", "Family Dependent Allowance"]` and `documents_attached` does not contain `"Attested_Dependent_Certificate"`.
- **Exception Severity:** `HIGH`
- **Assigned Action Owner:** HR Operations - Benefits Administration
- **Corrective Action:** Suspend allowance disbursement pending document submission; notify employee via Fair Notice portal.

### POL-DOC-003: Mandatory Separation Clearance for Exits
- **Category:** Required Documentation
- **Rule Description:** Employee separation/exit transactions must have an attached Signed Resignation Letter (or Termination Notice) and Departmental Handover Clearance.
- **Enforcement Logic:** If `type == "Exit"` and (`documents_attached` does not contain `"Resignation_Letter"` or does not contain `"Handover_Clearance"`).
- **Exception Severity:** `HIGH`
- **Assigned Action Owner:** Talent Operations - Offboarding Specialist
- **Corrective Action:** Halt final settlement calculation; contact department coordinator to complete mandatory property and asset handover checklist.

### POL-DOC-004: Flight Crew & Safety Medical Fitness (GCAA)
- **Category:** Regulatory Aviation Compliance
- **Rule Description:** Flight Deck Crew (Captains, First Officers) and Cabin Crew transactions involving transfer, reinstatement, or flying allowance activation require a valid General Civil Aviation Authority (GCAA) Class 1 Medical Fitness certificate.
- **Enforcement Logic:** If `department in ["Flight Operations", "Cabin Crew"]` and `type in ["Transfer", "Flight Crew Reinstatement"]` and `documents_attached` does not contain `"GCAA_Medical_Clearance"`.
- **Exception Severity:** `CRITICAL`
- **Assigned Action Owner:** Aviation Crew HR & Regulatory Compliance Lead
- **Corrective Action:** Ground roster clearance immediately; prevent flight assignment until GCAA Aeromedical validation is verified.

---

## 4. Timing Windows & Retrospective Approvals

### POL-TIM-001: Retrospective Effective Date Window (Max 30 Days)
- **Category:** Timing & Governance
- **Rule Description:** HR transactions must not have an effective date that precedes the transaction submission date by more than thirty (30) calendar days, unless supported by written Group HR Senior Vice President approval.
- **Enforcement Logic:** Flag if `(submission_date - effective_date) > 30 days` and `documents_attached` does not contain `"SVP_Retrospective_Waiver"`.
- **Exception Severity:** `HIGH`
- **Assigned Action Owner:** Enterprise Internal Audit Lead
- **Corrective Action:** Review payroll adjustment ledger; require business unit SVP sign-off justifying retrospective adjustment.

### POL-TIM-002: Minimum In-Role Tenure Before Lateral Transfer
- **Category:** Talent Mobility & Timing
- **Rule Description:** Employees must complete a minimum of twelve (12) consecutive months of service in their current position and grade before being eligible for an internal lateral transfer or departmental reassignment, unless part of documented corporate restructuring.
- **Enforcement Logic:** Flag if `type == "Transfer"` and `tenure_in_role_months < 12` and `transfer_reason != "Corporate Restructuring"`.
- **Exception Severity:** `MEDIUM`
- **Assigned Action Owner:** Talent Mobility & Succession Lead
- **Corrective Action:** Request Business Partner justification or hold transfer until completion of 12-month milestone.

### POL-TIM-003: Grade-Based Separation Notice Period
- **Category:** Separation Compliance
- **Rule Description:** Voluntary resignations must respect standard contractual notice periods: minimum 30 calendar days for Grades 01-06; minimum 90 calendar days for Grades 07 and above.
- **Enforcement Logic:** Flag if `type == "Exit"` and `resignation_type == "Voluntary"` and `(effective_date - submission_date) < required_notice_days` without `"Notice_Period_Waiver"`.
- **Exception Severity:** `MEDIUM`
- **Assigned Action Owner:** HR Shared Services - Payroll Operations
- **Corrective Action:** Validate whether early release was formally agreed and if notice buyout deduction was applied to end-of-service settlement.

---

## 5. Compensation, Allowances & Benefits Limits

### POL-ALLOW-001: Maximum Children's Education Allowance Cap
- **Category:** Compensation & Benefits
- **Rule Description:** Annual education allowance is capped according to employee eligibility criteria: maximum AED 45,000 per child per academic year, up to a maximum of 3 eligible dependents, applicable only to Grade 08 and above.
- **Enforcement Logic:** Flag if `type == "Education Allowance"` and (`amount > 45000` or `employee_grade < 8` or `dependent_count > 3`).
- **Exception Severity:** `HIGH`
- **Assigned Action Owner:** Compensation & Benefits Specialist
- **Corrective Action:** Adjust allowance claim down to policy limit or recover unauthorized overpayment via payroll adjustment.

### POL-ALLOW-002: Grade & Location Housing Allowance Ceilings
- **Category:** Compensation & Benefits
- **Rule Description:** Monthly housing allowance disbursements cannot exceed approved grade-band caps:
  - Grades `01` - `05`: Max **AED 4,500 / month**
  - Grades `06` - `08`: Max **AED 9,500 / month**
  - Grades `09` - `11`: Max **AED 16,000 / month**
  - Grades `12+`: Max **AED 25,000 / month**
- **Enforcement Logic:** Flag if `type == "Housing Allowance"` and `amount > grade_cap`.
- **Exception Severity:** `HIGH`
- **Assigned Action Owner:** Payroll Operations Team Lead
- **Corrective Action:** Recalculate monthly disbursement to grade ceiling; notify employee of policy allowance boundaries.

### POL-SAL-001: Maximum Single Off-Cycle Salary Increment Cap (15%)
- **Category:** Compensation & Governance
- **Rule Description:** Any ad-hoc or off-cycle base salary increment cannot exceed fifteen percent (15%) of the employee's existing base salary, unless accompanied by formal Promotion Committee or Group HR SVP approval.
- **Enforcement Logic:** Flag if `type == "Salary Adjustment"` and `increment_percentage > 15.0%` and `documents_attached` does not contain `"Promotion_Committee_Approval"`.
- **Exception Severity:** `CRITICAL`
- **Assigned Action Owner:** Group Remuneration & Executive Compensation Lead
- **Corrective Action:** Cap increase at 15% pending Executive Remuneration Committee formal review.

---

## 6. Integrity, Duplication & Leave Limits

### POL-DUP-001: Duplicate Allowance Claim Prevention
- **Category:** Fraud & Duplicate Prevention
- **Rule Description:** Duplicate reimbursement or allowance claims of the same type submitted for the same employee within the same 30-day payroll processing cycle are strictly prohibited.
- **Enforcement Logic:** Flag if multiple transactions exist for `employee_id` with identical `type` within a 30-day window.
- **Exception Severity:** `CRITICAL`
- **Assigned Action Owner:** HR Compliance Analyst & Payroll Operations
- **Corrective Action:** Void redundant duplicate transaction; verify if earlier payment was already disbursed.

### POL-LEAVE-001: Annual Leave Overdraft Ceiling
- **Category:** Leave Administration
- **Rule Description:** Annual leave requests must not exceed the employee's current accrued leave balance by more than five (5) days advance emergency overdraft.
- **Enforcement Logic:** Flag if `type == "Annual Leave"` and `(requested_days - accrued_balance) > 5 days`.
- **Exception Severity:** `LOW`
- **Assigned Action Owner:** HR Shared Services - Leave Desk
- **Corrective Action:** Notify employee and line manager; reduce requested dates to available balance or designate surplus as unpaid leave.

### POL-PROB-001: Probationary Period Mobility & Increment Restriction
- **Category:** Probation Governance
- **Rule Description:** Employees within their initial six (6) month probationary period are ineligible for discretionary salary adjustments, retention allowances, or non-essential departmental transfers.
- **Enforcement Logic:** Flag if `tenure_months < 6` and `type in ["Salary Adjustment", "Discretionary Allowance", "Transfer"]`.
- **Exception Severity:** `HIGH`
- **Assigned Action Owner:** Talent Operations - Onboarding & Probation Lead
- **Corrective Action:** Postpone transaction until successful completion and confirmation of the 6-month probationary review.

---

## 7. Aviation Security & Regulatory Controls

### POL-SEC-001: Airside Security Clearance & Pass Verification
- **Category:** Aviation Security Compliance
- **Rule Description:** Transfers or hires into dnata Airport Operations, Ramp Handling, or Aircraft Maintenance requiring airside terminal access must hold verified Dubai Airports / GCAA security clearance.
- **Enforcement Logic:** Flag if `department in ["Airport Operations", "Ramp Handling", "Engineering"]` and `type in ["Hire", "Transfer"]` and `documents_attached` does not contain `"Airside_Security_Pass"`.
- **Exception Severity:** `CRITICAL`
- **Assigned Action Owner:** Aviation Security & Compliance Manager
- **Corrective Action:** Suspend airside roster assignment; expedite background vetting with Dubai Police / GCAA authorities.

### POL-REL-001: Conflict of Interest & Close Relative Approval
- **Category:** Ethics & Governance
- **Rule Description:** Approvers must not approve transactions for individuals flagged in the HR database as direct relatives, spouses, or shared-household members.
- **Enforcement Logic:** Flag if `is_declared_relative(employee_id, approver_id) == True`.
- **Exception Severity:** `CRITICAL`
- **Assigned Action Owner:** Enterprise Internal Audit Lead & Legal Counsel
- **Corrective Action:** Transfer approval to Independent Governance Officer; issue mandatory disclosure conflict notice.
