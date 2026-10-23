"""
Emirates Group HR Unsupervised Anomaly & Pattern Detector
Identifies emergent behavioral anomalies, out-of-band velocities, and statistical outliers
that no written rule currently covers. Powered by scikit-learn Isolation Forest & Z-Score clustering.
"""

import datetime
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

class HRAnomalyDetector:
    def __init__(self, contamination=0.015):
        self.contamination = contamination
        self.model = IsolationForest(
            contamination=contamination, 
            random_state=42, 
            n_estimators=100
        )
        self.scaler = StandardScaler()

    def detect_anomalies(self, df_transactions):
        """
        Runs unsupervised multi-dimensional anomaly detection and pattern mining.
        Returns a DataFrame of detected anomalies with pattern tags and plain-language descriptions.
        """
        df = df_transactions.copy()
        
        # 1. Feature Engineering for ML
        df["sub_dt"] = pd.to_datetime(df["submission_date"])
        df["eff_dt"] = pd.to_datetime(df["effective_date"])
        df["day_of_week"] = df["sub_dt"].dt.dayofweek
        df["is_weekend"] = df["day_of_week"].isin([4, 5, 6]).astype(int) # Fri, Sat, Sun
        
        df["amount_clean"] = pd.to_numeric(df["amount_aed"], errors="coerce").fillna(0)
        df["salary_clean"] = pd.to_numeric(df["base_salary_aed"], errors="coerce").fillna(10000)
        df["tenure_clean"] = pd.to_numeric(df["tenure_months"], errors="coerce").fillna(12)
        df["duration_clean"] = pd.to_numeric(df["duration_days"], errors="coerce").fillna(0)
        df["grade_clean"] = pd.to_numeric(df["grade"], errors="coerce").fillna(5)
        
        df["amount_to_salary"] = df["amount_clean"] / (df["salary_clean"] + 1)
        
        # 2. Approver Velocity (Number of approvals by same approver within 7 days)
        approver_counts = df.groupby(["approver_id", pd.Grouper(key="sub_dt", freq="7D")])["transaction_id"].transform("count")
        df["approver_7d_velocity"] = approver_counts.fillna(1)
        
        # 3. Beneficiary Velocity (Number of requests for same employee within 30 days)
        beneficiary_counts = df.groupby(["employee_id", pd.Grouper(key="sub_dt", freq="30D")])["transaction_id"].transform("count")
        df["beneficiary_30d_velocity"] = beneficiary_counts.fillna(1)

        # 4. Department Z-Score for Financial Amounts
        dept_means = df.groupby("department")["amount_clean"].transform("mean")
        dept_stds = df.groupby("department")["amount_clean"].transform("std").replace(0, 1)
        df["dept_amount_zscore"] = (df["amount_clean"] - dept_means) / dept_stds

        # Feature matrix for Isolation Forest
        feature_cols = [
            "amount_clean", "amount_to_salary", "tenure_clean", 
            "duration_clean", "grade_clean", "approver_7d_velocity", 
            "beneficiary_30d_velocity", "dept_amount_zscore", "is_weekend"
        ]
        
        X = df[feature_cols].fillna(0)
        X_scaled = self.scaler.fit_transform(X)
        
        # Fit Isolation Forest
        self.model.fit(X_scaled)
        df["anomaly_score"] = self.model.decision_function(X_scaled)
        df["is_anomaly"] = self.model.predict(X_scaled) == -1
        
        # 5. Extract and classify anomaly patterns
        anomalies = []
        anomaly_counter = 1
        
        anomaly_subset = df[df["is_anomaly"]].copy()
        # Sort by most severe anomaly score (lowest decision function value)
        anomaly_subset = anomaly_subset.sort_values(by="anomaly_score")
        
        for _, row in anomaly_subset.iterrows():
            t_id = row["transaction_id"]
            e_id = row["employee_id"]
            emp_name = row["employee_name"]
            score = float(row["anomaly_score"])
            zscore = float(row["dept_amount_zscore"])
            velocity = int(row["approver_7d_velocity"])
            ben_velocity = int(row["beneficiary_30d_velocity"])
            amt = float(row["amount_clean"])
            dept = row["department"]
            app_name = row["approver_name"]
            app_id = row["approver_id"]
            
            # Pattern classification
            pattern_type = "Multi-variate Behavioral Outlier"
            explanation_en = ""
            explanation_ar = ""
            severity = "MEDIUM"
            suggested_action = "Conduct exploratory audit inquiry into workflow pattern."
            suggested_action_ar = "إجراء تحقيق تدقيقي استكشافي في نمط سير العمل غير المعتاد."
            
            if velocity >= 12:
                pattern_type = "High-Velocity Approver Clustering"
                severity = "HIGH"
                explanation_en = f"Approver {app_name} ({app_id}) approved {velocity} transactions in a 7-day period. This rapid approval velocity indicates potential rubber-stamping or automated script bypass."
                explanation_ar = f"قام المفوض {app_name} ({app_id}) باعتماد {velocity} معاملة خلال 7 أيام، مما يشير إلى اعتماد متسرع أو تجاوز آلي لنقاط المراجعة."
                suggested_action = "Review approver queue logs to confirm due diligence and substantive review time per transaction."
                suggested_action_ar = "مراجعة سجلات وقت التدقيق للتأكد من ممارسة العناية الواجبة قبل منح الاعتماد."

            elif ben_velocity >= 4:
                pattern_type = "Beneficiary Transaction Burst"
                severity = "HIGH"
                explanation_en = f"Employee {emp_name} ({e_id}) received {ben_velocity} distinct HR transactions within a 30-day window, representing an abnormal frequency spike."
                explanation_ar = f"سجل الموظف {emp_name} ({e_id}) عدد {ben_velocity} معاملات مختلفة خلال 30 يوماً، وهو ما يمثل تكراراً تصاعدياً غير معتاد."
                suggested_action = "Consolidate multiple transactions to audit for fragmented claims or uncoordinated compensation changes."
                suggested_action_ar = "دمج وتدقيق المعاملات المتعددة للتأكد من عدم تجزئة المطالبات لتفادي سقوف الاعتماد."

            elif zscore >= 3.0:
                pattern_type = "Departmental Financial Outlier"
                severity = "HIGH"
                explanation_en = f"Transaction amount of AED {amt:,.2f} in {dept} is {zscore:.1f} standard deviations above departmental baseline average."
                explanation_ar = f"قيمة المعاملة ({amt:,.2f} درهم) في قسم {dept} تفوق المتوسط المعتاد للدائرة بـ {zscore:.1f} انحرافات معيارية."
                suggested_action = "Verify business rationale with Head of Department for disproportionate departmental allocation."
                suggested_action_ar = "طلب إيضاح من رئيس الدائرة لتبرير التخصيص المالي الاستثنائي مقارنة بزملاء القسم."

            elif row["is_weekend"] == 1 and amt > 20000:
                pattern_type = "Off-Hours Weekend High-Value Submission"
                severity = "MEDIUM"
                explanation_en = f"High-value transaction of AED {amt:,.2f} was submitted during weekend off-hours ({row['submission_date']}), outside standard business operating rhythm."
                explanation_ar = f"معاملة ذات قيمة عالية ({amt:,.2f} درهم) قُدمت خلال عطلة نهاية الأسبوع وخارج أوقات العمل الرسمية."
                suggested_action = "Confirm transmission origin and line management awareness of out-of-band weekend filing."
                suggested_action_ar = "التأكد من مصدر المعاملة وإحاطة الإدارة المباشرة بتقديم الطلب في عطلة نهاية الأسبوع."

            else:
                pattern_type = "Multi-variate Statistical Outlier"
                severity = "MEDIUM"
                explanation_en = f"Isolation Forest identified complex correlation anomaly (score: {score:.3f}) across amount (AED {amt:,.2f}), employee tenure ({row['tenure_clean']:.1f} mo), and approval hierarchy."
                explanation_ar = f"تم رصد شذوذ إحصائي مركب (درجة العزل: {score:.3f}) يجمع بين قيمة المعاملة ومدة خدمة الموظف ورتبة الاعتماد."
                suggested_action = "Perform random sampling audit to assess whether this pattern reflects emerging business workflow shifts."
                suggested_action_ar = "إجراء فحص عشوائي للتأكد مما إذا كان النمط يعكس تغيراً تشغيلياً مشروعاً أو ثغرة إجراءات."

            anomalies.append({
                "anomaly_id": f"ANM-2026-{anomaly_counter:04d}",
                "transaction_id": t_id,
                "employee_id": e_id,
                "employee_name": emp_name,
                "department": dept,
                "pattern_type": pattern_type,
                "anomaly_score": round(score, 4),
                "severity": severity,
                "amount_aed": amt,
                "plain_language_explanation": explanation_en,
                "plain_language_explanation_ar": explanation_ar,
                "suggested_action": suggested_action,
                "suggested_action_ar": suggested_action_ar,
                "detection_date": str(row["submission_date"])
            })
            anomaly_counter += 1
            
        return pd.DataFrame(anomalies)

if __name__ == "__main__":
    df_txns = pd.read_csv("data/transactions.csv")
    detector = HRAnomalyDetector(contamination=0.015)
    anomalies_df = detector.detect_anomalies(df_txns)
    print(f"Total unsupervised anomalies detected: {len(anomalies_df)}")
    print("\nPattern Types Breakdown:")
    print(anomalies_df["pattern_type"].value_counts())
    # Save with utf-8 encoding
    anomalies_df.to_csv("data/detected_anomalies.csv", index=False, encoding="utf-8")
    print(f"Sample Anomaly ID: {anomalies_df.iloc[0]['anomaly_id']} - {anomalies_df.iloc[0]['pattern_type']}")
    print("Saved data/detected_anomalies.csv successfully!")
