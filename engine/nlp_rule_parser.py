"""
Emirates Group HR Natural Language Rule Engine (No-Code Rule Studio)
Parses human-written English policy rules into executable AST conditions,
validates syntax, tests impact against transaction batches, and registers active rules.
"""

import re
import datetime
import pandas as pd

class NLPRuleParser:
    def __init__(self):
        # Known taxonomy maps
        self.type_synonyms = {
            "housing": "Housing Allowance",
            "housing allowance": "Housing Allowance",
            "education": "Education Allowance",
            "tuition": "Education Allowance",
            "school": "Education Allowance",
            "salary": "Salary Adjustment",
            "increment": "Salary Adjustment",
            "pay": "Salary Adjustment",
            "sick": "Sick Leave",
            "sick leave": "Sick Leave",
            "annual leave": "Annual Leave",
            "vacation": "Annual Leave",
            "holiday": "Annual Leave",
            "transfer": "Transfer",
            "relocation": "Transfer",
            "exit": "Exit",
            "resignation": "Exit",
            "allowance": "Discretionary Allowance"
        }
        
        self.dept_synonyms = {
            "flight operations": "Flight Operations",
            "pilots": "Flight Operations",
            "cabin crew": "Cabin Crew",
            "engineering": "Engineering & Maintenance",
            "maintenance": "Engineering & Maintenance",
            "airport operations": "Airport Operations",
            "ground services": "Airport Operations",
            "cargo": "Cargo & Logistics",
            "catering": "Catering Services",
            "it": "Group IT & Digital",
            "hr": "Human Resources",
            "finance": "Finance & Procurement",
            "commercial": "Commercial Operations"
        }

    def parse_rule(self, natural_text: str, rule_id=None, rule_name=None, severity="HIGH", owner="HR Compliance Analyst"):
        """
        Parses plain English rule into executable lambda condition and metadata.
        Example inputs:
        - "Flag any housing allowance exceeding 12000 AED for Grade 6 or below"
        - "Flag sick leave exceeding 3 days missing Medical_Certificate"
        - "Flag transactions where amount is greater than 35000 in Flight Operations"
        - "Flag salary adjustment exceeding 20000 AED approved by Grade 8"
        """
        text_lower = natural_text.lower().strip()
        
        extracted = {
            "raw_text": natural_text,
            "rule_id": rule_id or f"POL-CUSTOM-{hash(natural_text) % 10000:04d}",
            "rule_name": rule_name or f"Custom Policy: {natural_text[:40]}...",
            "severity": severity,
            "owner": owner,
            "target_type": None,
            "target_dept": None,
            "amount_operator": None,
            "amount_threshold": None,
            "grade_operator": None,
            "grade_threshold": None,
            "duration_operator": None,
            "duration_threshold": None,
            "missing_doc": None
        }
        
        # 1. Detect transaction type
        for key, val in self.type_synonyms.items():
            if re.search(r'\b' + re.escape(key) + r'\b', text_lower):
                extracted["target_type"] = val
                break
                
        # 2. Detect department
        for key, val in self.dept_synonyms.items():
            if re.search(r'\b' + re.escape(key) + r'\b', text_lower):
                extracted["target_dept"] = val
                break
                
        # 3. Detect amount threshold (e.g. "exceeding 12000 AED", "greater than 25,000", "> 15000")
        amt_match = re.search(r'(?:exceeding|greater than|more than|above|>|over)\s*(?:aed|\$)?\s*([0-9,]+)', text_lower)
        if amt_match:
            extracted["amount_operator"] = ">"
            extracted["amount_threshold"] = float(amt_match.group(1).replace(",", ""))
            
        # 4. Detect grade threshold (e.g. "grade 6 or below", "grade <= 7", "grade under 8")
        grade_below = re.search(r'grade\s*(?:of\s*)?([0-9]+)\s*(?:or below|and below|or lower)', text_lower)
        if grade_below:
            extracted["grade_operator"] = "<="
            extracted["grade_threshold"] = int(grade_below.group(1))
        else:
            grade_above = re.search(r'grade\s*(?:of\s*)?([0-9]+)\s*(?:or above|and above|or higher)', text_lower)
            if grade_above:
                extracted["grade_operator"] = ">="
                extracted["grade_threshold"] = int(grade_above.group(1))
            else:
                grade_exact = re.search(r'grade\s*([0-9]+)', text_lower)
                if grade_exact:
                    extracted["grade_operator"] = "=="
                    extracted["grade_threshold"] = int(grade_exact.group(1))
                    
        # 5. Detect duration threshold (e.g. "exceeding 3 days", "greater than 5 days")
        dur_match = re.search(r'(?:exceeding|greater than|more than|above|>)\s*([0-9]+)\s*days?', text_lower)
        if dur_match:
            extracted["duration_operator"] = ">"
            extracted["duration_threshold"] = int(dur_match.group(1))

        # 6. Detect missing document (e.g. "missing Medical_Certificate", "without Ejari")
        doc_match = re.search(r'(?:missing|without|no)\s*([a-zA-Z0-9_]+(?:_[a-zA-Z0-9_]+)?)', text_lower)
        if doc_match:
            extracted["missing_doc"] = doc_match.group(1)

        # Build executable filter function
        def evaluate_row(row):
            # Check transaction type if specified
            if extracted["target_type"]:
                if row.get("transaction_type") != extracted["target_type"]:
                    return False
            # Check department if specified
            if extracted["target_dept"]:
                if row.get("department") != extracted["target_dept"]:
                    return False
            # Check amount threshold
            if extracted["amount_operator"] == ">":
                row_amt = float(row.get("amount_aed", 0) or 0)
                if row_amt <= extracted["amount_threshold"]:
                    return False
            # Check grade threshold
            if extracted["grade_operator"]:
                row_grade = int(row.get("grade", 0) or 0)
                if extracted["grade_operator"] == "<=" and row_grade > extracted["grade_threshold"]:
                    return False
                elif extracted["grade_operator"] == ">=" and row_grade < extracted["grade_threshold"]:
                    return False
                elif extracted["grade_operator"] == "==" and row_grade != extracted["grade_threshold"]:
                    return False
            # Check duration threshold
            if extracted["duration_operator"] == ">":
                row_dur = int(row.get("duration_days", 0) or 0)
                if row_dur <= extracted["duration_threshold"]:
                    return False
            # Check missing document
            if extracted["missing_doc"]:
                docs = str(row.get("documents_attached", "")).lower()
                if extracted["missing_doc"].lower() in docs:
                    return False
            return True

        extracted["compiled_func"] = evaluate_row
        return extracted

    def test_rule(self, parsed_rule, df_transactions):
        """Runs the compiled rule against a transaction DataFrame and returns matches."""
        matches = []
        for _, row in df_transactions.iterrows():
            if parsed_rule["compiled_func"](row):
                matches.append(row.to_dict())
        return pd.DataFrame(matches)

if __name__ == "__main__":
    parser = NLPRuleParser()
    test_query = "Flag any housing allowance exceeding 12000 AED for Grade 6 or below"
    parsed = parser.parse_rule(test_query)
    print("Parsed Rule Metadata:")
    for k, v in parsed.items():
        if k != "compiled_func":
            print(f"  {k}: {v}")
            
    df_txns = pd.read_csv("data/transactions.csv")
    df_matches = parser.test_rule(parsed, df_txns)
    print(f"\nRule matched {len(df_matches)} transactions in 10,000 dataset.")
    if len(df_matches) > 0:
        print("Sample match:")
        print(df_matches[["transaction_id", "employee_name", "grade", "transaction_type", "amount_aed"]].head(3))
