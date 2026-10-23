"""
Emirates Group HR Employee Experience & Procedural Fairness Module
Ensures transparent, dignified exception communication, structured employee appeal workflows,
and adverse-impact fairness metrics across grades and business units.
"""

import pandas as pd
import numpy as np

class EmployeeFairnessManager:
    def __init__(self, findings_df=None, employees_df=None):
        self.findings_df = findings_df
        self.employees_df = employees_df
        
    def generate_fair_notice(self, finding_row, employee_row):
        """
        Generates empathetic, non-punitive notification in English and Arabic.
        Emphasizes collaborative resolution, guidance, and right to appeal.
        """
        emp_name = employee_row.get("full_name", "Valued Colleague")
        rule_name = finding_row.get("rule_name", "Policy Guideline")
        t_id = finding_row.get("transaction_id", "HR-TXN")
        t_type = finding_row.get("violation_category", "HR Transaction")
        action = finding_row.get("suggested_corrective_action", "")
        
        notice_en = f"""Dear {emp_name},

We are writing to share a brief update regarding your recent {t_type} ({t_id}).

During our automated continuous compliance verification, our system flagged an item related to "{rule_name}" that requires a quick verification to ensure complete alignment with Emirates Group standards.

What this means for you:
This is a standard administrative verification and does NOT affect your employment standing or performance record. Our priority is ensuring that all documentation is accurate, complete, and protects your entitlements.

Recommended Next Step:
{action}

Your Rights & Support:
- You have 5 business days to upload requested documentation or provide context.
- If you believe this notice was triggered in error or have extenuating circumstances, you can submit an instant 1-click appeal or reach out to your HR Business Partner.
- No payroll adjustments will take place without prior consultation.

Thank you for your partnership in keeping Emirates Group compliant, transparent, and fair."""

        notice_ar = f"""عزيزنا الزميل / {emp_name}،

نود إحاطتكم علماً بمستجدات معاملتكم الإدارية الأخيرة ({t_id}).

خلال إجراءات التحقق والتدقيق المستمر، رصد النظام نقطة تتطلب استيضاحاً إدارياً بسيطاً فيما يخص "{rule_name}"، وذلك لضمان استيفاء المعايير المؤسسية لمجموعة طيران الإمارات.

ماذا يعني هذا بالنسبة لك:
هذا الإجراء هو تدقيق إداري دوري روتيني ولا يؤثر بأي شكل من الأشكال على سجلكم الوظيفي أو تقييم أدائكم. هدفنا الأساسي هو ضمان دقة الوثائق وحماية كامل استحقاقاتكم الوظيفية.

الخطوة التالية المطلوبة:
{finding_row.get('suggested_corrective_action_ar', action)}

حقوقكم والدعم المتاح:
- لديكم مهلة 5 أيام عمل لإرفاق الوثائق المطلوبة أو تقديم توضيح.
- في حال كان لديكم أي استفسار أو رغبة في تقديم تظلم، يمكنكم الضغط على زر التظلم الفوري أو التواصل مع شريك أعمال الموارد البشرية.
- لن يتم تطبيق أي تسوية مالية قبل استكمال التواصل معكم.

شاكرين لكم حسن تعاونكم في ترسيخ قيم الشفافية والعدالة بمجموعة طيران الإمارات."""

        return {
            "notice_en": notice_en,
            "notice_ar": notice_ar,
            "appeal_allowed": True,
            "appeal_sla_days": 5
        }

    def compute_fairness_analytics(self, df_txns, df_findings):
        """
        Calculates adverse impact ratio (AIR) across departments and grades
        to verify that compliance checking is procedurally fair and does not
        disproportionately impact any single workforce cohort.
        """
        merged = df_txns.copy()
        flagged_txns = set(df_findings["transaction_id"].unique())
        merged["is_flagged"] = merged["transaction_id"].isin(flagged_txns)
        
        # Flag rate by department
        dept_stats = merged.groupby("department").agg(
            total_txns=("transaction_id", "count"),
            flagged_txns=("is_flagged", "sum")
        ).reset_index()
        dept_stats["flag_rate_pct"] = round((dept_stats["flagged_txns"] / dept_stats["total_txns"]) * 100, 2)
        
        # Flag rate by Grade band (Junior 1-5, Mid 6-8, Senior 9-11, Exec 12+)
        def grade_band(g):
            if g <= 5: return "Frontline / Junior (Gr 1-5)"
            elif g <= 8: return "Mid-Level / Specialist (Gr 6-8)"
            elif g <= 11: return "Senior Leadership (Gr 9-11)"
            else: return "Executive Directorate (Gr 12+)"
            
        merged["grade_band"] = merged["grade"].apply(grade_band)
        band_stats = merged.groupby("grade_band").agg(
            total_txns=("transaction_id", "count"),
            flagged_txns=("is_flagged", "sum")
        ).reset_index()
        band_stats["flag_rate_pct"] = round((band_stats["flagged_txns"] / band_stats["total_txns"]) * 100, 2)
        
        # Calculate Disparate Impact Ratio against baseline average
        overall_rate = merged["is_flagged"].mean()
        dept_stats["disparate_impact_ratio"] = round(dept_stats["flag_rate_pct"] / (overall_rate * 100), 2)
        
        return {
            "overall_audit_rate": round(overall_rate * 100, 2),
            "department_fairness": dept_stats.to_dict(orient="records"),
            "grade_fairness": band_stats.to_dict(orient="records")
        }

if __name__ == "__main__":
    df_txns = pd.read_csv("data/transactions.csv")
    df_fnds = pd.read_csv("audit_findings_output.csv")
    df_emps = pd.read_csv("data/employees.csv")
    
    mgr = EmployeeFairnessManager(df_fnds, df_emps)
    analytics = mgr.compute_fairness_analytics(df_txns, df_fnds)
    print("Fairness Analytics Computed:")
    print(f"Overall exception rate: {analytics['overall_audit_rate']}%")
    print("Grade Band Fairness Distribution:")
    for gb in analytics["grade_fairness"]:
        print(f"  {gb['grade_band']}: {gb['flag_rate_pct']}% ({gb['flagged_txns']}/{gb['total_txns']})")
