"""
Emirates Group HR Continuous Compliance Rule Engine
Evaluates 100% of transactions against 18 formal Emirates policy rules.
Generates plain-language English & Arabic explanations, exact cited evidence,
severity ratings, and operational routing owners.
"""

import datetime
import pandas as pd
import numpy as np

RULE_DEFINITIONS = {
    "POL-DOA-001": {
        "name": "Grade-Based Financial Approval Limits",
        "category": "Delegation of Authority (DOA)",
        "owner": "HR Operations - Compensation & Benefits Lead",
        "description": "Approval limits: Grade <=8: AED 10k, Grade 9-10: AED 25k, Grade 11-12: AED 60k, Grade 13+: Unlimited."
    },
    "POL-SOD-001": {
        "name": "Self-Approval Prohibition",
        "category": "Segregation of Duties (SoD)",
        "owner": "Internal Audit - Fraud Risk & HR Governance",
        "description": "Employees cannot approve transactions where they are the beneficiary or requester."
    },
    "POL-SOD-002": {
        "name": "Subordinate Inversion Approval",
        "category": "Segregation of Duties (SoD)",
        "owner": "HR Compliance Operations Lead",
        "description": "Subordinates cannot approve compensation or leave for higher-grade supervisors."
    },
    "POL-DOC-001": {
        "name": "Medical Certificate for Extended Sick Leave",
        "category": "Required Documentation",
        "owner": "HR Operations - Employee Shared Services",
        "description": "Medical certificate required for sick leave exceeding 2 consecutive days."
    },
    "POL-DOC-002": {
        "name": "Attested Proof for Dependent Allowances",
        "category": "Required Documentation",
        "owner": "HR Operations - Benefits Administration",
        "description": "Attested birth/marriage certificate required for education and family allowances."
    },
    "POL-DOC-003": {
        "name": "Mandatory Separation Clearance for Exits",
        "category": "Required Documentation",
        "owner": "Talent Operations - Offboarding Specialist",
        "description": "Signed resignation letter and departmental handover clearance mandatory for exits."
    },
    "POL-DOC-004": {
        "name": "Flight Crew Aviation Medical Clearance",
        "category": "Regulatory Aviation Compliance",
        "owner": "Aviation Crew HR & Regulatory Compliance Lead",
        "description": "GCAA Class 1 Medical Fitness certificate required for Flight Operations / Cabin Crew transfers."
    },
    "POL-TIM-001": {
        "name": "Retrospective Effective Date Window",
        "category": "Timing & Governance",
        "owner": "Enterprise Internal Audit Lead",
        "description": "Effective date cannot be backdated >30 days without Group HR SVP waiver."
    },
    "POL-TIM-002": {
        "name": "Minimum In-Role Service Tenure",
        "category": "Talent Mobility & Timing",
        "owner": "Talent Mobility & Succession Lead",
        "description": "Minimum 12 months in current role required before lateral departmental transfer."
    },
    "POL-TIM-003": {
        "name": "Grade-Based Separation Notice Period",
        "category": "Separation Compliance",
        "owner": "HR Shared Services - Payroll Operations",
        "description": "Voluntary separation notice: 30 days for Grade 1-6, 90 days for Grade 7+."
    },
    "POL-ALLOW-001": {
        "name": "Maximum Education Allowance Cap",
        "category": "Compensation & Benefits",
        "owner": "Compensation & Benefits Specialist",
        "description": "Education allowance capped at AED 45,000 per child, restricted to Grade 8+."
    },
    "POL-ALLOW-002": {
        "name": "Grade & Location Housing Allowance Ceilings",
        "category": "Compensation & Benefits",
        "owner": "Payroll Operations Team Lead",
        "description": "Monthly housing allowance caps: Gr 1-5: 4.5k, Gr 6-8: 9.5k, Gr 9-11: 16k, Gr 12+: 25k AED."
    },
    "POL-SAL-001": {
        "name": "Off-Cycle Salary Increment Cap (15%)",
        "category": "Compensation & Governance",
        "owner": "Group Remuneration & Executive Compensation Lead",
        "description": "Off-cycle salary increases cannot exceed 15% without Promotion Committee approval."
    },
    "POL-DUP-001": {
        "name": "Duplicate Allowance Claim Prevention",
        "category": "Fraud & Duplicate Prevention",
        "owner": "HR Compliance Analyst & Payroll Operations",
        "description": "Multiple identical allowance claims for same employee within 30 days are prohibited."
    },
    "POL-LEAVE-001": {
        "name": "Annual Leave Overdraft Ceiling",
        "category": "Leave Administration",
        "owner": "HR Shared Services - Leave Desk",
        "description": "Leave request cannot exceed accrued balance by more than 5 days advance overdraft."
    },
    "POL-PROB-001": {
        "name": "Probationary Period Mobility & Increment Restriction",
        "category": "Probation Governance",
        "owner": "Talent Operations - Onboarding & Probation Lead",
        "description": "Employees under 6 months tenure ineligible for ad-hoc increments or transfers."
    },
    "POL-SEC-001": {
        "name": "Airside Security Clearance Compliance",
        "category": "Aviation Security Compliance",
        "owner": "Aviation Security & Compliance Manager",
        "description": "Transfers/hires into Airport Operations/Ramp/Engineering require Airside Security Pass."
    },
    "POL-REL-001": {
        "name": "Conflict of Interest & Relative Approval",
        "category": "Ethics & Governance",
        "owner": "Enterprise Internal Audit Lead & Legal Counsel",
        "description": "Approvers cannot authorize transactions for declared relatives or household members."
    }
}

class ComplianceRuleEngine:
    def __init__(self, employees_df=None):
        self.employees_df = employees_df
        self.emp_map = {}
        if employees_df is not None:
            self.emp_map = {row["employee_id"]: row.to_dict() for _, row in employees_df.iterrows()}

    def evaluate_batch(self, transactions_df):
        findings = []
        finding_counter = 1
        
        # Sort transactions for temporal duplicate analysis
        txns_sorted = transactions_df.sort_values(by="submission_date").copy()
        txns_records = txns_sorted.to_dict(orient="records")
        
        # Track employee allowance history for POL-DUP-001
        emp_history = {} # emp_id -> list of (sub_date, txn_type, amount, txn_id)

        for txn in txns_records:
            t_id = txn["transaction_id"]
            e_id = txn["employee_id"]
            t_type = txn["transaction_type"]
            amount = float(txn.get("amount_aed", 0) or 0)
            duration = int(txn.get("duration_days", 0) or 0)
            sub_date_str = str(txn["submission_date"])[:10]
            eff_date_str = str(txn["effective_date"])[:10]
            sub_date = datetime.date.fromisoformat(sub_date_str)
            eff_date = datetime.date.fromisoformat(eff_date_str)
            
            req_id = str(txn.get("requester_id", ""))
            app_id = str(txn.get("approver_id", ""))
            app_grade = int(txn.get("approver_grade", 0) or 0)
            emp_grade = int(txn.get("grade", 0) or 0)
            docs = str(txn.get("documents_attached", "")).split(";")
            docs = [d.strip() for d in docs if d.strip()]
            dept = str(txn.get("department", ""))
            tenure_m = float(txn.get("tenure_months", 0) or 0)
            base_sal = float(txn.get("base_salary_aed", 0) or 0)
            accrued_leave = int(txn.get("accrued_leave_balance", 0) or 0)
            resig_type = str(txn.get("resignation_type", "N/A"))

            emp_master = self.emp_map.get(e_id, {})
            rel_id = emp_master.get("declared_relative_id", "")

            # -------------------------------------------------------------
            # Rule 1: POL-DOA-001 (Financial Approval Limits)
            # -------------------------------------------------------------
            if amount > 0:
                limit = 1000000000 # default high
                if app_grade <= 8:
                    limit = 10000
                elif app_grade <= 10:
                    limit = 25000
                elif app_grade <= 12:
                    limit = 60000

                if amount > limit:
                    excess = amount - limit
                    sev = "CRITICAL" if excess >= (limit * 0.5) or amount > 60000 else "HIGH"
                    findings.append(self._create_finding(
                        finding_counter, t_id, e_id, "POL-DOA-001", sev,
                        f"Financial transaction of AED {amount:,.2f} approved by Grade {app_grade:02d} Approver ({txn.get('approver_name')}), which exceeds the grade authority ceiling of AED {limit:,.2f} by AED {excess:,.2f}.",
                        f"معاملة مالية بقيمة {amount:,.2f} درهم تم اعتمادها من قبل مفوض بالدرجة {app_grade:02d}، متجاوزة سقف الصلاحية المالية للدرجة (AED {limit:,.2f}) بمقدار {excess:,.2f} درهم.",
                        f"amount=AED {amount:.2f}; approver_grade={app_grade}; grade_limit=AED {limit:.2f}; excess=AED {excess:.2f}",
                        "Escalate transaction to Grade 10+ Department VP or Group Remuneration Committee for retroactive authorization, or revise financial sum.",
                        "تصعيد المعاملة إلى نائب رئيس الدائرة (الدرجة 10+) أو لجنة المكافآت للمصادقة الاستثنائية، أو تعديل المبلغ لسقف الدرجة."
                    ))
                    finding_counter += 1

            # -------------------------------------------------------------
            # Rule 2: POL-SOD-001 (Self-Approval Prohibition)
            # -------------------------------------------------------------
            if (req_id == app_id and req_id == e_id) or (app_id == e_id and t_type in ["Salary Adjustment", "Housing Allowance", "Education Allowance", "Discretionary Allowance", "Annual Leave"]):
                findings.append(self._create_finding(
                    finding_counter, t_id, e_id, "POL-SOD-001", "CRITICAL",
                    f"Employee {e_id} ({txn.get('employee_name')}) approved their own {t_type} transaction. Emirates Group HR policy strictly prohibits self-approval of personal remuneration or leave.",
                    f"قام الموظف {e_id} باعتماد معاملة {t_type} الخاصة به ذاتياً، وهو ما يخالف قواعد الفصل بين المهام ومكافحة تضارب المصالح.",
                    f"employee_id={e_id}; requester_id={req_id}; approver_id={app_id}; transaction_type={t_type}",
                    "Immediately freeze workflow processing; revoke line self-authorization and assign approval to neutral Department Head.",
                    "إيقاف سير المعاملة فوراً، وإلغاء الاعتماد الذاتي، وإعادة توجيه الطلب إلى مدير الدائرة المستقل للبت فيه."
                ))
                finding_counter += 1

            # -------------------------------------------------------------
            # Rule 3: POL-SOD-002 (Subordinate Inversion Approval)
            # -------------------------------------------------------------
            if app_grade < emp_grade:
                findings.append(self._create_finding(
                    finding_counter, t_id, e_id, "POL-SOD-002", "HIGH",
                    f"Transaction for Grade {emp_grade:02d} employee was approved by Grade {app_grade:02d} subordinate ({txn.get('approver_name')}). Subordinates cannot authorize transactions for higher-grade supervisors.",
                    f"تم اعتماد المعاملة لموظف بالدرجة {emp_grade:02d} من قبل موظف أدنى رتبة بالدرجة {app_grade:02d}، وهو ما يخالف الهيكل الإشرافي المعتمد.",
                    f"employee_grade={emp_grade}; approver_grade={app_grade}; hierarchy_inversion=TRUE",
                    "Void subordinate approval signature; re-route to the supervisor of the employee's reporting line (N+2 level).",
                    "إلغاء توقيع الموظف الأدنى، وإعادة توجيه المعاملة إلى الرئيس المباشر الأعلى (المستوى N+2) للاعتماد النظامي."
                ))
                finding_counter += 1

            # -------------------------------------------------------------
            # Rule 4: POL-DOC-001 (Sick Leave Medical Certificate)
            # -------------------------------------------------------------
            if t_type == "Sick Leave" and duration > 2 and "Medical_Certificate" not in docs:
                findings.append(self._create_finding(
                    finding_counter, t_id, e_id, "POL-DOC-001", "MEDIUM",
                    f"Sick leave submitted for {duration} consecutive calendar days without a mandatory Dubai Health Authority (DHA) medical certificate. Policy requires medical proof for absences > 2 days.",
                    f"تم تقديم طلب إجازة مرضية لمدة {duration} أيام دون إرفاق الشهادة الطبية المعتمدة من هيئة الصحة بدبي (DHA). السياسة تلزم بإرفاق تقرير طبي للغياب المتجاوز يومين.",
                    f"transaction_type=Sick Leave; duration_days={duration}; documents_attached={';'.join(docs) or 'None'}",
                    "Issue automated Fair Notice request to employee to upload certified DHA medical certificate within 5 working days.",
                    "إرسال إشعار التزام ودي للموظف عبر البوابة لإرفاق التقرير الطبي خلال 5 أيام عمل قبل خصم الإجازة."
                ))
                finding_counter += 1

            # -------------------------------------------------------------
            # Rule 5: POL-DOC-002 (Attested Proof for Dependent Allowances)
            # -------------------------------------------------------------
            if t_type in ["Education Allowance", "Family Dependent Allowance"] and "Attested_Dependent_Certificate" not in docs:
                findings.append(self._create_finding(
                    finding_counter, t_id, e_id, "POL-DOC-002", "HIGH",
                    f"{t_type} claim of AED {amount:,.2f} is missing mandatory attested dependent documentation (birth/marriage certificate or legal guardianship proof).",
                    f"طلب {t_type} بقيمة {amount:,.2f} درهم يفتقر إلى وثائق إثبات الإعالة المصدقة رسمياً (شهادة ميلاد أو زواج مصدقة).",
                    f"transaction_type={t_type}; amount=AED {amount:.2f}; missing_required_doc=Attested_Dependent_Certificate",
                    "Suspend allowance payout; notify employee to upload attested consular/ministry certificates via Employee Portal.",
                    "تعليق صرف البدل وإشعار الموظف برفع الشهادات المصدقة من الجهات الرسمية عبر بوابة الخدمة الذاتية."
                ))
                finding_counter += 1

            # -------------------------------------------------------------
            # Rule 6: POL-DOC-003 (Mandatory Separation Clearance for Exits)
            # -------------------------------------------------------------
            if t_type == "Exit" and ("Resignation_Letter" not in docs or "Handover_Clearance" not in docs):
                missing = []
                if "Resignation_Letter" not in docs: missing.append("Resignation_Letter")
                if "Handover_Clearance" not in docs: missing.append("Handover_Clearance")
                findings.append(self._create_finding(
                    finding_counter, t_id, e_id, "POL-DOC-003", "HIGH",
                    f"Employee exit processing initiated without mandatory offboarding documentation: missing {', '.join(missing)}.",
                    f"بدأت إجراءات إنهاء خدمة الموظف دون استكمال الوثائق الإلزامية: وثائق مفقودة ({', '.join(missing)}).",
                    f"transaction_type=Exit; missing_docs={';'.join(missing)}; documents_attached={';'.join(docs) or 'None'}",
                    "Hold final end-of-service settlement calculation until departmental asset clearance and signed letter are archived.",
                    "تجميد احتساب مستحقات نهاية الخدمة لحين استلام استمارة إبراء الذمة واستلام العهد وخطاب الاستقالة الموقع."
                ))
                finding_counter += 1

            # -------------------------------------------------------------
            # Rule 7: POL-DOC-004 (Flight Crew Aviation Medical Clearance)
            # -------------------------------------------------------------
            if dept in ["Flight Operations", "Cabin Crew"] and t_type in ["Transfer", "Flight Crew Reinstatement"] and "GCAA_Medical_Clearance" not in docs:
                findings.append(self._create_finding(
                    finding_counter, t_id, e_id, "POL-DOC-004", "CRITICAL",
                    f"Flight crew transaction in {dept} is missing mandatory GCAA Class 1 Medical Fitness clearance. Civil aviation regulations mandate current aeromedical validation.",
                    f"معاملة طاقم الطيران في {dept} تفتقر إلى شهادة اللياقة الطبية من الفئة الأولى المعتمدة من الهيئة العامة للطيران المدني (GCAA).",
                    f"department={dept}; transaction_type={t_type}; missing_mandatory_clearance=GCAA_Medical_Clearance",
                    "Immediately ground flight roster eligibility; notify Chief Pilot and Medical Operations to confirm GCAA certification.",
                    "إيقاف جدولة رحلات الطيار/المضيف فوراً وإخطار رئيس الطيارين والعمليات الطبية للتأكد من الترخيص."
                ))
                finding_counter += 1

            # -------------------------------------------------------------
            # Rule 8: POL-TIM-001 (Retrospective Effective Date Window)
            # -------------------------------------------------------------
            delta_backdate = (sub_date - eff_date).days
            if delta_backdate > 30 and "SVP_Retrospective_Waiver" not in docs:
                findings.append(self._create_finding(
                    finding_counter, t_id, e_id, "POL-TIM-001", "HIGH",
                    f"Transaction effective date ({eff_date}) precedes submission date ({sub_date}) by {delta_backdate} days, exceeding the 30-day policy backdating limit without SVP authorization.",
                    f"تاريخ سريان المعاملة ({eff_date}) يسبق تاريخ التقديم ({sub_date}) بـ {delta_backdate} يوماً، متجاوزاً مهلة الرجعية المسموحة (30 يوماً) دون استثناء معتمد.",
                    f"submission_date={sub_date}; effective_date={eff_date}; backdated_days={delta_backdate}; max_allowed_days=30",
                    "Require business unit Senior Vice President written retroactive waiver and audit justification before payroll execution.",
                    "طلب استثناء خطي معتمد من نائب الرئيس الأول ومبررات التدقيق قبل إدراج التعديل بأثر رجعي في الرواتب."
                ))
                finding_counter += 1

            # -------------------------------------------------------------
            # Rule 9: POL-TIM-002 (Minimum In-Role Service Tenure)
            # -------------------------------------------------------------
            if t_type == "Transfer" and tenure_m < 12.0 and "Restructure_Waiver" not in docs:
                findings.append(self._create_finding(
                    finding_counter, t_id, e_id, "POL-TIM-002", "MEDIUM",
                    f"Lateral transfer requested with only {tenure_m:.1f} months tenure in current position. Policy requires a minimum of 12 months service before internal transfers.",
                    f"طلب نقل داخلي للموظف بعد قضاء {tenure_m:.1f} شهراً فقط في منصبه الحالي، بينما تنص السياسة على إتمام 12 شهراً كحد أدنى.",
                    f"transaction_type=Transfer; tenure_months={tenure_m:.1f}; required_minimum_months=12.0",
                    "Obtain VP Talent Mobility justification or defer transfer effective date until the 12-month tenure threshold is met.",
                    "الحصول على موافقة استثنائية من نائب رئيس تنقل الكفاءات أو تأجيل النقل حتى إتمام فترة الـ 12 شهراً."
                ))
                finding_counter += 1

            # -------------------------------------------------------------
            # Rule 10: POL-TIM-003 (Grade-Based Separation Notice Period)
            # -------------------------------------------------------------
            if t_type == "Exit" and resig_type == "Voluntary":
                notice_days = (eff_date - sub_date).days
                req_notice = 30 if emp_grade <= 6 else 90
                if notice_days < req_notice and "Notice_Period_Waiver" not in docs:
                    findings.append(self._create_finding(
                        finding_counter, t_id, e_id, "POL-TIM-003", "MEDIUM",
                        f"Voluntary exit notice of {notice_days} days is below contractual requirement of {req_notice} days for Grade {emp_grade:02d} without an authorized notice buyout or waiver.",
                        f"فترة إشعار الاستقالة المقدمة ({notice_days} يوماً) أقل من المهلة العقدية ({req_notice} يوماً) للدرجة {emp_grade:02d} دون إبراء ذمة أو شراء فترة الإشعار.",
                        f"employee_grade={emp_grade}; actual_notice_days={notice_days}; contractual_required_days={req_notice}",
                        "Verify whether early release notice buyout was calculated and deducted from end-of-service settlement.",
                        "التحقق من موافقة الدائرة على الاستقالة المبكرة وتطبيق خصم بدل فترة الإشعار من مستحقات نهاية الخدمة."
                    ))
                    finding_counter += 1

            # -------------------------------------------------------------
            # Rule 11: POL-ALLOW-001 (Maximum Education Allowance Cap)
            # -------------------------------------------------------------
            if t_type == "Education Allowance":
                if emp_grade < 8:
                    findings.append(self._create_finding(
                        finding_counter, t_id, e_id, "POL-ALLOW-001", "HIGH",
                        f"Education allowance claim of AED {amount:,.2f} submitted for Grade {emp_grade:02d} employee. Policy restricts education allowance eligibility to Grade 08 and above.",
                        f"طلب بدل تعليم بقيمة {amount:,.2f} درهم لموظف بالدرجة {emp_grade:02d}، في حين يقتصر استحقاق بدل التعليم على الدرجة 08 فما فوق.",
                        f"employee_grade={emp_grade}; eligible_minimum_grade=8; amount=AED {amount:.2f}",
                        "Reject ineligible education claim; notify employee of policy eligibility guidelines.",
                        "رفض طلب بدل التعليم لعدم انطباق شروط الاستحقاق، وإشعار الموظف بضوابط البدلات المعتمدة."
                    ))
                    finding_counter += 1
                elif amount > 45000:
                    excess = amount - 45000
                    findings.append(self._create_finding(
                        finding_counter, t_id, e_id, "POL-ALLOW-001", "HIGH",
                        f"Education allowance claim of AED {amount:,.2f} exceeds annual policy cap of AED 45,000.00 by AED {excess:,.2f}.",
                        f"طلب بدل تعليم بقيمة {amount:,.2f} درهم يتجاوز السقف السنوي المسموح به (45,000 درهم) بمقدار {excess:,.2f} درهم.",
                        f"amount=AED {amount:.2f}; policy_ceiling=AED 45000.00; excess=AED {excess:.2f}",
                        "Adjust claimed disbursement down to the AED 45,000 policy maximum.",
                        "تعديل مبلغ الصرف إلى الحد الأقصى المسموح به وفق السياسة (45,000 درهم)."
                    ))
                    finding_counter += 1

            # -------------------------------------------------------------
            # Rule 12: POL-ALLOW-002 (Grade Housing Allowance Ceilings)
            # -------------------------------------------------------------
            if t_type == "Housing Allowance":
                h_cap = 4500 if emp_grade <= 5 else (9500 if emp_grade <= 8 else (16000 if emp_grade <= 11 else 25000))
                if amount > h_cap:
                    excess = amount - h_cap
                    findings.append(self._create_finding(
                        finding_counter, t_id, e_id, "POL-ALLOW-002", "HIGH",
                        f"Housing allowance claim of AED {amount:,.2f} exceeds Grade {emp_grade:02d} monthly entitlement cap of AED {h_cap:,.2f} by AED {excess:,.2f}.",
                        f"طلب بدل سكن بقيمة {amount:,.2f} درهم يتجاوز سقف الاستحقاق الشهري للدرجة {emp_grade:02d} (AED {h_cap:,.2f}) بمقدار {excess:,.2f} درهم.",
                        f"employee_grade={emp_grade}; housing_cap=AED {h_cap:.2f}; amount=AED {amount:.2f}; excess=AED {excess:.2f}",
                        "Cap housing allowance at the grade ceiling; notify employee and payroll processing desk.",
                        "تعديل بدل السكن إلى سقف الدرجة الوظيفية المعتمد، وإخطار الموظف ومكتب الرواتب بالتحديث."
                    ))
                    finding_counter += 1

            # -------------------------------------------------------------
            # Rule 13: POL-SAL-001 (Off-Cycle Salary Increment Cap 15%)
            # -------------------------------------------------------------
            if t_type == "Salary Adjustment" and base_sal > 0 and amount > 0:
                hike_ratio = amount / base_sal
                if hike_ratio > 0.15 and "Promotion_Committee_Approval" not in docs:
                    findings.append(self._create_finding(
                        finding_counter, t_id, e_id, "POL-SAL-001", "CRITICAL",
                        f"Off-cycle salary adjustment of AED {amount:,.2f} represents a {hike_ratio*100:.1f}% increase over base salary (AED {base_sal:,.2f}), exceeding the 15% threshold without Promotion Committee signoff.",
                        f"تعديل الراتب الاستثنائي بقيمة {amount:,.2f} درهم يمثل زيادة قدرها {hike_ratio*100:.1f}% من الراتب الأساسي، متجاوزاً سقف الـ 15% دون موافقة لجنة الترقيات.",
                        f"base_salary=AED {base_sal:.2f}; increment=AED {amount:.2f}; percentage={hike_ratio*100:.1f}%; max_allowed=15.0%",
                        "Cap increment at 15% pending formal evaluation and sign-off by Group Remuneration Committee.",
                        "تحديد نسبة الزيادة بـ 15% كحد أقصى لحين استكمال العرض على لجنة المكافآت والترقيات بالمجموعة."
                    ))
                    finding_counter += 1

            # -------------------------------------------------------------
            # Rule 14: POL-DUP-001 (Duplicate Allowance Claim Prevention)
            # -------------------------------------------------------------
            if amount > 0 and t_type in ["Discretionary Allowance", "Education Allowance", "Housing Allowance"]:
                prior_claims = emp_history.get(e_id, [])
                for (prev_date, prev_type, prev_amt, prev_id) in prior_claims:
                    if prev_type == t_type and abs((sub_date - prev_date).days) <= 30:
                        findings.append(self._create_finding(
                            finding_counter, t_id, e_id, "POL-DUP-001", "CRITICAL",
                            f"Duplicate {t_type} claim of AED {amount:,.2f} submitted within {(sub_date - prev_date).days} days of prior claim ({prev_id} for AED {prev_amt:,.2f}).",
                            f"طلب مكرر لـ {t_type} بقيمة {amount:,.2f} درهم مقدم خلال {(sub_date - prev_date).days} يوماً من طلب سابق ({prev_id} بقيمة {prev_amt:,.2f} درهم).",
                            f"transaction_id={t_id}; previous_transaction_id={prev_id}; type={t_type}; current_amt=AED {amount:.2f}; prior_amt=AED {prev_amt:.2f}; days_between={(sub_date - prev_date).days}",
                            "Void duplicate submission immediately; audit prior payment status to prevent double disbursement.",
                            "إلغاء المعاملة المكررة فوراً، وتدقيق سجل الصرف السابق لمنع ازدواجية الدفع."
                        ))
                        finding_counter += 1
                        break
                # Record in history
                if e_id not in emp_history:
                    emp_history[e_id] = []
                emp_history[e_id].append((sub_date, t_type, amount, t_id))

            # -------------------------------------------------------------
            # Rule 15: POL-LEAVE-001 (Annual Leave Overdraft Ceiling)
            # -------------------------------------------------------------
            if t_type == "Annual Leave" and duration > (accrued_leave + 5):
                overdraft = duration - (accrued_leave + 5)
                findings.append(self._create_finding(
                    finding_counter, t_id, e_id, "POL-LEAVE-001", "LOW",
                    f"Annual leave request of {duration} days exceeds available accrued balance ({accrued_leave} days) plus 5-day allowable emergency overdraft by {overdraft} days.",
                    f"طلب الإجازة السنوية البالغ {duration} يوماً يتجاوز الرصيد المستحق ({accrued_leave} يوماً) وسلفة الإجازة المسموحة (5 أيام) بمقدار {overdraft} يوماً.",
                    f"requested_days={duration}; accrued_balance={accrued_leave}; max_overdraft=5; excess={overdraft}",
                    "Reduce approved leave duration to available accrued balance plus 5 days, or convert remaining surplus to unpaid leave.",
                    "تعديل مدة الإجازة المعتمدة إلى الرصيد المتاح بالإضافة لـ 5 أيام، أو احتساب الفائض كإجازة غير مدفوعة الأجر."
                ))
                finding_counter += 1

            # -------------------------------------------------------------
            # Rule 16: POL-PROB-001 (Probationary Period Mobility & Increment)
            # -------------------------------------------------------------
            if tenure_m < 6.0 and t_type in ["Salary Adjustment", "Discretionary Allowance", "Transfer"]:
                findings.append(self._create_finding(
                    finding_counter, t_id, e_id, "POL-PROB-001", "HIGH",
                    f"Transaction type '{t_type}' submitted during employee's {tenure_m:.1f}-month probationary period. Policy restricts discretionary increases and lateral transfers during probation.",
                    f"معاملة من نوع '{t_type}' مقدمة خلال فترة التجربة للموظف ({tenure_m:.1f} شهراً). تحظر السياسة النقل أو الزيادات الاستثنائية خلال فترة الاختبار.",
                    f"tenure_months={tenure_m:.1f}; probation_limit=6.0; transaction_type={t_type}",
                    "Defer transaction until successful completion and confirmation of the 6-month probationary review.",
                    "تأجيل المعاملة لحين اجتياز وتثبيت الموظف رسمياً بعد انقضاء فترة التجربة المقررة (6 أشهر)."
                ))
                finding_counter += 1

            # -------------------------------------------------------------
            # Rule 17: POL-SEC-001 (Airside Security Clearance Compliance)
            # -------------------------------------------------------------
            if dept in ["Airport Operations", "Cargo & Logistics", "Engineering & Maintenance"] and t_type in ["Transfer", "Hire"] and "Airside_Security_Pass" not in docs:
                findings.append(self._create_finding(
                    finding_counter, t_id, e_id, "POL-SEC-001", "CRITICAL",
                    f"Operational transfer/hire in {dept} is missing verified Dubai Airports Airside Security Pass. Mandatory regulatory airside access verification required.",
                    f"معاملة تعيين/نقل تشغيلي في {dept} تفتقر إلى تصريح الدخول الأمني لساحة المطار (Airside Pass) الصادر من مطارات دبي والجهات الأمنية.",
                    f"department={dept}; transaction_type={t_type}; missing_credential=Airside_Security_Pass",
                    "Suspend airside operational roster access until security vetting is confirmed and physical pass is issued.",
                    "تعليق إدراج الموظف في الجداول التشغيلية لساحة المطار لحين استكمال الفحص الأمني وإصدار التصريح."
                ))
                finding_counter += 1

            # -------------------------------------------------------------
            # Rule 18: POL-REL-001 (Conflict of Interest & Relative Approval)
            # -------------------------------------------------------------
            if rel_id and app_id == rel_id:
                findings.append(self._create_finding(
                    finding_counter, t_id, e_id, "POL-REL-001", "CRITICAL",
                    f"Transaction authorized by {txn.get('approver_name')} ({app_id}), who is recorded in HR master data as a declared relative/household member of beneficiary {e_id}.",
                    f"تم اعتماد المعاملة من قبل {txn.get('approver_name')} ({app_id})، المسجل رسمياً كقريب/أحد أفراد عائلة الموظف المستفيد {e_id}، مما يشكل تضارب مصالح.",
                    f"employee_id={e_id}; approver_id={app_id}; declared_relative_id={rel_id}; conflict_type=NEPOTISM",
                    "Cancel approval signature immediately; transfer transaction to an independent HR Governance Officer.",
                    "إلغاء الاعتماد فوراً، وتكليف مسؤول حوكمة موارد بشرية محايد للبت في المعاملة وفق الأصول."
                ))
                finding_counter += 1

        df_findings = pd.DataFrame(findings)
        return df_findings

    def _create_finding(self, count, t_id, e_id, r_id, sev, expl_en, expl_ar, evidence, action_en, action_ar):
        r_def = RULE_DEFINITIONS.get(r_id, {
            "name": "Custom HR Compliance Policy Rule",
            "category": "Operational Policy",
            "owner": "HR Compliance Lead"
        })
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        return {
            "finding_id": f"FND-2026-{count:05d}",
            "transaction_id": t_id,
            "employee_id": e_id,
            "rule_id": r_id,
            "rule_name": r_def["name"],
            "violation_category": r_def["category"],
            "severity": sev,
            "plain_language_explanation": expl_en,
            "plain_language_explanation_ar": expl_ar,
            "cited_evidence": evidence,
            "assigned_owner": r_def["owner"],
            "suggested_corrective_action": action_en,
            "suggested_corrective_action_ar": action_ar,
            "audit_status": "FLAGGED_FOR_REVIEW",
            "detection_timestamp": now_iso
        }

if __name__ == "__main__":
    print("Testing ComplianceRuleEngine on data/transactions.csv...")
    df_emps = pd.read_csv("data/employees.csv")
    df_txns = pd.read_csv("data/transactions.csv")
    
    engine = ComplianceRuleEngine(df_emps)
    df_res = engine.evaluate_batch(df_txns)
    
    print(f"Total transactions audited: {len(df_txns)}")
    print(f"Total exceptions flagged: {len(df_res)}")
    print("\nBreakdown by severity:")
    print(df_res["severity"].value_counts())
    print("\nBreakdown by rule:")
    print(df_res["rule_id"].value_counts())
    
    # Export official output matching finding_format.csv
    # The submission requires: finding_id, transaction_id, employee_id, rule_id, rule_name, violation_category, severity, plain_language_explanation, cited_evidence, assigned_owner, suggested_corrective_action, audit_status, detection_timestamp
    submission_cols = [
        "finding_id", "transaction_id", "employee_id", "rule_id", "rule_name", 
        "violation_category", "severity", "plain_language_explanation", 
        "cited_evidence", "assigned_owner", "suggested_corrective_action", 
        "audit_status", "detection_timestamp"
    ]
    df_res[submission_cols].to_csv("audit_findings_output.csv", index=False)
    print("\nExported audit_findings_output.csv successfully!")
