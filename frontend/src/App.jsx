import React, { useState, useEffect } from 'react';
import {
  Shield, AlertTriangle, AlertCircle, CheckCircle, Clock, Filter,
  Search, Download, ChevronRight, User, FileText, Sparkles, Globe,
  RefreshCw, TrendingUp, BarChart3, Layers, Lock, ArrowUpRight,
  Send, HelpCircle, Check, X, ShieldAlert, Cpu, HeartHandshake, Eye
} from 'lucide-react';

const API_BASE = '/api';

export default function App() {
  const [lang, setLang] = useState('en'); // 'en' or 'ar'
  const [persona, setPersona] = useState('analyst'); // 'analyst', 'lead', 'audit', 'fairness'
  const [activeTab, setActiveTab] = useState('workbench'); // 'workbench', 'hotspots', 'nlp', 'anomalies', 'fairness'
  
  // Data states
  const [stats, setStats] = useState(null);
  const [findings, setFindings] = useState([]);
  const [totalFindings, setTotalFindings] = useState(0);
  const [selectedFinding, setSelectedFinding] = useState(null);
  const [findingDetail, setFindingDetail] = useState(null);
  const [rules, setRules] = useState([]);
  const [hotspots, setHotspots] = useState(null);
  const [anomalies, setAnomalies] = useState([]);
  const [fairnessData, setFairnessData] = useState(null);
  const [loading, setLoading] = useState(true);

  // Filter states
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSeverity, setSelectedSeverity] = useState('ALL');
  const [selectedRule, setSelectedRule] = useState('ALL');
  const [selectedDept, setSelectedDept] = useState('ALL');
  const [selectedStatus, setSelectedStatus] = useState('ALL');
  const [page, setPage] = useState(1);

  // Human decision form
  const [decisionNotes, setDecisionNotes] = useState('');
  const [submittingAction, setSubmittingAction] = useState(false);

  // NLP Rule Studio states
  const [nlpText, setNlpText] = useState('Flag any housing allowance exceeding 12000 AED for Grade 6 or below');
  const [nlpResult, setNlpResult] = useState(null);
  const [nlpLoading, setNlpLoading] = useState(false);
  const [nlpActivated, setNlpActivated] = useState(false);

  // Employee Appeal states
  const [appealReason, setAppealReason] = useState('Supporting documentation was submitted to line manager via email');
  const [appealNotes, setAppealNotes] = useState('Please review attached email thread approving exception due to urgent operational redeployment.');
  const [appealSuccess, setAppealSuccess] = useState(false);

  // Fetch initial stats and rules
  useEffect(() => {
    fetchStats();
    fetchRules();
    fetchHotspots();
    fetchAnomalies();
    fetchFairness();
  }, []);

  // Fetch findings when filters change
  useEffect(() => {
    fetchFindings();
  }, [page, selectedSeverity, selectedRule, selectedDept, selectedStatus, searchQuery]);

  const fetchStats = async () => {
    try {
      const res = await fetch(`${API_BASE}/stats`);
      const data = await res.json();
      setStats(data);
    } catch (err) {
      console.error('Error fetching stats:', err);
    }
  };

  const fetchRules = async () => {
    try {
      const res = await fetch(`${API_BASE}/rules`);
      const data = await res.json();
      setRules(data.rules || []);
    } catch (err) {
      console.error('Error fetching rules:', err);
    }
  };

  const fetchHotspots = async () => {
    try {
      const res = await fetch(`${API_BASE}/hotspots`);
      const data = await res.json();
      setHotspots(data);
    } catch (err) {
      console.error('Error fetching hotspots:', err);
    }
  };

  const fetchAnomalies = async () => {
    try {
      const res = await fetch(`${API_BASE}/anomalies`);
      const data = await res.json();
      setAnomalies(data.anomalies || []);
    } catch (err) {
      console.error('Error fetching anomalies:', err);
    }
  };

  const fetchFairness = async () => {
    try {
      const res = await fetch(`${API_BASE}/fairness`);
      const data = await res.json();
      setFairnessData(data);
    } catch (err) {
      console.error('Error fetching fairness:', err);
    }
  };

  const fetchFindings = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        limit: '20',
        severity: selectedSeverity,
        rule_id: selectedRule,
        department: selectedDept,
        audit_status: selectedStatus,
        search: searchQuery
      });
      const res = await fetch(`${API_BASE}/findings?${params}`);
      const data = await res.json();
      setFindings(data.findings || []);
      setTotalFindings(data.total || 0);
      if (data.findings && data.findings.length > 0 && !selectedFinding) {
        loadFindingDetail(data.findings[0].finding_id);
      }
    } catch (err) {
      console.error('Error fetching findings:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadFindingDetail = async (findingId) => {
    try {
      const res = await fetch(`${API_BASE}/findings/${findingId}`);
      const data = await res.json();
      setSelectedFinding(data.finding);
      setFindingDetail(data);
      setDecisionNotes(data.finding.decision_notes || '');
    } catch (err) {
      console.error('Error loading finding detail:', err);
    }
  };

  const handleHumanDecision = async (decision) => {
    if (!selectedFinding) return;
    setSubmittingAction(true);
    try {
      const res = await fetch(`${API_BASE}/findings/${selectedFinding.finding_id}/action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          decision,
          notes: decisionNotes || `Action executed by ${persona.toUpperCase()}`,
          decided_by: persona === 'analyst' ? 'HR Compliance Analyst' : 'HR Operations Team Lead'
        })
      });
      const data = await res.json();
      if (data.success) {
        // update local state
        setSelectedFinding(prev => ({ ...prev, audit_status: decision, decision_notes: decisionNotes }));
        fetchFindings();
        fetchStats();
      }
    } catch (err) {
      console.error('Decision error:', err);
    } finally {
      setSubmittingAction(false);
    }
  };

  const handleNlpParse = async () => {
    setNlpLoading(true);
    setNlpActivated(false);
    try {
      const res = await fetch(`${API_BASE}/rules/nlp-parse`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: nlpText, severity: 'HIGH', owner: 'HR Compliance Analyst' })
      });
      const data = await res.json();
      setNlpResult(data);
    } catch (err) {
      console.error('NLP parse error:', err);
    } finally {
      setNlpLoading(false);
    }
  };

  const handleActivateNlpRule = async () => {
    if (!nlpResult) return;
    try {
      const res = await fetch(`${API_BASE}/rules/activate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(nlpResult)
      });
      const data = await res.json();
      if (data.success) {
        setNlpActivated(true);
        fetchRules();
      }
    } catch (err) {
      console.error('Activate rule error:', err);
    }
  };

  const handleFileAppeal = async () => {
    if (!selectedFinding) return;
    try {
      const res = await fetch(`${API_BASE}/fairness/appeal`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          finding_id: selectedFinding.finding_id,
          employee_id: selectedFinding.employee_id,
          appeal_reason: appealReason,
          supporting_notes: appealNotes
        })
      });
      const data = await res.json();
      if (data.success) {
        setAppealSuccess(true);
        fetchFairness();
        setTimeout(() => setAppealSuccess(false), 4000);
      }
    } catch (err) {
      console.error('Appeal error:', err);
    }
  };

  const isRTL = lang === 'ar';

  return (
    <div dir={isRTL ? 'rtl' : 'ltr'} className="min-h-screen bg-[#0B0F19] text-gray-100 flex flex-col">
      {/* TOP BRAND HEADER */}
      <header className="border-b border-gray-800 bg-[#0F1423] sticky top-0 z-50 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            
            {/* Emirates Logo & Brand Title */}
            <div className="flex items-center space-x-3 rtl:space-x-reverse">
              <div className="bg-[#D71921] text-white font-black px-3 py-1.5 rounded tracking-wider text-sm flex items-center shadow-md">
                <span>EMIRATES</span>
                <span className="text-[#C5A059] ml-1.5 font-normal rtl:mr-1.5 rtl:ml-0">GROUP</span>
              </div>
              <div className="h-6 w-px bg-gray-700 hidden sm:block"></div>
              <div>
                <h1 className="text-base font-bold text-white flex items-center gap-2">
                  <span>{isRTL ? 'نظام الامتثال المستمر للموارد البشرية' : 'Continuous HR Compliance Intelligence'}</span>
                  <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-400 border border-emerald-800">
                    {isRTL ? 'تغطية كاملة 100%' : '100% Audited'}
                  </span>
                </h1>
                <p className="text-xs text-gray-400">
                  {isRTL ? 'تدقيق مؤتمت، تفسير فوري باللغة البسيطة وحوكمة بشرية' : 'Automated Policy Auditing • Explainable AI • Human-in-the-Loop'}
                </p>
              </div>
            </div>

            {/* Persona Switcher & Controls */}
            <div className="flex items-center space-x-3 rtl:space-x-reverse">
              {/* Persona Selector */}
              <div className="hidden lg:flex items-center bg-[#151C2C] border border-gray-700 rounded-lg p-0.5">
                {[
                  { id: 'analyst', label: isRTL ? 'محلل الامتثال' : 'HR Analyst', icon: Shield },
                  { id: 'lead', label: isRTL ? 'رئيس العمليات' : 'Ops Lead', icon: Layers },
                  { id: 'audit', label: isRTL ? 'التدقيق الداخلي' : 'Internal Audit', icon: BarChart3 },
                  { id: 'fairness', label: isRTL ? 'تجربة الموظف' : 'Fairness & Equity', icon: HeartHandshake }
                ].map(p => {
                  const Icon = p.icon;
                  const active = persona === p.id;
                  return (
                    <button
                      key={p.id}
                      onClick={() => setPersona(p.id)}
                      className={`flex items-center gap-1.5 px-3 py-1 text-xs font-medium rounded-md transition-all ${
                        active ? 'bg-[#D71921] text-white shadow' : 'text-gray-400 hover:text-white'
                      }`}
                    >
                      <Icon className="w-3.5 h-3.5" />
                      <span>{p.label}</span>
                    </button>
                  );
                })}
              </div>

              {/* Language Switcher */}
              <button
                onClick={() => setLang(lang === 'en' ? 'ar' : 'en')}
                className="flex items-center gap-1 px-2.5 py-1 text-xs font-semibold rounded-md border border-gray-700 bg-[#151C2C] text-gray-200 hover:border-[#C5A059] transition-colors"
                title={isRTL ? 'Switch to English' : 'التحويل إلى العربية'}
              >
                <Globe className="w-3.5 h-3.5 text-[#C5A059]" />
                <span>{lang === 'en' ? 'العربية' : 'English'}</span>
              </button>

              {/* Export Pack CSV Button */}
              <a
                href={`${API_BASE}/export/csv`}
                download="audit_findings_output.csv"
                className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-md bg-[#C5A059] hover:bg-[#b08d47] text-black font-semibold shadow transition-all"
              >
                <Download className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">{isRTL ? 'تصدير ملف التدقيق' : 'Export Findings CSV'}</span>
              </a>
            </div>

          </div>
        </div>

        {/* NAVIGATION TABS */}
        <div className="bg-[#111726] border-t border-gray-800/80 px-4 sm:px-6 lg:px-8">
          <div className="max-w-7xl mx-auto flex space-x-1 rtl:space-x-reverse overflow-x-auto py-1">
            {[
              { id: 'workbench', label: isRTL ? 'منصة فحص الاستثناءات' : 'Exception Triage Workbench', count: totalFindings },
              { id: 'hotspots', label: isRTL ? 'بؤر المخاطر والاتجاهات' : 'Hotspots & Trends Analytics', icon: TrendingUp },
              { id: 'nlp', label: isRTL ? 'منشئ القواعد باللغة الطبيعية' : 'No-Code NLP Rule Studio', icon: Sparkles, badge: 'New' },
              { id: 'anomalies', label: isRTL ? 'كاشف الأنماط الشاذة (ذكاء اصطناعي)' : 'Unsupervised Anomaly Detector', count: anomalies.length, icon: Cpu },
              { id: 'fairness', label: isRTL ? 'العدالة الإجرائية وتجربة الموظف' : 'Fairness & Employee Experience', icon: HeartHandshake }
            ].map(tab => {
              const active = activeTab === tab.id;
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-4 py-2 text-xs font-medium rounded-md transition-all whitespace-nowrap ${
                    active
                      ? 'bg-[#1E293B] text-white border-b-2 border-[#D71921] font-semibold'
                      : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/40'
                  }`}
                >
                  {Icon && <Icon className="w-3.5 h-3.5 text-[#C5A059]" />}
                  <span>{tab.label}</span>
                  {tab.count !== undefined && (
                    <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-gray-800 text-gray-300 border border-gray-700">
                      {tab.count.toLocaleString()}
                    </span>
                  )}
                  {tab.badge && (
                    <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-[#D71921] text-white font-bold">
                      {tab.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        </div>
      </header>

      {/* KPI METRIC STRIP */}
      {stats && (
        <section className="bg-[#0D121F] border-b border-gray-800 py-3">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3">
              
              <div className="bg-[#131A2B] border border-gray-800 p-2.5 rounded-lg flex items-center justify-between">
                <div>
                  <p className="text-[11px] text-gray-400">{isRTL ? 'المعاملات المدققة' : 'Transactions Audited'}</p>
                  <p className="text-lg font-bold text-white">10,000</p>
                  <span className="text-[10px] text-emerald-400">100% {isRTL ? 'تغطية شاملة' : 'Coverage (0% Sampling)'}</span>
                </div>
                <CheckCircle className="w-6 h-6 text-emerald-500 opacity-80" />
              </div>

              <div className="bg-[#131A2B] border border-gray-800 p-2.5 rounded-lg flex items-center justify-between">
                <div>
                  <p className="text-[11px] text-gray-400">{isRTL ? 'الاستثناءات المرصودة' : 'Exceptions Flagged'}</p>
                  <p className="text-lg font-bold text-amber-400">{stats.total_exceptions_flagged.toLocaleString()}</p>
                  <span className="text-[10px] text-gray-400">{((stats.total_exceptions_flagged / stats.total_transactions_checked) * 100).toFixed(1)}% {isRTL ? 'نسبة الاستثناء' : 'Exception Rate'}</span>
                </div>
                <AlertTriangle className="w-6 h-6 text-amber-500 opacity-80" />
              </div>

              <div className="bg-[#131A2B] border border-gray-800 p-2.5 rounded-lg flex items-center justify-between">
                <div>
                  <p className="text-[11px] text-gray-400">{isRTL ? 'التعرض المالي تحت الخطر' : 'Financial Exposure'}</p>
                  <p className="text-lg font-bold text-[#E5C378]">AED {(stats.financial_exposure_at_risk_aed / 1000000).toFixed(1)}M</p>
                  <span className="text-[10px] text-gray-400">{isRTL ? 'إجمالي المبالغ المخالفة' : 'At-Risk Requisitions'}</span>
                </div>
                <Lock className="w-6 h-6 text-[#C5A059] opacity-80" />
              </div>

              <div className="bg-[#131A2B] border border-gray-800 p-2.5 rounded-lg flex items-center justify-between">
                <div>
                  <p className="text-[11px] text-gray-400">{isRTL ? 'مخالفات حرجة' : 'Critical Severity'}</p>
                  <p className="text-lg font-bold text-rose-500">{stats.severity_breakdown.CRITICAL || 0}</p>
                  <span className="text-[10px] text-rose-400">{isRTL ? 'تتطلب تدخلاً فورياً' : 'Urgent Action'}</span>
                </div>
                <ShieldAlert className="w-6 h-6 text-rose-500 opacity-80" />
              </div>

              <div className="bg-[#131A2B] border border-gray-800 p-2.5 rounded-lg flex items-center justify-between">
                <div>
                  <p className="text-[11px] text-gray-400">{isRTL ? 'أنماط شاذة بالـ ML' : 'ML Anomalies'}</p>
                  <p className="text-lg font-bold text-cyan-400">{stats.total_unsupervised_anomalies}</p>
                  <span className="text-[10px] text-cyan-400">{isRTL ? 'خارج القواعد الثابتة' : 'Beyond Written Rules'}</span>
                </div>
                <Cpu className="w-6 h-6 text-cyan-400 opacity-80" />
              </div>

              <div className="bg-[#131A2B] border border-gray-800 p-2.5 rounded-lg flex items-center justify-between">
                <div>
                  <p className="text-[11px] text-gray-400">{isRTL ? 'قرارات المحكمين' : 'Human Decisions'}</p>
                  <p className="text-lg font-bold text-indigo-400">
                    {stats.workflow_status_breakdown.APPROVED_WITH_WAIVER + stats.workflow_status_breakdown.RETURNED_TO_ORIGINATOR + stats.workflow_status_breakdown.REMEDIATED + stats.workflow_status_breakdown.ESCALATED_TO_AUDIT}
                  </p>
                  <span className="text-[10px] text-indigo-400">{isRTL ? 'قرارات بشرية مسجلة' : 'Human In The Loop'}</span>
                </div>
                <User className="w-6 h-6 text-indigo-400 opacity-80" />
              </div>

            </div>
          </div>
        </section>
      )}

      {/* MAIN CONTENT AREA */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        
        {/* ------------------------------------------------------------- */}
        {/* TAB 1: EXCEPTION WORKBENCH (TRIAGE SPLIT SCREEN) */}
        {/* ------------------------------------------------------------- */}
        {activeTab === 'workbench' && (
          <div className="space-y-4">
            
            {/* Filter Toolbar */}
            <div className="bg-[#131A2B] border border-gray-800 p-3 rounded-lg flex flex-wrap gap-3 items-center justify-between shadow">
              
              {/* Search Bar */}
              <div className="relative flex-1 min-w-[240px]">
                <Search className={`w-4 h-4 absolute top-2.5 text-gray-400 ${isRTL ? 'right-3' : 'left-3'}`} />
                <input
                  type="text"
                  placeholder={isRTL ? 'بحث بالموظف، المعاملة، القاعدة أو الكلمة المفتاحية...' : 'Search by employee, transaction ID, rule name, or text...'}
                  value={searchQuery}
                  onChange={(e) => { setSearchQuery(e.target.value); setPage(1); }}
                  className={`w-full bg-[#0D121F] border border-gray-700 rounded-md py-1.5 text-xs text-gray-100 placeholder-gray-500 focus:outline-none focus:border-[#C5A059] ${
                    isRTL ? 'pr-9 pl-3' : 'pl-9 pr-3'
                  }`}
                />
              </div>

              {/* Filters */}
              <div className="flex flex-wrap gap-2 items-center">
                {/* Severity */}
                <select
                  value={selectedSeverity}
                  onChange={(e) => { setSelectedSeverity(e.target.value); setPage(1); }}
                  className="bg-[#0D121F] border border-gray-700 rounded-md py-1.5 px-2.5 text-xs text-gray-200 focus:outline-none focus:border-[#C5A059]"
                >
                  <option value="ALL">{isRTL ? 'جميع مستويات الخطورة' : 'All Severities'}</option>
                  <option value="CRITICAL">🔴 CRITICAL</option>
                  <option value="HIGH">🟠 HIGH</option>
                  <option value="MEDIUM">🟡 MEDIUM</option>
                  <option value="LOW">🔵 LOW</option>
                </select>

                {/* Rule */}
                <select
                  value={selectedRule}
                  onChange={(e) => { setSelectedRule(e.target.value); setPage(1); }}
                  className="bg-[#0D121F] border border-gray-700 rounded-md py-1.5 px-2.5 text-xs text-gray-200 focus:outline-none focus:border-[#C5A059] max-w-[180px]"
                >
                  <option value="ALL">{isRTL ? 'جميع القواعد' : 'All Policy Rules'}</option>
                  {rules.map(r => (
                    <option key={r.rule_id} value={r.rule_id}>{r.rule_id} - {r.name}</option>
                  ))}
                </select>

                {/* Department */}
                <select
                  value={selectedDept}
                  onChange={(e) => { setSelectedDept(e.target.value); setPage(1); }}
                  className="bg-[#0D121F] border border-gray-700 rounded-md py-1.5 px-2.5 text-xs text-gray-200 focus:outline-none focus:border-[#C5A059]"
                >
                  <option value="ALL">{isRTL ? 'جميع الدوائر' : 'All Departments'}</option>
                  <option value="Flight Operations">Flight Operations</option>
                  <option value="Cabin Crew">Cabin Crew</option>
                  <option value="Airport Operations">Airport Operations (dnata)</option>
                  <option value="Cargo & Logistics">Cargo & Logistics (dnata)</option>
                  <option value="Engineering & Maintenance">Engineering & Maintenance</option>
                  <option value="Group IT & Digital">Group IT & Digital</option>
                  <option value="Human Resources">Human Resources</option>
                  <option value="Finance & Procurement">Finance & Procurement</option>
                  <option value="Catering Services">Catering Services</option>
                </select>

                {/* Status */}
                <select
                  value={selectedStatus}
                  onChange={(e) => { setSelectedStatus(e.target.value); setPage(1); }}
                  className="bg-[#0D121F] border border-gray-700 rounded-md py-1.5 px-2.5 text-xs text-gray-200 focus:outline-none focus:border-[#C5A059]"
                >
                  <option value="ALL">{isRTL ? 'جميع الحالات' : 'All Review Statuses'}</option>
                  <option value="FLAGGED_FOR_REVIEW">{isRTL ? 'قيد المراجعة' : 'Flagged for Review'}</option>
                  <option value="APPROVED_WITH_WAIVER">{isRTL ? 'معتمد باستثناء' : 'Approved with Waiver'}</option>
                  <option value="RETURNED_TO_ORIGINATOR">{isRTL ? 'معاد للمنشئ' : 'Returned to Submitter'}</option>
                  <option value="REMEDIATED">{isRTL ? 'تمت التسوية' : 'Remediated & Closed'}</option>
                  <option value="ESCALATED_TO_AUDIT">{isRTL ? 'مصعد للتدقيق' : 'Escalated to Audit'}</option>
                </select>

                {/* Clear filters */}
                <button
                  onClick={() => {
                    setSelectedSeverity('ALL');
                    setSelectedRule('ALL');
                    setSelectedDept('ALL');
                    setSelectedStatus('ALL');
                    setSearchQuery('');
                    setPage(1);
                  }}
                  className="p-1.5 text-gray-400 hover:text-white rounded border border-gray-700 bg-[#0D121F]"
                  title="Reset Filters"
                >
                  <RefreshCw className="w-3.5 h-3.5" />
                </button>
              </div>

            </div>

            {/* Split Screen Container */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
              
              {/* LEFT LIST PANE (5 cols) */}
              <div className="lg:col-span-5 flex flex-col h-[700px] bg-[#111726] border border-gray-800 rounded-lg overflow-hidden shadow">
                
                {/* List Header */}
                <div className="p-3 border-b border-gray-800 bg-[#131A2B] flex items-center justify-between">
                  <div className="text-xs font-semibold text-gray-200 flex items-center gap-1.5">
                    <Filter className="w-3.5 h-3.5 text-[#C5A059]" />
                    <span>{isRTL ? 'قائمة الاستثناءات' : 'Flagged Exceptions Queue'}</span>
                    <span className="text-[11px] text-gray-400">({totalFindings.toLocaleString()})</span>
                  </div>
                  <div className="text-[11px] text-gray-400">
                    {isRTL ? `الصفحة ${page}` : `Page ${page}`}
                  </div>
                </div>

                {/* List Scrollable Body */}
                <div className="flex-1 overflow-y-auto divide-y divide-gray-800/80">
                  {loading ? (
                    <div className="flex items-center justify-center h-48 text-gray-400 text-xs">
                      <RefreshCw className="w-4 h-4 animate-spin mr-2" />
                      <span>{isRTL ? 'جاري تحميل المعاملات...' : 'Auditing transactions...'}</span>
                    </div>
                  ) : findings.length === 0 ? (
                    <div className="p-8 text-center text-gray-500 text-xs">
                      <CheckCircle className="w-8 h-8 text-emerald-500/60 mx-auto mb-2" />
                      <p>{isRTL ? 'لا توجد استثناءات مطابقة للفلاتر المختارة.' : 'No exceptions found matching current filter parameters.'}</p>
                    </div>
                  ) : (
                    findings.map(f => {
                      const isSelected = selectedFinding && selectedFinding.finding_id === f.finding_id;
                      const sevColor = 
                        f.severity === 'CRITICAL' ? 'bg-rose-950/70 border-rose-800 text-rose-300' :
                        f.severity === 'HIGH' ? 'bg-amber-950/70 border-amber-800 text-amber-300' :
                        f.severity === 'MEDIUM' ? 'bg-yellow-950/50 border-yellow-800 text-yellow-300' :
                        'bg-blue-950/50 border-blue-800 text-blue-300';

                      return (
                        <div
                          key={f.finding_id}
                          onClick={() => loadFindingDetail(f.finding_id)}
                          className={`p-3 cursor-pointer transition-colors hover:bg-gray-800/40 ${
                            isSelected ? 'bg-gray-800/80 border-l-4 border-l-[#D71921]' : ''
                          }`}
                        >
                          <div className="flex items-start justify-between gap-2 mb-1">
                            <span className="font-mono text-[11px] text-gray-400">{f.finding_id}</span>
                            <span className={`text-[10px] px-1.5 py-0.5 rounded border font-semibold ${sevColor}`}>
                              {f.severity}
                            </span>
                          </div>

                          <div className="text-xs font-semibold text-white mb-1 line-clamp-1">
                            {f.rule_name}
                          </div>

                          <div className="text-[11px] text-gray-400 mb-1.5 line-clamp-2">
                            {isRTL && f.plain_language_explanation_ar ? f.plain_language_explanation_ar : f.plain_language_explanation}
                          </div>

                          <div className="flex items-center justify-between text-[10px] text-gray-500 pt-1 border-t border-gray-800/60">
                            <span className="text-gray-300 font-medium">{f.employee_name} ({f.employee_id})</span>
                            <span className="text-[#C5A059] font-mono">
                              {f.amount_aed > 0 ? `AED ${Number(f.amount_aed).toLocaleString()}` : f.department}
                            </span>
                          </div>
                        </div>
                      );
                    })
                  )}
                </div>

                {/* Pagination footer */}
                <div className="p-2 border-t border-gray-800 bg-[#131A2B] flex items-center justify-between text-xs">
                  <button
                    disabled={page <= 1}
                    onClick={() => setPage(p => Math.max(1, p - 1))}
                    className="px-2.5 py-1 rounded bg-[#0D121F] border border-gray-700 text-gray-300 disabled:opacity-30 disabled:cursor-not-allowed hover:border-gray-500"
                  >
                    {isRTL ? 'السابق' : 'Previous'}
                  </button>
                  <span className="text-[11px] text-gray-400">
                    {isRTL ? `صفحة ${page}` : `Page ${page}`}
                  </span>
                  <button
                    onClick={() => setPage(p => p + 1)}
                    className="px-2.5 py-1 rounded bg-[#0D121F] border border-gray-700 text-gray-300 hover:border-gray-500"
                  >
                    {isRTL ? 'التالي' : 'Next'}
                  </button>
                </div>

              </div>

              {/* RIGHT DETAIL PANE (7 cols) */}
              <div className="lg:col-span-7 flex flex-col h-[700px] bg-[#111726] border border-gray-800 rounded-lg overflow-y-auto shadow p-5">
                
                {selectedFinding && findingDetail ? (
                  <div className="space-y-4">
                    
                    {/* Header info */}
                    <div className="border-b border-gray-800 pb-3 flex items-start justify-between">
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-mono text-xs text-[#C5A059] font-bold">{selectedFinding.finding_id}</span>
                          <span className="text-xs text-gray-500">•</span>
                          <span className="font-mono text-xs text-gray-400">{selectedFinding.transaction_id}</span>
                          <span className={`text-[10px] font-bold px-2 py-0.5 rounded border ${
                            selectedFinding.severity === 'CRITICAL' ? 'bg-rose-950 text-rose-300 border-rose-800' :
                            selectedFinding.severity === 'HIGH' ? 'bg-amber-950 text-amber-300 border-amber-800' :
                            'bg-yellow-950 text-yellow-300 border-yellow-800'
                          }`}>
                            {selectedFinding.severity}
                          </span>
                        </div>
                        <h2 className="text-base font-bold text-white">{selectedFinding.rule_name}</h2>
                        <p className="text-xs text-gray-400">{selectedFinding.violation_category}</p>
                      </div>

                      {/* Review status badge */}
                      <div className="text-right rtl:text-left">
                        <span className="text-[10px] text-gray-400 block mb-1">{isRTL ? 'حالة المراجعة' : 'Audit Status'}</span>
                        <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-gray-800 text-gray-200 border border-gray-700">
                          {selectedFinding.audit_status}
                        </span>
                      </div>
                    </div>

                    {/* Plain Language Explanation Card */}
                    <div className="bg-[#151D2F] border border-indigo-950/60 p-3.5 rounded-lg">
                      <div className="flex items-center gap-2 mb-2">
                        <Sparkles className="w-4 h-4 text-[#C5A059]" />
                        <h3 className="text-xs font-bold text-indigo-300 uppercase tracking-wide">
                          {isRTL ? 'التفسير باللغة البسيطة (ذكاء اصطناعي قابل للتفسير)' : 'Plain Language Exception Explanation'}
                        </h3>
                      </div>
                      
                      {/* Bilingual text display */}
                      <div className="space-y-2 text-xs leading-relaxed">
                        <p className="text-gray-200 font-medium bg-[#0D121F] p-2.5 rounded border border-gray-800">
                          <span className="text-[10px] font-bold text-gray-500 block mb-0.5">ENGLISH EXPLANATION:</span>
                          {selectedFinding.plain_language_explanation}
                        </p>
                        <p className="text-gray-200 font-medium bg-[#0D121F] p-2.5 rounded border border-gray-800 text-right rtl:text-right" dir="rtl">
                          <span className="text-[10px] font-bold text-gray-500 block mb-0.5">التوضيح باللغة العربية:</span>
                          {selectedFinding.plain_language_explanation_ar || selectedFinding.plain_language_explanation}
                        </p>
                      </div>
                    </div>

                    {/* Cited Evidence Key-Value Matrix */}
                    <div className="bg-[#0E1422] border border-gray-800 p-3 rounded-lg">
                      <div className="flex items-center gap-1.5 mb-2 text-xs font-semibold text-gray-300">
                        <FileText className="w-3.5 h-3.5 text-amber-400" />
                        <span>{isRTL ? 'الأدلة والبيانات المخالفة المرصودة' : 'Cited Policy Evidence & Data Discrepancy'}</span>
                      </div>
                      <div className="font-mono text-xs text-amber-300 bg-[#070B13] p-2.5 rounded border border-gray-800 break-all">
                        {selectedFinding.cited_evidence}
                      </div>
                    </div>

                    {/* Transaction & Employee Profile Grid */}
                    <div className="grid grid-cols-2 gap-3 text-xs">
                      
                      {/* Employee Card */}
                      <div className="bg-[#131A2B] border border-gray-800 p-3 rounded-lg space-y-1.5">
                        <div className="text-[11px] font-bold text-gray-400 flex items-center gap-1">
                          <User className="w-3 h-3 text-[#C5A059]" />
                          <span>{isRTL ? 'الموظف المعني' : 'Beneficiary Employee'}</span>
                        </div>
                        <div className="font-semibold text-white">{selectedFinding.employee_name}</div>
                        <div className="text-gray-400 text-[11px]">ID: <span className="font-mono text-gray-200">{selectedFinding.employee_id}</span></div>
                        <div className="text-gray-400 text-[11px]">Department: <span className="text-gray-200">{findingDetail.transaction_details?.department || selectedFinding.department}</span></div>
                        <div className="text-gray-400 text-[11px]">Grade: <span className="text-gray-200">{findingDetail.transaction_details?.grade || 'N/A'}</span></div>
                        <div className="text-gray-400 text-[11px]">Base Salary: <span className="text-[#C5A059] font-mono">AED {Number(findingDetail.transaction_details?.base_salary_aed || 0).toLocaleString()}</span></div>
                      </div>

                      {/* Transaction Workflow Card */}
                      <div className="bg-[#131A2B] border border-gray-800 p-3 rounded-lg space-y-1.5">
                        <div className="text-[11px] font-bold text-gray-400 flex items-center gap-1">
                          <Clock className="w-3 h-3 text-emerald-400" />
                          <span>{isRTL ? 'بيانات المعاملة والاعتماد' : 'Workflow & Approver'}</span>
                        </div>
                        <div className="text-gray-400 text-[11px]">Type: <span className="font-semibold text-white">{findingDetail.transaction_details?.transaction_type}</span></div>
                        <div className="text-gray-400 text-[11px]">Approver: <span className="text-gray-200">{findingDetail.transaction_details?.approver_name} (Gr {findingDetail.transaction_details?.approver_grade})</span></div>
                        <div className="text-gray-400 text-[11px]">Amount: <span className="text-emerald-400 font-mono font-bold">AED {Number(findingDetail.transaction_details?.amount_aed || 0).toLocaleString()}</span></div>
                        <div className="text-gray-400 text-[11px]">Submission Date: <span className="font-mono text-gray-200">{findingDetail.transaction_details?.submission_date}</span></div>
                        <div className="text-gray-400 text-[11px]">Docs: <span className="text-gray-300 font-mono text-[10px]">{findingDetail.transaction_details?.documents_attached || 'None'}</span></div>
                      </div>

                    </div>

                    {/* Routing & Action Recommendation Card */}
                    <div className="bg-[#141C2E] border border-gray-800 p-3 rounded-lg space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-gray-300">{isRTL ? 'مسؤول المتابعة المكلف' : 'Assigned Action Owner'}</span>
                        <span className="text-xs font-semibold px-2 py-0.5 rounded bg-indigo-950 text-indigo-300 border border-indigo-800">
                          {selectedFinding.assigned_owner}
                        </span>
                      </div>
                      <div>
                        <span className="text-[11px] text-gray-400 block mb-1">{isRTL ? 'الإجراء التصحيحي المقترح' : 'Suggested Corrective Action'}</span>
                        <p className="text-xs text-gray-200 bg-[#0D121F] p-2 rounded border border-gray-800 leading-relaxed">
                          {isRTL && selectedFinding.suggested_corrective_action_ar ? selectedFinding.suggested_corrective_action_ar : selectedFinding.suggested_corrective_action}
                        </p>
                      </div>
                    </div>

                    {/* HUMAN-IN-THE-LOOP TRIAGE WORKBENCH */}
                    <div className="bg-[#171F33] border-2 border-indigo-900/60 p-4 rounded-lg space-y-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-1.5">
                          <Lock className="w-4 h-4 text-[#C5A059]" />
                          <h4 className="text-xs font-bold text-white uppercase tracking-wide">
                            {isRTL ? 'حوكمة القرار البشري (Human-in-the-Loop Decision)' : 'Authorized Human Decision Workbench'}
                          </h4>
                        </div>
                        <span className="text-[10px] text-gray-400 font-medium">
                          {isRTL ? 'الآلة توصي • والإنسان يقرر' : 'Tool Recommends • Human Decides'}
                        </span>
                      </div>

                      {/* Decision Notes */}
                      <div>
                        <textarea
                          rows={2}
                          placeholder={isRTL ? 'أدخل مبررات القرار أو ملاحظات التدقيق هنا...' : 'Enter formal justification notes or corrective directions...'}
                          value={decisionNotes}
                          onChange={(e) => setDecisionNotes(e.target.value)}
                          className="w-full bg-[#0D121F] border border-gray-700 rounded-md p-2 text-xs text-gray-100 placeholder-gray-500 focus:outline-none focus:border-[#C5A059]"
                        />
                      </div>

                      {/* Action Buttons */}
                      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                        <button
                          disabled={submittingAction}
                          onClick={() => handleHumanDecision('APPROVED_WITH_WAIVER')}
                          className="px-2.5 py-1.5 text-xs font-semibold rounded bg-emerald-950 hover:bg-emerald-900 text-emerald-300 border border-emerald-700 transition"
                        >
                          {isRTL ? 'اعتماد باستثناء' : 'Approve with Waiver'}
                        </button>
                        <button
                          disabled={submittingAction}
                          onClick={() => handleHumanDecision('RETURNED_TO_ORIGINATOR')}
                          className="px-2.5 py-1.5 text-xs font-semibold rounded bg-amber-950 hover:bg-amber-900 text-amber-300 border border-amber-700 transition"
                        >
                          {isRTL ? 'إعادة للمنشئ' : 'Return to Originator'}
                        </button>
                        <button
                          disabled={submittingAction}
                          onClick={() => handleHumanDecision('REMEDIATED')}
                          className="px-2.5 py-1.5 text-xs font-semibold rounded bg-indigo-950 hover:bg-indigo-900 text-indigo-300 border border-indigo-700 transition"
                        >
                          {isRTL ? 'إغلاق وتسوية' : 'Remediate & Close'}
                        </button>
                        <button
                          disabled={submittingAction}
                          onClick={() => handleHumanDecision('ESCALATED_TO_AUDIT')}
                          className="px-2.5 py-1.5 text-xs font-semibold rounded bg-rose-950 hover:bg-rose-900 text-rose-300 border border-rose-700 transition"
                        >
                          {isRTL ? 'تصعيد للتدقيق' : 'Escalate to Audit'}
                        </button>
                      </div>

                      {selectedFinding.decided_by && (
                        <div className="text-[10px] text-gray-400 pt-1 border-t border-gray-800">
                          {isRTL ? 'آخر قرار مسجل بواسطة: ' : 'Last recorded decision by: '} 
                          <span className="text-gray-200 font-semibold">{selectedFinding.decided_by}</span> ({selectedFinding.decision_timestamp})
                        </div>
                      )}
                    </div>

                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center h-full text-gray-500 text-xs">
                    <Eye className="w-8 h-8 text-gray-600 mb-2" />
                    <span>{isRTL ? 'اختر معاملة من القائمة لعرض تفاصيلها' : 'Select an exception from the queue to view audit evidence.'}</span>
                  </div>
                )}

              </div>

            </div>

          </div>
        )}

        {/* ------------------------------------------------------------- */}
        {/* TAB 2: HOTSPOTS & TRENDS ANALYTICS */}
        {/* ------------------------------------------------------------- */}
        {activeTab === 'hotspots' && hotspots && (
          <div className="space-y-6">
            
            <div className="bg-[#131A2B] border border-gray-800 p-4 rounded-lg flex items-center justify-between">
              <div>
                <h2 className="text-base font-bold text-white flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-[#C5A059]" />
                  <span>{isRTL ? 'تحليلات بؤر المخاطر والاتجاهات الزمنية' : 'Compliance Hotspots & 12-Month Trend Analytics'}</span>
                </h2>
                <p className="text-xs text-gray-400">
                  {isRTL ? 'توزيع المخالفات حسب الدوائر، القواعد وفترات الرواتب' : 'Real-time aggregated risk matrix across business units, policy rules, and payroll processing cycles.'}
                </p>
              </div>
              <div className="text-xs font-semibold px-3 py-1 rounded bg-[#0D121F] text-[#C5A059] border border-gray-700">
                100% {isRTL ? 'شامل لكافة المعاملات' : 'Full Population Audited'}
              </div>
            </div>

            {/* Grid of Hotspots */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              
              {/* Violations by Policy Rule */}
              <div className="bg-[#111726] border border-gray-800 rounded-lg p-4 shadow">
                <h3 className="text-xs font-bold text-gray-200 uppercase tracking-wide mb-3 flex items-center gap-1.5">
                  <BarChart3 className="w-3.5 h-3.5 text-[#D71921]" />
                  <span>{isRTL ? 'أكثر القواعد تعرضاً للمخالفة' : 'Top Violated Policy Rules'}</span>
                </h3>
                <div className="space-y-2.5">
                  {hotspots.by_rule.slice(0, 8).map(r => {
                    const maxVal = hotspots.by_rule[0]?.count || 1;
                    const pct = Math.round((r.count / maxVal) * 100);
                    return (
                      <div key={r.rule_id} className="text-xs">
                        <div className="flex justify-between mb-1">
                          <span className="font-semibold text-gray-300 truncate max-w-[280px]">{r.rule_id} - {r.rule_name}</span>
                          <span className="font-mono text-gray-400">{r.count}</span>
                        </div>
                        <div className="w-full bg-gray-800 rounded-full h-2 overflow-hidden">
                          <div className="bg-[#D71921] h-2 rounded-full" style={{ width: `${pct}%` }}></div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Violations by Department */}
              <div className="bg-[#111726] border border-gray-800 rounded-lg p-4 shadow">
                <h3 className="text-xs font-bold text-gray-200 uppercase tracking-wide mb-3 flex items-center gap-1.5">
                  <Layers className="w-3.5 h-3.5 text-[#C5A059]" />
                  <span>{isRTL ? 'توزيع المخالفات حسب الدوائر والقطاعات' : 'Exceptions by Department / Business Unit'}</span>
                </h3>
                <div className="space-y-2.5">
                  {hotspots.by_department.slice(0, 8).map(d => {
                    const maxVal = hotspots.by_department[0]?.count || 1;
                    const pct = Math.round((d.count / maxVal) * 100);
                    return (
                      <div key={d.department} className="text-xs">
                        <div className="flex justify-between mb-1">
                          <span className="font-semibold text-gray-300">{d.department}</span>
                          <span className="font-mono text-gray-400">{d.count}</span>
                        </div>
                        <div className="w-full bg-gray-800 rounded-full h-2 overflow-hidden">
                          <div className="bg-[#C5A059] h-2 rounded-full" style={{ width: `${pct}%` }}></div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* 12-Month Timeline Trends */}
              <div className="bg-[#111726] border border-gray-800 rounded-lg p-4 shadow md:col-span-2">
                <h3 className="text-xs font-bold text-gray-200 uppercase tracking-wide mb-3 flex items-center gap-1.5">
                  <TrendingUp className="w-3.5 h-3.5 text-emerald-400" />
                  <span>{isRTL ? 'المنحنى الزمني الشهري للمخالفات (12 شهراً)' : '12-Month Monthly Exception Volume Curve'}</span>
                </h3>
                <div className="grid grid-cols-6 sm:grid-cols-12 gap-2 pt-2">
                  {hotspots.monthly_trends.map(m => (
                    <div key={m.month} className="flex flex-col items-center">
                      <div className="text-[10px] text-gray-400 font-mono mb-1">{m.count}</div>
                      <div className="w-full bg-gray-800 rounded-t h-28 flex items-end justify-center">
                        <div
                          className="w-full bg-indigo-500 hover:bg-indigo-400 transition-all rounded-t"
                          style={{ height: `${Math.min(100, Math.max(15, (m.count / 350) * 100))}%` }}
                        ></div>
                      </div>
                      <div className="text-[9px] text-gray-500 font-mono mt-1 rotate-45 sm:rotate-0">{m.month.slice(5)}</div>
                    </div>
                  ))}
                </div>
              </div>

            </div>

          </div>
        )}

        {/* ------------------------------------------------------------- */}
        {/* TAB 3: NO-CODE NLP RULE STUDIO */}
        {/* ------------------------------------------------------------- */}
        {activeTab === 'nlp' && (
          <div className="space-y-6">
            
            <div className="bg-[#131A2B] border border-gray-800 p-4 rounded-lg flex items-center justify-between">
              <div>
                <h2 className="text-base font-bold text-white flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-[#C5A059]" />
                  <span>{isRTL ? 'منشئ القواعد باللغة الطبيعية (بدون كتابة كود)' : 'No-Code Natural Language Policy Rule Studio'}</span>
                </h2>
                <p className="text-xs text-gray-400">
                  {isRTL ? 'اكتب قاعدة سياسات بالإنجليزية البسيطة ليقوم النظام بتحويلها فورياً إلى منطق تدقيق قابل للتنفيذ' : 'Empower HR compliance analysts to define new governance rules in plain English without coding.'}
                </p>
              </div>
            </div>

            {/* Interactive Query Box */}
            <div className="bg-[#111726] border border-gray-800 p-5 rounded-lg space-y-4 shadow">
              <label className="text-xs font-bold text-gray-300 block">
                {isRTL ? 'نص القاعدة باللغة الإنجليزية البسيطة:' : 'Natural Language Rule Prompt:'}
              </label>

              <div className="flex gap-2">
                <input
                  type="text"
                  value={nlpText}
                  onChange={(e) => setNlpText(e.target.value)}
                  placeholder="e.g. Flag housing allowance exceeding 12000 AED for Grade 6 or below"
                  className="flex-1 bg-[#0D121F] border border-gray-700 rounded-md px-3 py-2 text-xs text-gray-100 focus:outline-none focus:border-[#C5A059]"
                />
                <button
                  disabled={nlpLoading || !nlpText.trim()}
                  onClick={handleNlpParse}
                  className="px-4 py-2 bg-[#D71921] hover:bg-[#b5121a] text-white text-xs font-bold rounded-md shadow flex items-center gap-1.5 transition disabled:opacity-40"
                >
                  {nlpLoading ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5" />}
                  <span>{isRTL ? 'تحليل ومحاكاة الأثر' : 'Parse & Simulate Rule'}</span>
                </button>
              </div>

              {/* Sample Quick Prompts */}
              <div className="flex flex-wrap gap-2 pt-1">
                <span className="text-[11px] text-gray-500">{isRTL ? 'أمثلة سريعة:' : 'Quick Templates:'}</span>
                {[
                  'Flag any housing allowance exceeding 12000 AED for Grade 6 or below',
                  'Flag sick leave exceeding 3 days missing Medical_Certificate',
                  'Flag transactions where amount is greater than 35000 in Catering Services',
                  'Flag salary adjustment exceeding 20000 AED approved by Grade 8'
                ].map((sample, i) => (
                  <button
                    key={i}
                    onClick={() => setNlpText(sample)}
                    className="text-[11px] px-2 py-0.5 rounded bg-gray-800 hover:bg-gray-700 text-gray-300 border border-gray-700"
                  >
                    {sample.slice(0, 45)}...
                  </button>
                ))}
              </div>
            </div>

            {/* Simulation Results Display */}
            {nlpResult && (
              <div className="bg-[#111726] border border-gray-800 p-5 rounded-lg space-y-4 shadow">
                <div className="flex items-center justify-between border-b border-gray-800 pb-3">
                  <div>
                    <span className="text-xs font-bold text-emerald-400 uppercase tracking-wide flex items-center gap-1.5">
                      <Check className="w-4 h-4 text-emerald-400" />
                      <span>{isRTL ? 'تم بناء منطق القاعدة بنجاح' : 'Rule Compiled & Simulated Successfully'}</span>
                    </span>
                    <h3 className="text-sm font-bold text-white mt-1">{nlpResult.rule_name}</h3>
                  </div>

                  {/* Deploy Button */}
                  <button
                    disabled={nlpActivated}
                    onClick={handleActivateNlpRule}
                    className={`px-4 py-1.5 text-xs font-bold rounded-md shadow transition flex items-center gap-1.5 ${
                      nlpActivated 
                        ? 'bg-emerald-900 text-emerald-300 border border-emerald-700' 
                        : 'bg-[#C5A059] hover:bg-[#a88741] text-black'
                    }`}
                  >
                    {nlpActivated ? <Check className="w-3.5 h-3.5" /> : <ArrowUpRight className="w-3.5 h-3.5" />}
                    <span>{nlpActivated ? (isRTL ? 'تم تفعيل القاعدة في المحرك' : 'Rule Active in Engine') : (isRTL ? 'تفعيل القاعدة رسمياً' : 'Deploy Rule to Active Registry')}</span>
                  </button>
                </div>

                {/* Parsed Attributes */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                  <div className="bg-[#0D121F] p-2.5 rounded border border-gray-800">
                    <span className="text-[10px] text-gray-500 block">Target Type:</span>
                    <span className="font-semibold text-white">{nlpResult.target_type || 'Any Transaction'}</span>
                  </div>
                  <div className="bg-[#0D121F] p-2.5 rounded border border-gray-800">
                    <span className="text-[10px] text-gray-500 block">Amount Threshold:</span>
                    <span className="font-semibold text-[#C5A059]">
                      {nlpResult.amount_threshold ? `> AED ${nlpResult.amount_threshold.toLocaleString()}` : 'None'}
                    </span>
                  </div>
                  <div className="bg-[#0D121F] p-2.5 rounded border border-gray-800">
                    <span className="text-[10px] text-gray-500 block">Grade Constraint:</span>
                    <span className="font-semibold text-indigo-300">
                      {nlpResult.grade_threshold ? `<= Grade ${nlpResult.grade_threshold}` : 'None'}
                    </span>
                  </div>
                  <div className="bg-[#0D121F] p-2.5 rounded border border-gray-800">
                    <span className="text-[10px] text-gray-500 block">Simulated Impact:</span>
                    <span className="font-bold text-amber-400">
                      {nlpResult.total_matched_transactions} exceptions ({nlpResult.match_percentage}%)
                    </span>
                  </div>
                </div>

                {/* Sample Matches Preview */}
                <div>
                  <h4 className="text-xs font-semibold text-gray-400 mb-2">
                    {isRTL ? 'عينة من المعاملات التي ستخضع للمخالفة بموجب هذه القاعدة:' : 'Sample Transactions Flagged by this Dynamic Rule:'}
                  </h4>
                  <div className="overflow-x-auto border border-gray-800 rounded">
                    <table className="w-full text-xs text-left rtl:text-right">
                      <thead className="bg-[#151D2F] text-gray-400 text-[10px]">
                        <tr>
                          <th className="p-2">TXN ID</th>
                          <th className="p-2">Employee</th>
                          <th className="p-2">Department</th>
                          <th className="p-2">Type</th>
                          <th className="p-2">Amount</th>
                          <th className="p-2">Date</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-800">
                        {nlpResult.sample_matches.map(m => (
                          <tr key={m.transaction_id} className="hover:bg-gray-800/40">
                            <td className="p-2 font-mono text-gray-300">{m.transaction_id}</td>
                            <td className="p-2 font-medium text-white">{m.employee_name}</td>
                            <td className="p-2 text-gray-400">{m.department}</td>
                            <td className="p-2 text-gray-300">{m.transaction_type}</td>
                            <td className="p-2 text-[#C5A059] font-mono font-semibold">AED {Number(m.amount_aed).toLocaleString()}</td>
                            <td className="p-2 text-gray-500 font-mono">{m.submission_date}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

              </div>
            )}

          </div>
        )}

        {/* ------------------------------------------------------------- */}
        {/* TAB 4: UNSUPERVISED ANOMALY DETECTOR */}
        {/* ------------------------------------------------------------- */}
        {activeTab === 'anomalies' && (
          <div className="space-y-6">
            
            <div className="bg-[#131A2B] border border-gray-800 p-4 rounded-lg flex items-center justify-between">
              <div>
                <h2 className="text-base font-bold text-white flex items-center gap-2">
                  <Cpu className="w-4 h-4 text-cyan-400" />
                  <span>{isRTL ? 'كاشف الأنماط والسلوكيات الشاذة (تعلم غير خاضع للإشراف)' : 'Unsupervised Machine Learning Anomaly Detector'}</span>
                </h2>
                <p className="text-xs text-gray-400">
                  {isRTL ? 'رصد الثغرات والأنماط المعقدة غير المشمولة بأي قاعدة مكتوبة (خوارزمية Isolation Forest & Z-Scores)' : 'Identifies subtle emergent patterns, velocity surges, and statistical anomalies no written rule covers.'}
                </p>
              </div>
              <div className="text-xs font-semibold px-3 py-1 rounded bg-cyan-950 text-cyan-300 border border-cyan-800">
                {anomalies.length} {isRTL ? 'نمط شاذ مرصود' : 'Anomalies Isolated'}
              </div>
            </div>

            {/* Anomaly Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {anomalies.map(anm => (
                <div key={anm.anomaly_id} className="bg-[#111726] border border-gray-800 rounded-lg p-4 space-y-3 shadow flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="font-mono text-[11px] text-cyan-400 font-semibold">{anm.anomaly_id}</span>
                      <span className="text-[10px] px-2 py-0.5 rounded bg-gray-800 text-gray-300 border border-gray-700">
                        Score: {anm.anomaly_score}
                      </span>
                    </div>

                    <h3 className="text-xs font-bold text-white mb-1">{anm.pattern_type}</h3>
                    <div className="text-[11px] text-gray-400 mb-2">
                      {anm.employee_name} ({anm.employee_id}) • <span className="text-gray-300">{anm.department}</span>
                    </div>

                    <p className="text-xs text-gray-300 bg-[#0D121F] p-2.5 rounded border border-gray-800 leading-relaxed">
                      {isRTL && anm.plain_language_explanation_ar ? anm.plain_language_explanation_ar : anm.plain_language_explanation}
                    </p>
                  </div>

                  <div className="pt-2 border-t border-gray-800 text-[11px]">
                    <span className="text-gray-500 block mb-0.5">{isRTL ? 'التوصية التدقيقية:' : 'Audit Recommendation:'}</span>
                    <span className="text-indigo-300 font-medium">
                      {isRTL && anm.suggested_action_ar ? anm.suggested_action_ar : anm.suggested_action}
                    </span>
                  </div>
                </div>
              ))}
            </div>

          </div>
        )}

        {/* ------------------------------------------------------------- */}
        {/* TAB 5: FAIRNESS & EMPLOYEE EXPERIENCE */}
        {/* ------------------------------------------------------------- */}
        {activeTab === 'fairness' && fairnessData && (
          <div className="space-y-6">
            
            <div className="bg-[#131A2B] border border-gray-800 p-4 rounded-lg flex items-center justify-between">
              <div>
                <h2 className="text-base font-bold text-white flex items-center gap-2">
                  <HeartHandshake className="w-4 h-4 text-[#C5A059]" />
                  <span>{isRTL ? 'العدالة الإجرائية وتجربة الموظف وحقوق التظلم' : 'Procedural Justice, Employee Experience & Fair Notice Hub'}</span>
                </h2>
                <p className="text-xs text-gray-400">
                  {isRTL ? 'ضمان الشفافية، العدالة بين الدرجات الوظيفية، وإخطار الموظفين بأسلوب لائق غير اتهامي' : 'Ensures dignified exception communication, transparent appeal rights, and continuous adverse-impact auditing.'}
                </p>
              </div>
            </div>

            {/* Adverse Impact & Parity Across Grade Bands */}
            <div className="bg-[#111726] border border-gray-800 p-5 rounded-lg space-y-4 shadow">
              <h3 className="text-xs font-bold text-gray-200 uppercase tracking-wide flex items-center gap-1.5">
                <BarChart3 className="w-3.5 h-3.5 text-[#C5A059]" />
                <span>{isRTL ? 'تدقيق العدالة وعدم التحيز حسب الرتب الوظيفية' : 'Equity & Scrutiny Balance Across Grade Bands'}</span>
              </h3>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {fairnessData.analytics.grade_fairness.map(gb => (
                  <div key={gb.grade_band} className="bg-[#0D121F] border border-gray-800 p-3.5 rounded-lg">
                    <span className="text-[11px] font-semibold text-gray-300 block mb-1">{gb.grade_band}</span>
                    <div className="text-lg font-bold text-white mb-0.5">{gb.flag_rate_pct}%</div>
                    <span className="text-[10px] text-gray-400">
                      {gb.flagged_txns} / {gb.total_txns} {isRTL ? 'معاملة مفحوصة' : 'txns audited'}
                    </span>
                    <div className="w-full bg-gray-800 rounded-full h-1.5 mt-2">
                      <div className="bg-indigo-500 h-1.5 rounded-full" style={{ width: `${Math.min(100, gb.flag_rate_pct)}%` }}></div>
                    </div>
                  </div>
                ))}
              </div>

              <p className="text-[11px] text-gray-400 italic bg-[#070B13] p-2.5 rounded border border-gray-800">
                {isRTL
                  ? 'ملاحظة تدقيقية: تخضع المعاملات القيادية والتنفيذية (الدرجات 12+) لمعدل تدقيق صارم وفق سقوف الصلاحيات المالية (DOA) والفصل بين المهام (SoD)، بينما يتمتع موظفو الخطوط الأمامية بمستويات استقرار عالية دون انحياز سلبي.'
                  : 'Fairness Note: Executive leadership transactions undergo rigorous scrutiny for Financial Delegation (DOA) and Segregation of Duties (SoD) compliance, ensuring executive integrity without penalizing frontline operational staff.'
                }
              </p>
            </div>

            {/* Empathetic Fair Notice Preview & Dispute Filing */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              
              {/* Empathetic Fair Notice Template */}
              <div className="bg-[#111726] border border-gray-800 p-5 rounded-lg space-y-3 shadow">
                <div className="flex items-center justify-between border-b border-gray-800 pb-2">
                  <h3 className="text-xs font-bold text-white flex items-center gap-1.5">
                    <FileText className="w-4 h-4 text-[#C5A059]" />
                    <span>{isRTL ? 'نموذج إشعار الموظف الودي (Fair Notice)' : 'Empathetic "Fair Notice" Portal Communication'}</span>
                  </h3>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800">
                    Non-Accusatory Tone
                  </span>
                </div>

                <div className="bg-[#070B13] border border-gray-800 p-4 rounded-lg font-mono text-[11px] text-gray-300 whitespace-pre-line leading-relaxed max-h-[340px] overflow-y-auto">
                  {isRTL && selectedFinding ? (
                    findingDetail?.fair_notice?.notice_ar || 'اختر معاملة لمعاينة الإشعار...'
                  ) : (
                    findingDetail?.fair_notice?.notice_en || 'Select an exception from the Workbench to preview the personalized Fair Notice.'
                  )}
                </div>
              </div>

              {/* Employee Appeal & Dispute Resolution Channel */}
              <div className="bg-[#111726] border border-gray-800 p-5 rounded-lg space-y-3 shadow">
                <div className="flex items-center justify-between border-b border-gray-800 pb-2">
                  <h3 className="text-xs font-bold text-white flex items-center gap-1.5">
                    <Send className="w-4 h-4 text-indigo-400" />
                    <span>{isRTL ? 'قناة التظلم والاستيضاح الفوري للموظف' : '1-Click Employee Dispute & Clarification Channel'}</span>
                  </h3>
                  <span className="text-[10px] px-2 py-0.5 rounded bg-indigo-950 text-indigo-300 border border-indigo-800">
                    SLA: 3 Days Resolution
                  </span>
                </div>

                <div className="space-y-3 text-xs">
                  <div>
                    <label className="text-[11px] text-gray-400 block mb-1">
                      {isRTL ? 'سبب التظلم / الاستيضاح:' : 'Reason for Appeal / Clarification:'}
                    </label>
                    <input
                      type="text"
                      value={appealReason}
                      onChange={(e) => setAppealReason(e.target.value)}
                      className="w-full bg-[#0D121F] border border-gray-700 rounded p-2 text-xs text-gray-100 focus:outline-none focus:border-[#C5A059]"
                    />
                  </div>

                  <div>
                    <label className="text-[11px] text-gray-400 block mb-1">
                      {isRTL ? 'ملاحظات وتفاصيل المستندات الداعمة:' : 'Detailed Context & Attached Evidence Notes:'}
                    </label>
                    <textarea
                      rows={4}
                      value={appealNotes}
                      onChange={(e) => setAppealNotes(e.target.value)}
                      className="w-full bg-[#0D121F] border border-gray-700 rounded p-2 text-xs text-gray-100 focus:outline-none focus:border-[#C5A059]"
                    />
                  </div>

                  <button
                    disabled={!selectedFinding}
                    onClick={handleFileAppeal}
                    className="w-full py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded text-xs shadow flex items-center justify-center gap-1.5 transition disabled:opacity-40"
                  >
                    <Send className="w-3.5 h-3.5" />
                    <span>{isRTL ? 'تقديم طلب التظلم إلى لجنة الحوكمة المستقلة' : 'Submit Appeal to Independent Governance Panel'}</span>
                  </button>

                  {appealSuccess && (
                    <div className="p-2 rounded bg-emerald-950 text-emerald-300 border border-emerald-800 text-[11px] flex items-center gap-1.5">
                      <Check className="w-3.5 h-3.5" />
                      <span>{isRTL ? 'تم تسجيل التظلم بنجاح وتعيين رقم متابعة رسمي.' : 'Appeal successfully logged and assigned SLA resolution target.'}</span>
                    </div>
                  )}
                </div>
              </div>

            </div>

          </div>
        )}

      </main>

      {/* FOOTER */}
      <footer className="border-t border-gray-800 bg-[#070B13] py-4 text-xs text-gray-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-2">
          <div>
            <span>© 2026 Emirates Group Continuous HR Compliance Platform • Confidential Synthetic Demonstration</span>
          </div>
          <div className="flex items-center space-x-4 rtl:space-x-reverse text-gray-400">
            <span>Audit Trail Immutable</span>
            <span>•</span>
            <span>Zero Mutation Guarantee</span>
            <span>•</span>
            <span>UAE PDPL Compliant</span>
          </div>
        </div>
      </footer>

    </div>
  );
}
