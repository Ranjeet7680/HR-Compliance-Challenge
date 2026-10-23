"""
Emirates Group HR Synthetic Data Pack Generator (Optimized)
Generates 2,000 employee master records and 10,000 HR transactions spanning 12 months.
Injects realistic planted policy violations across 18 rules with ground-truth labels.
"""

import os
import random
import datetime
import pandas as pd
import numpy as np

RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

FIRST_NAMES = [
    "Mohammed", "Ahmed", "Rashid", "Sultan", "Saeed", "Hamad", "Omar", "Khalid", "Fatima", "Mariam", 
    "Shamsa", "Alia", "Noora", "Hessa", "Zayed", "Tariq", "Mansoor", "Layla", "Yousef", "Sara",
    "James", "Oliver", "David", "Emma", "Charlotte", "Sophie", "Liam", "William", "Benjamin", "Lucas",
    "Rahul", "Priya", "Arjun", "Ananya", "Vikram", "Sneha", "Rohan", "Sunita", "Deepak", "Kavita",
    "John", "Michael", "Maria", "Grace", "Mark", "Angelo", "Christine", "Paulo", "Rhea", "Jerome",
    "Liam", "Declan", "Sean", "Connor", "Fiona", "Siobhan", "Callum", "Kirsty", "Graeme", "Niel",
    "Jean-Pierre", "Claire", "Antoine", "Camille", "Etienne", "Margaux", "Matthias", "Sabine", "Stefan"
]

LAST_NAMES = [
    "Al Maktoum", "Al Falasi", "Al Nuaimi", "Al Marzooqi", "Al Kaabi", "Al Zaabi", "Al Suwaidi", 
    "Al Shamsi", "Al Mansoori", "Al Mazrouei", "Al Blooshi", "Al Hammadi", "Al Dhaheri", "Al Hashimi",
    "Smith", "Johnson", "Williams", "Taylor", "Brown", "Davies", "Evans", "Wilson", "Thomas", "Roberts",
    "Sharma", "Patel", "Verma", "Rao", "Nair", "Menon", "Reddy", "Kulkarni", "Gupta", "Kapoor",
    "Santos", "Reyes", "Cruz", "Bautista", "Ocampo", "Garcia", "Mendoza", "Torres", "Aquino", "Del Rosario",
    "Van der Merwe", "Botha", "Du Plessis", "Fourie", "Pretorius", "Coetzee", "Venter", "Nel", "Swanepoel"
]

DEPARTMENTS = [
    ("Flight Operations", "Emirates Airline"),
    ("Cabin Crew", "Emirates Airline"),
    ("Engineering & Maintenance", "Emirates Airline"),
    ("Airport Operations", "dnata"),
    ("Cargo & Logistics", "dnata"),
    ("Catering Services", "Emirates Flight Catering"),
    ("Group IT & Digital", "Emirates Group Corporate"),
    ("Human Resources", "Emirates Group Corporate"),
    ("Finance & Procurement", "Emirates Group Corporate"),
    ("Commercial Operations", "Emirates Airline"),
    ("Security & Network Safety", "Emirates Group Corporate"),
    ("Customer Experience", "Emirates Airline")
]

LOCATIONS = [
    "Dubai International Airport (DXB)", "Dubai World Central (DWC)",
    "Emirates Group Headquarters (EGHQ)", "dnata Travel Centre",
    "Emirates Aviation College", "London Heathrow (LHR)",
    "Singapore Changi (SIN)", "Sydney Kingsford Smith (SYD)"
]

JOB_TITLES = {
    "Flight Operations": [("Captain A380", 11), ("First Officer B777", 8), ("Fleet Training Captain", 12), ("Flight Dispatcher", 6), ("Crew Roster Planner", 5)],
    "Cabin Crew": [("Cabin Crew Service Leader", 7), ("Senior Flight Steward", 5), ("Flight Stewardess", 4), ("Purser", 6), ("Cabin Service Director", 8)],
    "Engineering & Maintenance": [("Senior Avionics Engineer", 8), ("Licensed Aircraft Engineer", 7), ("Aircraft Maintenance Technician", 5), ("Base Maintenance VP", 11), ("Component Overhaul Lead", 7)],
    "Airport Operations": [("Airside Ramp Supervisor", 6), ("Baggage Operations Lead", 5), ("Passenger Service Agent", 3), ("Hub Operations Manager", 8), ("Turnaround Coordinator", 5)],
    "Cargo & Logistics": [("Cargo Loadmaster", 6), ("Freight Handling Specialist", 4), ("Dangerous Goods Inspector", 7), ("Cargo Operations Manager", 9)],
    "Catering Services": [("Executive Sous Chef", 8), ("Food Safety Officer", 6), ("Flight Catering Coordinator", 4), ("Production Manager", 8)],
    "Group IT & Digital": [("Cloud Enterprise Architect", 10), ("Senior DevOps Engineer", 8), ("Cybersecurity Specialist", 8), ("HR Systems Analyst", 6), ("VP Digital Transformation", 11)],
    "Human Resources": [("HR Business Partner", 8), ("Talent Acquisition Specialist", 6), ("Compensation & Benefits Lead", 8), ("Employee Relations Manager", 8), ("VP Group HR", 12)],
    "Finance & Procurement": [("Senior Financial Analyst", 7), ("Payroll Operations Lead", 8), ("Category Procurement Manager", 9), ("Audit Senior", 8), ("VP Group Finance", 12)],
    "Commercial Operations": [("Revenue Management Lead", 8), ("Commercial Account Manager", 7), ("Pricing Analyst", 6), ("Regional VP Commercial", 12)],
    "Security & Network Safety": [("Aviation Security Officer", 6), ("Airside Security Inspector", 7), ("Security Compliance Lead", 8)],
    "Customer Experience": [("First Class Lounge Lead", 6), ("Customer Relations Specialist", 5), ("VIP Hospitality Executive", 6)]
}

def generate_employees(num_employees=2000):
    employees = []
    
    # Executives (Grades 12-14)
    executives = []
    for i in range(1, 21):
        emp_id = f"EK-{i:05d}"
        fn = random.choice(FIRST_NAMES)
        ln = random.choice(LAST_NAMES)
        name = f"{fn} {ln}"
        dept_info = random.choice(DEPARTMENTS)
        grade = random.choice([12, 13, 14])
        salary = grade * 8500 + random.randint(15000, 35000)
        executives.append({
            "employee_id": emp_id,
            "full_name": name,
            "gender": random.choice(["Male", "Female"]),
            "grade": grade,
            "department": dept_info[0],
            "business_unit": dept_info[1],
            "job_title": "Executive Vice President" if grade >= 13 else "Senior Vice President",
            "location": "Emirates Group Headquarters (EGHQ)",
            "manager_id": "BOARD-001",
            "hire_date": (datetime.date(2010, 1, 1) + datetime.timedelta(days=random.randint(0, 3000))).isoformat(),
            "base_salary_aed": salary,
            "accrued_leave_days": random.randint(20, 45),
            "status": "ACTIVE"
        })
    employees.extend(executives)
    
    # Managers (Grades 8-11)
    managers = []
    for i in range(21, 251):
        emp_id = f"EK-{i:05d}"
        fn = random.choice(FIRST_NAMES)
        ln = random.choice(LAST_NAMES)
        name = f"{fn} {ln}"
        dept_info = random.choice(DEPARTMENTS)
        grade = random.choice([8, 9, 10, 11])
        exec_mgr = random.choice([e["employee_id"] for e in executives])
        salary = grade * 4500 + random.randint(8000, 18000)
        managers.append({
            "employee_id": emp_id,
            "full_name": name,
            "gender": random.choice(["Male", "Female"]),
            "grade": grade,
            "department": dept_info[0],
            "business_unit": dept_info[1],
            "job_title": "Vice President" if grade >= 10 else "Department Manager",
            "location": random.choice(LOCATIONS),
            "manager_id": exec_mgr,
            "hire_date": (datetime.date(2014, 1, 1) + datetime.timedelta(days=random.randint(0, 3200))).isoformat(),
            "base_salary_aed": salary,
            "accrued_leave_days": random.randint(15, 38),
            "status": "ACTIVE"
        })
    employees.extend(managers)
    
    # Staff (Grades 1-7)
    for i in range(251, num_employees + 1):
        emp_id = f"EK-{i:05d}"
        fn = random.choice(FIRST_NAMES)
        ln = random.choice(LAST_NAMES)
        name = f"{fn} {ln}"
        dept_info = random.choice(DEPARTMENTS)
        dept_name = dept_info[0]
        bu_name = dept_info[1]
        
        titles = JOB_TITLES.get(dept_name, [("Operations Specialist", 5)])
        title_tuple = random.choice(titles)
        job_title = title_tuple[0]
        grade = max(1, min(7, title_tuple[1] + random.randint(-1, 1)))
        
        dept_mgrs = [m["employee_id"] for m in managers if m["department"] == dept_name]
        manager_id = random.choice(dept_mgrs) if dept_mgrs else random.choice([m["employee_id"] for m in managers])
        
        salary = grade * 2800 + random.randint(3500, 7500)
        hire_date = datetime.date(2016, 1, 1) + datetime.timedelta(days=random.randint(0, 3600))
        
        employees.append({
            "employee_id": emp_id,
            "full_name": name,
            "gender": random.choice(["Male", "Female"]),
            "grade": grade,
            "department": dept_name,
            "business_unit": bu_name,
            "job_title": job_title,
            "location": random.choice(LOCATIONS),
            "manager_id": manager_id,
            "hire_date": hire_date.isoformat(),
            "base_salary_aed": salary,
            "accrued_leave_days": random.randint(5, 32),
            "status": "ACTIVE"
        })
        
    relatives_map = {}
    for _ in range(40):
        e1 = random.choice(employees)["employee_id"]
        e2 = random.choice(employees)["employee_id"]
        if e1 != e2:
            relatives_map[e1] = e2
            relatives_map[e2] = e1
            
    for emp in employees:
        emp["declared_relative_id"] = relatives_map.get(emp["employee_id"], "")
        
    return pd.DataFrame(employees)


def generate_transactions(df_employees, num_transactions=10000, start_date=datetime.date(2025, 11, 1), end_date=datetime.date(2026, 10, 23)):
    transactions = []
    total_days = (end_date - start_date).days
    
    emp_dict = {row["employee_id"]: row.to_dict() for _, row in df_employees.iterrows()}
    emp_ids = list(emp_dict.keys())
    
    # Precompute candidate pools for blazing fast lookup
    all_emps = list(emp_dict.values())
    mgrs_gr7_8 = [e for e in all_emps if e["grade"] in [7, 8]]
    mgrs_gr8_plus = [e for e in all_emps if e["grade"] >= 8]
    mgrs_gr10_plus = [e for e in all_emps if e["grade"] >= 10]
    mgrs_gr12_plus = [e for e in all_emps if e["grade"] >= 12]
    junior_emps_gr5_under = [e for e in all_emps if e["grade"] <= 5]
    flight_crew_emps = [e for e in all_emps if e["department"] in ["Flight Operations", "Cabin Crew"]]
    ops_clearance_emps = [e for e in all_emps if e["department"] in ["Airport Operations", "Cargo & Logistics", "Engineering & Maintenance"]]

    rules_list = [
        "POL-DOA-001", "POL-SOD-001", "POL-SOD-002", "POL-DOC-001", 
        "POL-DOC-002", "POL-DOC-003", "POL-DOC-004", "POL-TIM-001", 
        "POL-TIM-002", "POL-TIM-003", "POL-ALLOW-001", "POL-ALLOW-002", 
        "POL-SAL-001", "POL-DUP-001", "POL-LEAVE-001", "POL-PROB-001", 
        "POL-SEC-001", "POL-REL-001"
    ]
    
    num_violations = int(num_transactions * 0.11) # ~11% violations
    violation_indices = set(random.sample(range(num_transactions), num_violations))
    
    for idx in range(num_transactions):
        txn_id = f"TXN-2026-{idx+1:05d}"
        sub_date = start_date + datetime.timedelta(days=random.randint(0, total_days))
        
        emp_id = random.choice(emp_ids)
        emp = emp_dict[emp_id]
        
        is_violation = (idx in violation_indices)
        planted_rule = random.choice(rules_list) if is_violation else None
        
        txn_type = random.choice([
            "Salary Adjustment", "Housing Allowance", "Education Allowance", 
            "Discretionary Allowance", "Transfer", "Annual Leave", "Sick Leave", "Exit"
        ])
        
        eff_date = sub_date + datetime.timedelta(days=random.randint(1, 14))
        requester_id = emp["manager_id"] if emp["manager_id"] in emp_dict else "HR-SYSTEM"
        requester_name = emp_dict.get(requester_id, {}).get("full_name", "HR Operations Portal")
        
        approver_id = emp["manager_id"] if emp["manager_id"] in emp_dict else emp_id
        approver = emp_dict.get(approver_id, emp)
        approver_grade = approver["grade"]
        approver_name = approver["full_name"]
        
        amount_aed = 0
        duration_days = 0
        docs = ["Standard_HR_Form_V2"]
        resignation_type = "N/A"
        comments = "Routine automated HR workflow transaction"
        
        if planted_rule == "POL-DOA-001":
            txn_type = random.choice(["Salary Adjustment", "Discretionary Allowance", "Housing Allowance"])
            approver = random.choice(mgrs_gr7_8)
            approver_id = approver["employee_id"]
            approver_grade = approver["grade"]
            approver_name = approver["full_name"]
            amount_aed = random.randint(15000, 38000)
            docs = ["Standard_HR_Form_V2", "Manager_Justification"]
            comments = f"Special adjustment of AED {amount_aed} authorized by Grade {approver_grade} Manager"

        elif planted_rule == "POL-SOD-001":
            txn_type = random.choice(["Housing Allowance", "Discretionary Allowance", "Salary Adjustment", "Annual Leave"])
            requester_id = emp_id
            requester_name = emp["full_name"]
            approver_id = emp_id
            approver_grade = emp["grade"]
            approver_name = emp["full_name"]
            amount_aed = random.randint(3000, 15000) if txn_type != "Annual Leave" else 0
            duration_days = random.randint(5, 14) if txn_type == "Annual Leave" else 0
            docs = ["Self_Service_Request"]
            comments = "Self-submitted and self-authorized via portal bypass"

        elif planted_rule == "POL-SOD-002":
            emp = random.choice(mgrs_gr8_plus)
            emp_id = emp["employee_id"]
            approver = random.choice(junior_emps_gr5_under)
            approver_id = approver["employee_id"]
            approver_grade = approver["grade"]
            approver_name = approver["full_name"]
            txn_type = "Salary Adjustment"
            amount_aed = random.randint(4000, 12000)
            docs = ["Standard_HR_Form_V2"]
            comments = "Subordinate counter-signature on senior manager compensation"

        elif planted_rule == "POL-DOC-001":
            txn_type = "Sick Leave"
            duration_days = random.randint(3, 9)
            docs = ["Leave_Application_Form"]
            amount_aed = 0
            comments = f"Absence due to severe flu reported for {duration_days} consecutive days"

        elif planted_rule == "POL-DOC-002":
            txn_type = random.choice(["Education Allowance", "Family Dependent Allowance"])
            amount_aed = random.randint(18000, 35000)
            docs = ["School_Tuition_Invoice"]
            comments = "Tuition reimbursement request for newly registered dependent child"

        elif planted_rule == "POL-DOC-003":
            txn_type = "Exit"
            resignation_type = "Voluntary"
            docs = ["Exit_Interview_Survey"]
            comments = "Employee resignation submitted; clearance checklist pending"

        elif planted_rule == "POL-DOC-004":
            emp = random.choice(flight_crew_emps)
            emp_id = emp["employee_id"]
            txn_type = "Transfer"
            docs = ["Internal_Transfer_Form", "Fleet_Qualification_Doc"]
            comments = "Fleet type re-assignment to Airbus A380 operations"

        elif planted_rule == "POL-TIM-001":
            txn_type = random.choice(["Salary Adjustment", "Housing Allowance", "Discretionary Allowance"])
            amount_aed = random.randint(2500, 9000)
            backdate_days = random.randint(35, 120)
            eff_date = sub_date - datetime.timedelta(days=backdate_days)
            docs = ["Standard_HR_Form_V2"]
            comments = f"Adjustment retroactively effective from {eff_date.isoformat()} ({backdate_days} days backdated)"

        elif planted_rule == "POL-TIM-002":
            txn_type = "Transfer"
            eff_date = sub_date + datetime.timedelta(days=10)
            docs = ["Departmental_Transfer_Request"]
            comments = "Lateral transfer request with only 4 months tenure in current position"

        elif planted_rule == "POL-TIM-003":
            txn_type = "Exit"
            resignation_type = "Voluntary"
            short_notice = random.randint(3, 14)
            eff_date = sub_date + datetime.timedelta(days=short_notice)
            docs = ["Resignation_Letter", "Handover_Clearance"]
            comments = f"Immediate exit requested in {short_notice} days without contractual notice buyout"

        elif planted_rule == "POL-ALLOW-001":
            txn_type = "Education Allowance"
            if random.random() < 0.5:
                emp = random.choice(junior_emps_gr5_under)
                emp_id = emp["employee_id"]
                amount_aed = 32000
            else:
                amount_aed = random.randint(48000, 75000)
            docs = ["School_Tuition_Invoice", "Attested_Dependent_Certificate"]
            comments = f"Academic tuition assistance claim of AED {amount_aed}"

        elif planted_rule == "POL-ALLOW-002":
            txn_type = "Housing Allowance"
            emp_grade = emp["grade"]
            if emp_grade <= 5:
                amount_aed = random.randint(6000, 9000)
            elif emp_grade <= 8:
                amount_aed = random.randint(11000, 15000)
            elif emp_grade <= 11:
                amount_aed = random.randint(18500, 24000)
            else:
                amount_aed = random.randint(28000, 36000)
            docs = ["Tenancy_Contract_Ejari"]
            comments = f"Monthly housing allowance renewal exceeding Grade {emp_grade} ceiling"

        elif planted_rule == "POL-SAL-001":
            txn_type = "Salary Adjustment"
            current_salary = emp["base_salary_aed"]
            hike_pct = random.uniform(0.18, 0.45)
            amount_aed = int(current_salary * hike_pct)
            docs = ["Department_Commendation"]
            comments = f"Off-cycle performance salary increase of {hike_pct*100:.1f}% (+AED {amount_aed})"

        elif planted_rule == "POL-DUP-001":
            txn_type = random.choice(["Discretionary Allowance", "Education Allowance"])
            amount_aed = random.randint(5000, 15000)
            docs = ["Allowance_Requisition", "Expense_Receipts"]
            comments = "Duplicate claim submission for project milestone allowance"

        elif planted_rule == "POL-LEAVE-001":
            txn_type = "Annual Leave"
            accrued = emp["accrued_leave_days"]
            duration_days = accrued + random.randint(8, 20)
            amount_aed = 0
            docs = ["Leave_Application_Form"]
            comments = f"Extended annual holiday booking for {duration_days} days (accrued: {accrued} days)"

        elif planted_rule == "POL-PROB-001":
            txn_type = random.choice(["Salary Adjustment", "Discretionary Allowance", "Transfer"])
            amount_aed = random.randint(3000, 8000) if txn_type != "Transfer" else 0
            docs = ["Standard_HR_Form_V2"]
            comments = "Off-cycle adjustment requested during initial probationary employment"

        elif planted_rule == "POL-SEC-001":
            emp = random.choice(ops_clearance_emps)
            emp_id = emp["employee_id"]
            txn_type = random.choice(["Transfer", "Hire"])
            docs = ["Internal_Transfer_Form", "Safety_Briefing_Signoff"]
            comments = "Transfer to Dubai International Airside Terminal 3 Ramp Handling"

        elif planted_rule == "POL-REL-001":
            rel_id = emp["declared_relative_id"]
            if rel_id and rel_id in emp_dict:
                approver = emp_dict[rel_id]
                approver_id = rel_id
                approver_name = approver["full_name"]
                approver_grade = approver["grade"]
            else:
                other_emp = random.choice(all_emps)
                approver_id = other_emp["employee_id"]
                approver_name = other_emp["full_name"]
                approver_grade = other_emp["grade"]
            txn_type = "Discretionary Allowance"
            amount_aed = random.randint(5000, 14000)
            docs = ["Family_Assistance_Grant"]
            comments = f"Special family support grant approved by declared relative {approver_name}"

        else:
            # COMPLIANT TRANSACTIONS
            if txn_type == "Salary Adjustment":
                current_salary = emp["base_salary_aed"]
                hike_pct = random.uniform(0.03, 0.10)
                amount_aed = int(current_salary * hike_pct)
                if amount_aed <= 10000:
                    approver = random.choice(mgrs_gr8_plus)
                elif amount_aed <= 25000:
                    approver = random.choice(mgrs_gr10_plus)
                else:
                    approver = random.choice(mgrs_gr12_plus)
                approver_id = approver["employee_id"]
                approver_grade = approver["grade"]
                approver_name = approver["full_name"]
                docs = ["Standard_HR_Form_V2", "Performance_Appraisal_Form"]
                comments = f"Annual merit-based salary progression (+{hike_pct*100:.1f}%)"

            elif txn_type == "Housing Allowance":
                grade = emp["grade"]
                if grade <= 5:
                    amount_aed = random.randint(2500, 4400)
                elif grade <= 8:
                    amount_aed = random.randint(5500, 9400)
                elif grade <= 11:
                    amount_aed = random.randint(10500, 15800)
                else:
                    amount_aed = random.randint(18000, 24500)
                approver = random.choice(mgrs_gr10_plus if grade >= 8 else mgrs_gr8_plus)
                approver_id = approver["employee_id"]
                approver_grade = approver["grade"]
                approver_name = approver["full_name"]
                docs = ["Standard_HR_Form_V2", "Tenancy_Contract_Ejari"]
                comments = "Standard annual housing allowance renewal in accordance with grade entitlement"

            elif txn_type == "Education Allowance":
                emp = random.choice(mgrs_gr8_plus)
                emp_id = emp["employee_id"]
                amount_aed = random.randint(15000, 42000)
                approver = random.choice(mgrs_gr10_plus)
                approver_id = approver["employee_id"]
                approver_grade = approver["grade"]
                approver_name = approver["full_name"]
                docs = ["School_Tuition_Invoice", "Attested_Dependent_Certificate"]
                comments = "Term tuition payment for enrolled dependent child"

            elif txn_type == "Sick Leave":
                duration_days = random.randint(1, 5)
                docs = ["Leave_Application_Form"] if duration_days <= 2 else ["Leave_Application_Form", "Medical_Certificate"]
                amount_aed = 0
                comments = f"Sick leave notification ({duration_days} days)"

            elif txn_type == "Annual Leave":
                accrued = emp["accrued_leave_days"]
                duration_days = random.randint(1, max(2, min(accrued + 3, 25)))
                amount_aed = 0
                docs = ["Leave_Application_Form", "Manager_Approval_Signoff"]
                comments = f"Scheduled annual leave entitlement ({duration_days} days)"

            elif txn_type == "Transfer":
                amount_aed = 0
                docs = ["Internal_Transfer_Form", "Manager_Approval_Signoff"]
                if emp["department"] in ["Flight Operations", "Cabin Crew"]:
                    docs.append("GCAA_Medical_Clearance")
                if emp["department"] in ["Airport Operations", "Cargo & Logistics", "Engineering & Maintenance"]:
                    docs.append("Airside_Security_Pass")
                approver = random.choice(mgrs_gr10_plus)
                approver_id = approver["employee_id"]
                approver_grade = approver["grade"]
                approver_name = approver["full_name"]
                comments = "Internal departmental transfer following completed service tenure"

            elif txn_type == "Exit":
                resignation_type = "Voluntary"
                required_notice = 30 if emp["grade"] <= 6 else 90
                eff_date = sub_date + datetime.timedelta(days=required_notice + random.randint(5, 20))
                docs = ["Resignation_Letter", "Handover_Clearance", "Exit_Interview_Survey"]
                amount_aed = 0
                approver = random.choice(mgrs_gr8_plus)
                approver_id = approver["employee_id"]
                approver_grade = approver["grade"]
                approver_name = approver["full_name"]
                comments = "Voluntary resignation with standard notice compliance and clearance checklist"

            else:
                amount_aed = random.randint(1000, 6000)
                docs = ["Standard_HR_Form_V2"]
                comments = "General HR operational requisition"
                
        emp_hire_dt = datetime.date.fromisoformat(emp["hire_date"])
        tenure_days = max(1, (sub_date - emp_hire_dt).days)
        tenure_months = round(tenure_days / 30.4, 1)

        if planted_rule == "POL-TIM-002":
            tenure_months = random.choice([3.2, 5.5, 8.0, 10.1])
        if planted_rule == "POL-PROB-001":
            tenure_months = random.choice([1.5, 2.8, 4.0, 5.2])

        transactions.append({
            "transaction_id": txn_id,
            "submission_date": sub_date.isoformat(),
            "effective_date": eff_date.isoformat(),
            "transaction_type": txn_type,
            "employee_id": emp_id,
            "employee_name": emp["full_name"],
            "grade": emp["grade"],
            "department": emp["department"],
            "business_unit": emp["business_unit"],
            "location": emp["location"],
            "amount_aed": amount_aed,
            "duration_days": duration_days,
            "tenure_months": tenure_months,
            "accrued_leave_balance": emp["accrued_leave_days"],
            "base_salary_aed": emp["base_salary_aed"],
            "requester_id": requester_id,
            "requester_name": requester_name,
            "approver_id": approver_id,
            "approver_name": approver_name,
            "approver_grade": approver_grade,
            "documents_attached": ";".join(docs),
            "resignation_type": resignation_type,
            "workflow_status": random.choice(["PENDING_PAYROLL", "APPROVED_BY_LINE", "PROCESSING", "AUDIT_REVIEW"]),
            "comments": comments,
            "is_planted_violation": is_violation,
            "planted_rule_id": planted_rule if planted_rule else "COMPLIANT"
        })

    # Sort by submission date
    transactions = sorted(transactions[:num_transactions], key=lambda x: x["submission_date"])
    for i, t in enumerate(transactions):
        t["transaction_id"] = f"TXN-2026-{i+1:05d}"
        
    return pd.DataFrame(transactions)

if __name__ == "__main__":
    print("Generating synthetic Emirates Group HR data pack...")
    df_emps = generate_employees(2000)
    df_emps.to_csv("data/employees.csv", index=False)
    print(f"Generated data/employees.csv: {len(df_emps)} records.")
    
    df_txns = generate_transactions(df_emps, 10000)
    df_txns.to_csv("data/transactions.csv", index=False)
    print(f"Generated data/transactions.csv: {len(df_txns)} records.")
    
    # Generate test transactions
    df_test = generate_transactions(df_emps, 2500, start_date=datetime.date(2026, 7, 1), end_date=datetime.date(2026, 10, 23))
    df_test_unlabelled = df_test.drop(columns=["is_planted_violation", "planted_rule_id"])
    df_test_unlabelled.to_csv("data/test_transactions.csv", index=False)
    print(f"Generated data/test_transactions.csv: {len(df_test_unlabelled)} records.")
    print("Data pack generation completed successfully!")
