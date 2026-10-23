"""
Emirates Group HR Continuous Compliance Intelligence Platform
FastAPI Enterprise Audit Backend
Provides high-performance continuous audit verification, plain language explanations,
human-in-the-loop triage, no-code NLP rule compiler, anomaly detection, and fairness analytics.
"""

import os
import json
import datetime
from typing import Optional, List
from fastapi import FastAPI, Query, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import pandas as pd
import numpy as np

from engine.rule_engine import ComplianceRuleEngine, RULE_DEFINITIONS
from engine.nlp_rule_parser import NLPRuleParser
from engine.anomaly_detector import HRAnomalyDetector
from engine.fairness_module import EmployeeFairnessManager

app = FastAPI(
    title="Emirates Group Continuous HR Compliance Intelligence",
    version="2.0.0",
    description="Enterprise Continuous Transaction Auditing, Explainable AI, and Human-in-the-Loop Governance"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load data on startup
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
OUTPUT_CSV = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "audit_findings_output.csv"))

employees_df = pd.read_csv(os.path.join(DATA_DIR, "employees.csv"))
transactions_df = pd.read_csv(os.path.join(DATA_DIR, "transactions.csv"))
findings_df = pd.read_csv(OUTPUT_CSV)

# In-memory stores
emp_dict = {row["employee_id"]: row.to_dict() for _, row in employees_df.iterrows()}
txn_dict = {row["transaction_id"]: row.to_dict() for _, row in transactions_df.iterrows()}

# Finding records with dynamic human decisions
findings_records = findings_df.to_dict(orient="records")
# Pre-enrich findings with employee name, department, amount, and submission date for fast filtering
for f in findings_records:
    t = txn_dict.get(f["transaction_id"], {})
    f["employee_name"] = t.get("employee_name", "Unknown Employee")
    f["department"] = t.get("department", "Corporate")
    f["business_unit"] = t.get("business_unit", "Emirates Group")
    f["amount_aed"] = float(t.get("amount_aed", 0) or 0)
    f["submission_date"] = str(t.get("submission_date", ""))
    f["human_decision"] = None
    f["decision_notes"] = None
    f["decision_timestamp"] = None
    f["decided_by"] = None

findings_map = {f["finding_id"]: f for f in findings_records}

# Engines
rule_engine = ComplianceRuleEngine(employees_df)
nlp_parser = NLPRuleParser()
anomaly_detector = HRAnomalyDetector(contamination=0.015)
fairness_manager = EmployeeFairnessManager(findings_df, employees_df)

# Load or generate anomalies
anomalies_file = os.path.join(DATA_DIR, "detected_anomalies.csv")
if os.path.exists(anomalies_file):
    anomalies_df = pd.read_csv(anomalies_file, encoding="utf-8")
else:
    anomalies_df = anomaly_detector.detect_anomalies(transactions_df)
    anomalies_df.to_csv(anomalies_file, index=False, encoding="utf-8")
anomalies_records = anomalies_df.to_dict(orient="records")

# Custom active rules list
active_custom_rules = []

# Employee appeals store
employee_appeals = []

# Models
class HumanDecisionRequest(BaseModel):
    decision: str  # REMEDIATED, APPROVED_WITH_WAIVER, RETURNED_TO_ORIGINATOR, ESCALATED_TO_AUDIT
    notes: str
    decided_by: str = "HR Compliance Lead"

class NLPRuleRequest(BaseModel):
    text: str
    severity: str = "HIGH"
    owner: str = "HR Compliance Analyst"

class EmployeeAppealRequest(BaseModel):
    finding_id: str
    employee_id: str
    appeal_reason: str
    supporting_notes: str

@app.get("/api/health")
def health_check():
    return {
        "status": "HEALTHY",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "total_transactions": len(transactions_df),
        "total_employees": len(employees_df),
        "total_findings": len(findings_records),
        "total_anomalies": len(anomalies_records),
        "compliance_coverage": "100.0%"
    }

@app.get("/api/stats")
def get_kpi_stats():
    total_txns = len(transactions_df)
    total_findings = len(findings_records)
    
    # Financial at risk (sum of amounts on financial violations)
    at_risk_aed = sum(f["amount_aed"] for f in findings_records if f["amount_aed"] > 0)
    
    # Severity breakdown
    sev_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for f in findings_records:
        sev = f.get("severity", "MEDIUM")
        sev_counts[sev] = sev_counts.get(sev, 0) + 1
        
    # Owner queues
    owner_counts = {}
    for f in findings_records:
        own = f.get("assigned_owner", "Unassigned")
        owner_counts[own] = owner_counts.get(own, 0) + 1
        
    # Category counts
    cat_counts = {}
    for f in findings_records:
        cat = f.get("violation_category", "General")
        cat_counts[cat] = cat_counts.get(cat, 0) + 1

    # Status counts (human-in-the-loop decisions)
    status_counts = {
        "FLAGGED_FOR_REVIEW": 0,
        "APPROVED_WITH_WAIVER": 0,
        "RETURNED_TO_ORIGINATOR": 0,
        "REMEDIATED": 0,
        "ESCALATED_TO_AUDIT": 0
    }
    for f in findings_records:
        st = f.get("audit_status", "FLAGGED_FOR_REVIEW")
        status_counts[st] = status_counts.get(st, 0) + 1

    return {
        "total_transactions_checked": total_txns,
        "coverage_percentage": 100.0,
        "total_exceptions_flagged": total_findings,
        "financial_exposure_at_risk_aed": round(at_risk_aed, 2),
        "severity_breakdown": sev_counts,
        "owner_queues": owner_counts,
        "category_breakdown": cat_counts,
        "workflow_status_breakdown": status_counts,
        "total_unsupervised_anomalies": len(anomalies_records)
    }

@app.get("/api/findings")
def get_findings(
    severity: Optional[str] = Query(None),
    rule_id: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    assigned_owner: Optional[str] = Query(None),
    audit_status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=200)
):
    filtered = findings_records
    
    if severity and severity != "ALL":
        filtered = [f for f in filtered if f["severity"].upper() == severity.upper()]
    if rule_id and rule_id != "ALL":
        filtered = [f for f in filtered if f["rule_id"] == rule_id]
    if department and department != "ALL":
        filtered = [f for f in filtered if f["department"] == department]
    if assigned_owner and assigned_owner != "ALL":
        filtered = [f for f in filtered if f["assigned_owner"] == assigned_owner]
    if audit_status and audit_status != "ALL":
        filtered = [f for f in filtered if f["audit_status"] == audit_status]
    if search:
        s = search.lower()
        filtered = [
            f for f in filtered if 
            s in f["finding_id"].lower() or 
            s in f["transaction_id"].lower() or 
            s in f["employee_id"].lower() or 
            s in f["employee_name"].lower() or
            s in f["rule_name"].lower() or 
            s in f["plain_language_explanation"].lower()
        ]
        
    total_count = len(filtered)
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    page_data = filtered[start_idx:end_idx]
    
    return {
        "total": total_count,
        "page": page,
        "limit": limit,
        "total_pages": max(1, (total_count + limit - 1) // limit),
        "findings": page_data
    }

@app.get("/api/findings/{finding_id}")
def get_finding_detail(finding_id: str):
    f = findings_map.get(finding_id)
    if not f:
        raise HTTPException(status_code=404, detail="Finding not found")
        
    txn = txn_dict.get(f["transaction_id"], {})
    emp = emp_dict.get(f["employee_id"], {})
    approver = emp_dict.get(txn.get("approver_id", ""), {})
    
    # Fair notice preview
    fair_notice = fairness_manager.generate_fair_notice(f, emp)
    
    return {
        "finding": f,
        "transaction_details": txn,
        "employee_profile": emp,
        "approver_profile": approver,
        "fair_notice": fair_notice
    }

@app.post("/api/findings/{finding_id}/action")
def record_human_decision(finding_id: str, req: HumanDecisionRequest):
    f = findings_map.get(finding_id)
    if not f:
        raise HTTPException(status_code=404, detail="Finding not found")
        
    valid_decisions = ["APPROVED_WITH_WAIVER", "RETURNED_TO_ORIGINATOR", "REMEDIATED", "ESCALATED_TO_AUDIT"]
    if req.decision not in valid_decisions:
        raise HTTPException(status_code=400, detail=f"Invalid decision. Choose from {valid_decisions}")
        
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    f["audit_status"] = req.decision
    f["human_decision"] = req.decision
    f["decision_notes"] = req.notes
    f["decided_by"] = req.decided_by
    f["decision_timestamp"] = now_iso
    
    return {
        "success": True,
        "finding_id": finding_id,
        "new_status": req.decision,
        "timestamp": now_iso
    }

@app.get("/api/hotspots")
def get_hotspots_and_trends():
    df_f = pd.DataFrame(findings_records)
    
    # 1. Violations by Department
    dept_hotspots = df_f["department"].value_counts().reset_index()
    dept_hotspots.columns = ["department", "count"]
    
    # 2. Violations by Rule
    rule_hotspots = df_f.groupby(["rule_id", "rule_name"]).size().reset_index(name="count")
    rule_hotspots = rule_hotspots.sort_values(by="count", ascending=False)
    
    # 3. Monthly Trends (from submission date)
    df_f["month"] = pd.to_datetime(df_f["submission_date"]).dt.strftime("%Y-%m")
    monthly_trends = df_f.groupby("month").size().reset_index(name="count").sort_values(by="month")
    
    # 4. Department x Severity Risk Matrix
    risk_matrix = df_f.groupby(["department", "severity"]).size().unstack(fill_value=0).reset_index()
    
    # 5. Financial Exposure by Department
    dept_exposure = df_f.groupby("department")["amount_aed"].sum().reset_index()
    dept_exposure = dept_exposure.sort_values(by="amount_aed", ascending=False)

    return {
        "by_department": dept_hotspots.to_dict(orient="records"),
        "by_rule": rule_hotspots.to_dict(orient="records"),
        "monthly_trends": monthly_trends.to_dict(orient="records"),
        "risk_matrix": risk_matrix.to_dict(orient="records"),
        "financial_exposure_by_dept": dept_exposure.to_dict(orient="records")
    }

@app.get("/api/rules")
def list_rules():
    rules = []
    for r_id, r_info in RULE_DEFINITIONS.items():
        # count occurrences in current findings
        count = sum(1 for f in findings_records if f["rule_id"] == r_id)
        rules.append({
            "rule_id": r_id,
            "name": r_info["name"],
            "category": r_info["category"],
            "owner": r_info["owner"],
            "description": r_info["description"],
            "violations_count": count
        })
    return {"rules": rules, "custom_rules": active_custom_rules}

@app.post("/api/rules/nlp-parse")
def parse_natural_language_rule(req: NLPRuleRequest):
    parsed = nlp_parser.parse_rule(
        req.text, 
        severity=req.severity, 
        owner=req.owner
    )
    # Test against transactions
    matches_df = nlp_parser.test_rule(parsed, transactions_df)
    
    preview_matches = matches_df[["transaction_id", "employee_name", "department", "transaction_type", "amount_aed", "submission_date"]].head(10).to_dict(orient="records")
    
    return {
        "rule_id": parsed["rule_id"],
        "rule_name": parsed["rule_name"],
        "severity": parsed["severity"],
        "owner": parsed["owner"],
        "target_type": parsed["target_type"],
        "target_dept": parsed["target_dept"],
        "amount_threshold": parsed["amount_threshold"],
        "grade_threshold": parsed["grade_threshold"],
        "duration_threshold": parsed["duration_threshold"],
        "missing_doc": parsed["missing_doc"],
        "total_matched_transactions": len(matches_df),
        "match_percentage": round((len(matches_df) / len(transactions_df)) * 100, 2),
        "sample_matches": preview_matches
    }

@app.post("/api/rules/activate")
def activate_custom_rule(rule_data: dict = Body(...)):
    active_custom_rules.append({
        "rule_id": rule_data.get("rule_id", f"POL-CUSTOM-{len(active_custom_rules)+1:03d}"),
        "name": rule_data.get("rule_name", "Custom Natural Language Rule"),
        "category": "Ad-Hoc Compliance Policy",
        "severity": rule_data.get("severity", "HIGH"),
        "owner": rule_data.get("owner", "HR Compliance Analyst"),
        "activated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "query": rule_data.get("raw_text", ""),
        "matched_count": rule_data.get("total_matched_transactions", 0)
    })
    return {"success": True, "active_custom_rules_count": len(active_custom_rules)}

@app.get("/api/anomalies")
def get_anomalies(
    pattern_type: Optional[str] = Query(None),
    severity: Optional[str] = Query(None)
):
    filtered = anomalies_records
    if pattern_type and pattern_type != "ALL":
        filtered = [a for a in filtered if a["pattern_type"] == pattern_type]
    if severity and severity != "ALL":
        filtered = [a for a in filtered if a["severity"] == severity]
    return {
        "total": len(filtered),
        "anomalies": filtered
    }

@app.get("/api/fairness")
def get_fairness_analytics():
    analytics = fairness_manager.compute_fairness_analytics(transactions_df, findings_df)
    return {
        "analytics": analytics,
        "appeals_count": len(employee_appeals),
        "recent_appeals": employee_appeals[-10:]
    }

@app.post("/api/fairness/appeal")
def file_employee_appeal(req: EmployeeAppealRequest):
    appeal_entry = {
        "appeal_id": f"APL-2026-{len(employee_appeals)+1:04d}",
        "finding_id": req.finding_id,
        "employee_id": req.employee_id,
        "reason": req.appeal_reason,
        "notes": req.supporting_notes,
        "status": "UNDER_ADMINISTRATIVE_REVIEW",
        "submitted_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "sla_resolution_target_days": 3
    }
    employee_appeals.append(appeal_entry)
    return {"success": True, "appeal": appeal_entry}

@app.get("/api/export/csv")
def export_findings_csv():
    if os.path.exists(OUTPUT_CSV):
        return FileResponse(
            OUTPUT_CSV, 
            media_type="text/csv", 
            filename="audit_findings_output.csv"
        )
    raise HTTPException(status_code=404, detail="File not found")

# Serve frontend build if exists
STATIC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"))
if os.path.exists(STATIC_DIR):
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=False)
