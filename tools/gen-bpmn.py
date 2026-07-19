#!/usr/bin/env python3
"""
Generate BPMN 2.0 XML (Camunda Zeebe) for every GovOrg in data/gov/{cc}/*.ndjson.
Output: data/gov/{cc}/bpmn/{safe-path}.bpmn

COFOG → process template mapping:
  01 / 01.6  → general-public-services  (policy, budget, coordination)
  02         → defence                  (military ops, procurement, readiness)
  03         → public-order             (law enforcement, judicial, corrections)
  04         → economic-affairs         (regulation, licensing, planning)
  04.2       → agriculture              (farming support, inspection, subsidy)
  04.5       → transport                (infrastructure, permits, safety)
  05         → environment              (permits, monitoring, enforcement)
  06         → housing                  (permits, urban planning)
  07         → health                   (policy, licensing, inspection)
  08         → recreation               (grants, facilities)
  09         → education                (curriculum, accreditation, grants)
  10         → social-protection        (welfare, pensions)
  intl       → international            (multilateral, treaty)

Run from etzhayyim-project-states/:
  python3 tools/gen-bpmn.py
"""
import json, pathlib, re, textwrap
from xml.sax.saxutils import escape as _xe  # XML-escape: & → &amp;, < → &lt;, > → &gt;

DATA = pathlib.Path("data/gov")

# ── BPMN header / footer helpers ──────────────────────────────────────────────

BPMN_NS = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <bpmn:definitions
        xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL"
        xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI"
        xmlns:dc="http://www.omg.org/spec/DD/20100524/DC"
        xmlns:di="http://www.omg.org/spec/DD/20100524/DI"
        xmlns:zeebe="http://camunda.org/schema/zeebe/1.0"
        xmlns:modeler="http://camunda.org/schema/modeler/1.0"
        id="Definitions_{pid}"
        targetNamespace="http://bpmn.io/schema/bpmn"
        exporter="Camunda Modeler" exporterVersion="5.17.0"
        modeler:executionPlatform="Camunda Cloud"
        modeler:executionPlatformVersion="8.2.0">
    """)

def _header(pid: str, org_name: str, nanoid_tag: str) -> str:
    return BPMN_NS.replace("{pid}", pid) + f"""\
  <bpmn:collaboration id="Collaboration_{pid}">
    <bpmn:participant id="Pool_{pid}" name="{_xe(org_name)} ({_xe(nanoid_tag)})" processRef="Process_{pid}" />
  </bpmn:collaboration>
"""

def _footer(pid: str) -> str:
    return f"</bpmn:definitions>\n"

# Minimal BPMNDiagram block (no layout coordinates — Camunda auto-layout on import)
def _diagram(pid: str) -> str:
    return f"""\
  <bpmndi:BPMNDiagram id="BPMNDiagram_{pid}">
    <bpmndi:BPMNPlane id="BPMNPlane_{pid}" bpmnElement="Collaboration_{pid}" />
  </bpmndi:BPMNDiagram>
"""

def _service(task_id: str, task_name: str, task_type: str,
             incoming: str, outgoing: str,
             headers: dict[str, str] | None = None) -> str:
    hdr = ""
    if headers:
        hdr_items = "\n".join(
            f'          <zeebe:header key="{k}" value="{v}" />'
            for k, v in headers.items()
        )
        hdr = f"\n        <zeebe:taskHeaders>\n{hdr_items}\n        </zeebe:taskHeaders>"
    return f"""\
    <bpmn:serviceTask id="{task_id}" name="{_xe(task_name)}">
      <bpmn:extensionElements>
        <zeebe:taskDefinition type="{task_type}" />{hdr}
      </bpmn:extensionElements>
      <bpmn:incoming>{incoming}</bpmn:incoming>
      <bpmn:outgoing>{outgoing}</bpmn:outgoing>
    </bpmn:serviceTask>
"""

def _user(task_id: str, task_name: str, incoming: str, outgoing: str,
          assignee: str = "gov-official") -> str:
    return f"""\
    <bpmn:userTask id="{task_id}" name="{_xe(task_name)}">
      <bpmn:extensionElements>
        <zeebe:assignmentDefinition assignee="{assignee}" />
      </bpmn:extensionElements>
      <bpmn:incoming>{incoming}</bpmn:incoming>
      <bpmn:outgoing>{outgoing}</bpmn:outgoing>
    </bpmn:userTask>
"""

def _exclusive(gw_id: str, gw_name: str, incoming: str, outgoings: list[str]) -> str:
    outs = "\n".join(f"      <bpmn:outgoing>{o}</bpmn:outgoing>" for o in outgoings)
    return f"""\
    <bpmn:exclusiveGateway id="{gw_id}" name="{_xe(gw_name)}" isMarkerVisible="true">
      <bpmn:incoming>{incoming}</bpmn:incoming>
{outs}
    </bpmn:exclusiveGateway>
"""

def _parallel(gw_id: str, gw_name: str, incomings: list[str], outgoings: list[str]) -> str:
    ins = "\n".join(f"      <bpmn:incoming>{i}</bpmn:incoming>" for i in incomings)
    outs = "\n".join(f"      <bpmn:outgoing>{o}</bpmn:outgoing>" for o in outgoings)
    return f"""\
    <bpmn:parallelGateway id="{gw_id}" name="{_xe(gw_name)}">
{ins}
{outs}
    </bpmn:parallelGateway>
"""

def _flow(fid: str, src: str, tgt: str, name: str = "", cond: str = "") -> str:
    name_attr = f' name="{_xe(name)}"' if name else ""
    cond_elem = f"\n      <bpmn:conditionExpression>={cond}</bpmn:conditionExpression>" if cond else ""
    return f'    <bpmn:sequenceFlow id="{fid}" sourceRef="{src}" targetRef="{tgt}"{name_attr}>{cond_elem}\n    </bpmn:sequenceFlow>\n'

def _start(eid: str, name: str, outgoing: str) -> str:
    return f'    <bpmn:startEvent id="{eid}" name="{_xe(name)}"><bpmn:outgoing>{outgoing}</bpmn:outgoing></bpmn:startEvent>\n'

def _end(eid: str, name: str, incomings: list[str]) -> str:
    ins = "\n".join(f"      <bpmn:incoming>{i}</bpmn:incoming>" for i in incomings)
    return f'    <bpmn:endEvent id="{eid}" name="{_xe(name)}">\n{ins}\n    </bpmn:endEvent>\n'

def _process_wrap(pid: str, proc_name: str, body: str) -> str:
    return f'  <bpmn:process id="Process_{pid}" name="{_xe(proc_name)}" isExecutable="true">\n{body}  </bpmn:process>\n'

# ── COFOG Process Templates ────────────────────────────────────────────────────

def bpmn_general(pid: str, org: str, cc: str, path: str) -> str:
    """COFOG 01 — General Public Services (policy, budget, coordination)."""
    p = pid
    body = (
        _start(f"Start_{p}", "Policy trigger\nreceived", f"F_{p}_01") +
        _parallel(f"GW_{p}_open", "Parallel checks", [f"F_{p}_01"],
                  [f"F_{p}_02", f"F_{p}_03", f"F_{p}_04"]) +
        _service(f"T_{p}_policy", "Draft Policy\nProposal",
                 f"gov.{cc}.{path}.draft_policy", f"F_{p}_02", f"F_{p}_05",
                 {"kpi": "policy_output", "cofog": "01"}) +
        _service(f"T_{p}_budget", "Allocate Budget\n(COFOG 01)",
                 f"gov.{cc}.{path}.allocate_budget", f"F_{p}_03", f"F_{p}_06",
                 {"kpi": "budget_execution_rate", "cofog": "01"}) +
        _service(f"T_{p}_coord", "Inter-Agency\nCoordination",
                 f"gov.{cc}.{path}.coordinate", f"F_{p}_04", f"F_{p}_07",
                 {"kpi": "coordination_score"}) +
        _parallel(f"GW_{p}_join", "Checks complete",
                  [f"F_{p}_05", f"F_{p}_06", f"F_{p}_07"], [f"F_{p}_08"]) +
        _user(f"T_{p}_review", "Minister Review\n& Sign-off", f"F_{p}_08", f"F_{p}_09") +
        _exclusive(f"GW_{p}_risk", "Approved?", f"F_{p}_09",
                   [f"F_{p}_10a", f"F_{p}_10b"]) +
        _service(f"T_{p}_publish", "Publish Policy\n& Notify Citizens",
                 f"gov.{cc}.{path}.publish_policy", f"F_{p}_10a", f"F_{p}_11",
                 {"action": "publish"}) +
        _service(f"T_{p}_revise", "Return for\nRevision",
                 f"gov.{cc}.{path}.request_revision", f"F_{p}_10b", f"F_{p}_11",
                 {"action": "revise"}) +
        _end(f"End_{p}", "Process complete", [f"F_{p}_11", f"F_{p}_11b"]) +
        _flow(f"F_{p}_01", f"Start_{p}", f"GW_{p}_open") +
        _flow(f"F_{p}_02", f"GW_{p}_open", f"T_{p}_policy") +
        _flow(f"F_{p}_03", f"GW_{p}_open", f"T_{p}_budget") +
        _flow(f"F_{p}_04", f"GW_{p}_open", f"T_{p}_coord") +
        _flow(f"F_{p}_05", f"T_{p}_policy", f"GW_{p}_join") +
        _flow(f"F_{p}_06", f"T_{p}_budget", f"GW_{p}_join") +
        _flow(f"F_{p}_07", f"T_{p}_coord", f"GW_{p}_join") +
        _flow(f"F_{p}_08", f"GW_{p}_join", f"T_{p}_review") +
        _flow(f"F_{p}_09", f"T_{p}_review", f"GW_{p}_risk") +
        _flow(f"F_{p}_10a", f"GW_{p}_risk", f"T_{p}_publish", "Approved", "approved = true") +
        _flow(f"F_{p}_10b", f"GW_{p}_risk", f"T_{p}_revise", "Rejected", "approved = false") +
        _flow(f"F_{p}_11", f"T_{p}_publish", f"End_{p}") +
        _flow(f"F_{p}_11b", f"T_{p}_revise", f"End_{p}")
    )
    return _process_wrap(p, f"{org} — General Public Services", body)

def bpmn_defence(pid: str, org: str, cc: str, path: str) -> str:
    """COFOG 02 — Defence."""
    p = pid
    body = (
        _start(f"Start_{p}", "Readiness\nassessment triggered", f"F_{p}_01") +
        _service(f"T_{p}_assess", "Assess Operational\nReadiness",
                 f"gov.{cc}.{path}.assess_readiness", f"F_{p}_01", f"F_{p}_02",
                 {"kpi": "readiness_score", "cofog": "02"}) +
        _exclusive(f"GW_{p}_ready", "Readiness level?", f"F_{p}_02",
                   [f"F_{p}_03a", f"F_{p}_03b", f"F_{p}_03c"]) +
        _service(f"T_{p}_ops", "Execute Operations\nPlan",
                 f"gov.{cc}.{path}.execute_ops", f"F_{p}_03a", f"F_{p}_04",
                 {"action": "execute", "kpi": "mission_success_rate"}) +
        _service(f"T_{p}_proc", "Initiate Procurement\n& Logistics",
                 f"gov.{cc}.{path}.procurement", f"F_{p}_03b", f"F_{p}_04",
                 {"action": "procure", "kpi": "procurement_cycle_days"}) +
        _service(f"T_{p}_alert", "Raise Alert\n& Escalate",
                 f"gov.{cc}.{path}.escalate", f"F_{p}_03c", f"F_{p}_04",
                 {"action": "escalate"}) +
        _service(f"T_{p}_report", "Submit Readiness\nReport",
                 f"gov.{cc}.{path}.submit_report", f"F_{p}_04", f"F_{p}_05") +
        _end(f"End_{p}", "Assessment complete", [f"F_{p}_05"]) +
        _flow(f"F_{p}_01", f"Start_{p}", f"T_{p}_assess") +
        _flow(f"F_{p}_02", f"T_{p}_assess", f"GW_{p}_ready") +
        _flow(f"F_{p}_03a", f"GW_{p}_ready", f"T_{p}_ops", "High", "readiness = 'high'") +
        _flow(f"F_{p}_03b", f"GW_{p}_ready", f"T_{p}_proc", "Medium", "readiness = 'medium'") +
        _flow(f"F_{p}_03c", f"GW_{p}_ready", f"T_{p}_alert", "Low", "readiness = 'low'") +
        _flow(f"F_{p}_04", f"T_{p}_ops", f"T_{p}_report") +
        _flow(f"F_{p}_04b", f"T_{p}_proc", f"T_{p}_report") +
        _flow(f"F_{p}_04c", f"T_{p}_alert", f"T_{p}_report") +
        _flow(f"F_{p}_05", f"T_{p}_report", f"End_{p}")
    )
    return _process_wrap(p, f"{org} — Defence Operations", body)

def bpmn_public_order(pid: str, org: str, cc: str, path: str) -> str:
    """COFOG 03 — Public Order & Safety."""
    p = pid
    body = (
        _start(f"Start_{p}", "Incident\nreported", f"F_{p}_01") +
        _service(f"T_{p}_triage", "Triage Incident\n(severity classification)",
                 f"gov.{cc}.{path}.triage", f"F_{p}_01", f"F_{p}_02",
                 {"kpi": "response_time_minutes", "cofog": "03"}) +
        _exclusive(f"GW_{p}_sev", "Severity?", f"F_{p}_02",
                   [f"F_{p}_03a", f"F_{p}_03b", f"F_{p}_03c"]) +
        _service(f"T_{p}_emergency", "Deploy Emergency\nResponse",
                 f"gov.{cc}.{path}.emergency_response", f"F_{p}_03a", f"F_{p}_06",
                 {"action": "emergency"}) +
        _service(f"T_{p}_investigate", "Open Investigation\n& Assign Officers",
                 f"gov.{cc}.{path}.investigate", f"F_{p}_03b", f"F_{p}_06",
                 {"action": "investigate"}) +
        _service(f"T_{p}_log", "Log Report\n& Close",
                 f"gov.{cc}.{path}.log_close", f"F_{p}_03c", f"F_{p}_06",
                 {"action": "log"}) +
        _service(f"T_{p}_report", "File Incident\nReport",
                 f"gov.{cc}.{path}.file_report", f"F_{p}_06", f"F_{p}_07") +
        _end(f"End_{p}", "Incident resolved", [f"F_{p}_07"]) +
        _flow(f"F_{p}_01", f"Start_{p}", f"T_{p}_triage") +
        _flow(f"F_{p}_02", f"T_{p}_triage", f"GW_{p}_sev") +
        _flow(f"F_{p}_03a", f"GW_{p}_sev", f"T_{p}_emergency", "Critical", "severity = 'critical'") +
        _flow(f"F_{p}_03b", f"GW_{p}_sev", f"T_{p}_investigate", "Standard", "severity = 'standard'") +
        _flow(f"F_{p}_03c", f"GW_{p}_sev", f"T_{p}_log", "Minor", "severity = 'minor'") +
        _flow(f"F_{p}_06", f"T_{p}_emergency", f"T_{p}_report") +
        _flow(f"F_{p}_06b", f"T_{p}_investigate", f"T_{p}_report") +
        _flow(f"F_{p}_06c", f"T_{p}_log", f"T_{p}_report") +
        _flow(f"F_{p}_07", f"T_{p}_report", f"End_{p}")
    )
    return _process_wrap(p, f"{org} — Public Order & Safety", body)

def bpmn_economic(pid: str, org: str, cc: str, path: str) -> str:
    """COFOG 04 — Economic Affairs (regulation, licensing)."""
    p = pid
    body = (
        _start(f"Start_{p}", "License / Permit\napplication received", f"F_{p}_01") +
        _service(f"T_{p}_screen", "Screen Application\n(completeness check)",
                 f"gov.{cc}.{path}.screen_application", f"F_{p}_01", f"F_{p}_02",
                 {"kpi": "processing_days", "cofog": "04"}) +
        _exclusive(f"GW_{p}_complete", "Complete?", f"F_{p}_02",
                   [f"F_{p}_03a", f"F_{p}_03b"]) +
        _service(f"T_{p}_return", "Return for\nAdditional Info",
                 f"gov.{cc}.{path}.return_application", f"F_{p}_03b", f"F_{p}_end1") +
        _parallel(f"GW_{p}_checks", "Parallel review",
                  [f"F_{p}_03a"], [f"F_{p}_04a", f"F_{p}_04b"]) +
        _service(f"T_{p}_legal", "Legal Compliance\nReview",
                 f"gov.{cc}.{path}.legal_review", f"F_{p}_04a", f"F_{p}_05",
                 {"kpi": "compliance_pass_rate"}) +
        _service(f"T_{p}_technical", "Technical\nAssessment",
                 f"gov.{cc}.{path}.technical_assessment", f"F_{p}_04b", f"F_{p}_05b",
                 {"kpi": "technical_score"}) +
        _parallel(f"GW_{p}_join", "Reviews complete",
                  [f"F_{p}_05", f"F_{p}_05b"], [f"F_{p}_06"]) +
        _user(f"T_{p}_decision", "Approval Decision\nby Authority", f"F_{p}_06", f"F_{p}_07") +
        _exclusive(f"GW_{p}_approve", "Decision?", f"F_{p}_07",
                   [f"F_{p}_08a", f"F_{p}_08b"]) +
        _service(f"T_{p}_issue", "Issue License\n/ Permit",
                 f"gov.{cc}.{path}.issue_license", f"F_{p}_08a", f"F_{p}_end1",
                 {"action": "issue"}) +
        _service(f"T_{p}_deny", "Send Denial\nNotice",
                 f"gov.{cc}.{path}.deny_application", f"F_{p}_08b", f"F_{p}_end1",
                 {"action": "deny"}) +
        _end(f"End_{p}", "Application\nprocessed", [f"F_{p}_end1", f"F_{p}_end1b", f"F_{p}_end1c"]) +
        _flow(f"F_{p}_01", f"Start_{p}", f"T_{p}_screen") +
        _flow(f"F_{p}_02", f"T_{p}_screen", f"GW_{p}_complete") +
        _flow(f"F_{p}_03a", f"GW_{p}_complete", f"GW_{p}_checks", "Yes", "complete = true") +
        _flow(f"F_{p}_03b", f"GW_{p}_complete", f"T_{p}_return", "No", "complete = false") +
        _flow(f"F_{p}_04a", f"GW_{p}_checks", f"T_{p}_legal") +
        _flow(f"F_{p}_04b", f"GW_{p}_checks", f"T_{p}_technical") +
        _flow(f"F_{p}_05", f"T_{p}_legal", f"GW_{p}_join") +
        _flow(f"F_{p}_05b", f"T_{p}_technical", f"GW_{p}_join") +
        _flow(f"F_{p}_06", f"GW_{p}_join", f"T_{p}_decision") +
        _flow(f"F_{p}_07", f"T_{p}_decision", f"GW_{p}_approve") +
        _flow(f"F_{p}_08a", f"GW_{p}_approve", f"T_{p}_issue", "Approved", "approved = true") +
        _flow(f"F_{p}_08b", f"GW_{p}_approve", f"T_{p}_deny", "Denied", "approved = false") +
        _flow(f"F_{p}_end1", f"T_{p}_issue", f"End_{p}") +
        _flow(f"F_{p}_end1b", f"T_{p}_deny", f"End_{p}") +
        _flow(f"F_{p}_end1c", f"T_{p}_return", f"End_{p}")
    )
    return _process_wrap(p, f"{org} — Economic Affairs / Licensing", body)

def bpmn_environment(pid: str, org: str, cc: str, path: str) -> str:
    """COFOG 05 — Environmental Protection."""
    p = pid
    body = (
        _start(f"Start_{p}", "Environmental\nmonitor triggered", f"F_{p}_01") +
        _service(f"T_{p}_monitor", "Environmental\nMonitoring & Data",
                 f"gov.{cc}.{path}.monitor", f"F_{p}_01", f"F_{p}_02",
                 {"kpi": "compliance_rate", "cofog": "05"}) +
        _exclusive(f"GW_{p}_thresh", "Threshold\nexceeded?", f"F_{p}_02",
                   [f"F_{p}_03a", f"F_{p}_03b"]) +
        _service(f"T_{p}_enforce", "Issue Enforcement\nNotice / Fine",
                 f"gov.{cc}.{path}.enforce", f"F_{p}_03a", f"F_{p}_04",
                 {"action": "enforce"}) +
        _service(f"T_{p}_log", "Log Readings\n& Archive",
                 f"gov.{cc}.{path}.log", f"F_{p}_03b", f"F_{p}_04",
                 {"action": "log"}) +
        _service(f"T_{p}_report", "Publish Environmental\nStatus Report",
                 f"gov.{cc}.{path}.publish_report", f"F_{p}_04", f"F_{p}_05") +
        _end(f"End_{p}", "Cycle complete", [f"F_{p}_05"]) +
        _flow(f"F_{p}_01", f"Start_{p}", f"T_{p}_monitor") +
        _flow(f"F_{p}_02", f"T_{p}_monitor", f"GW_{p}_thresh") +
        _flow(f"F_{p}_03a", f"GW_{p}_thresh", f"T_{p}_enforce", "Yes", "exceeded = true") +
        _flow(f"F_{p}_03b", f"GW_{p}_thresh", f"T_{p}_log", "No", "exceeded = false") +
        _flow(f"F_{p}_04", f"T_{p}_enforce", f"T_{p}_report") +
        _flow(f"F_{p}_04b", f"T_{p}_log", f"T_{p}_report") +
        _flow(f"F_{p}_05", f"T_{p}_report", f"End_{p}")
    )
    return _process_wrap(p, f"{org} — Environmental Protection", body)

def bpmn_health(pid: str, org: str, cc: str, path: str) -> str:
    """COFOG 07 — Health."""
    p = pid
    body = (
        _start(f"Start_{p}", "Health policy\ncycle initiated", f"F_{p}_01") +
        _parallel(f"GW_{p}_open", "Parallel health checks",
                  [f"F_{p}_01"], [f"F_{p}_02a", f"F_{p}_02b", f"F_{p}_02c"]) +
        _service(f"T_{p}_surveillance", "Epidemiological\nSurveillance",
                 f"gov.{cc}.{path}.surveillance", f"F_{p}_02a", f"F_{p}_03",
                 {"kpi": "disease_incidence_rate", "cofog": "07"}) +
        _service(f"T_{p}_license", "Healthcare Provider\nLicensing",
                 f"gov.{cc}.{path}.license_provider", f"F_{p}_02b", f"F_{p}_03b",
                 {"kpi": "licensed_facilities"}) +
        _service(f"T_{p}_drug", "Drug & Medical\nDevice Approval",
                 f"gov.{cc}.{path}.drug_approval", f"F_{p}_02c", f"F_{p}_03c",
                 {"kpi": "approval_cycle_days"}) +
        _parallel(f"GW_{p}_join", "Reviews complete",
                  [f"F_{p}_03", f"F_{p}_03b", f"F_{p}_03c"], [f"F_{p}_04"]) +
        _service(f"T_{p}_policy", "Update Health\nPolicy",
                 f"gov.{cc}.{path}.update_policy", f"F_{p}_04", f"F_{p}_05") +
        _end(f"End_{p}", "Health cycle complete", [f"F_{p}_05"]) +
        _flow(f"F_{p}_01", f"Start_{p}", f"GW_{p}_open") +
        _flow(f"F_{p}_02a", f"GW_{p}_open", f"T_{p}_surveillance") +
        _flow(f"F_{p}_02b", f"GW_{p}_open", f"T_{p}_license") +
        _flow(f"F_{p}_02c", f"GW_{p}_open", f"T_{p}_drug") +
        _flow(f"F_{p}_03", f"T_{p}_surveillance", f"GW_{p}_join") +
        _flow(f"F_{p}_03b", f"T_{p}_license", f"GW_{p}_join") +
        _flow(f"F_{p}_03c", f"T_{p}_drug", f"GW_{p}_join") +
        _flow(f"F_{p}_04", f"GW_{p}_join", f"T_{p}_policy") +
        _flow(f"F_{p}_05", f"T_{p}_policy", f"End_{p}")
    )
    return _process_wrap(p, f"{org} — Health Administration", body)

def bpmn_education(pid: str, org: str, cc: str, path: str) -> str:
    """COFOG 09 — Education."""
    p = pid
    body = (
        _start(f"Start_{p}", "Academic year\ncycle start", f"F_{p}_01") +
        _service(f"T_{p}_curriculum", "Review & Update\nCurriculum",
                 f"gov.{cc}.{path}.curriculum_review", f"F_{p}_01", f"F_{p}_02",
                 {"kpi": "curriculum_compliance", "cofog": "09"}) +
        _service(f"T_{p}_accredit", "Institutional\nAccreditation Review",
                 f"gov.{cc}.{path}.accreditation", f"F_{p}_02", f"F_{p}_03",
                 {"kpi": "accreditation_rate"}) +
        _service(f"T_{p}_grants", "Allocate Education\nGrants & Scholarships",
                 f"gov.{cc}.{path}.allocate_grants", f"F_{p}_03", f"F_{p}_04",
                 {"kpi": "grant_disbursement_rate"}) +
        _service(f"T_{p}_report", "Publish Education\nOutcomes Report",
                 f"gov.{cc}.{path}.publish_outcomes", f"F_{p}_04", f"F_{p}_05") +
        _end(f"End_{p}", "Academic cycle\ncomplete", [f"F_{p}_05"]) +
        _flow(f"F_{p}_01", f"Start_{p}", f"T_{p}_curriculum") +
        _flow(f"F_{p}_02", f"T_{p}_curriculum", f"T_{p}_accredit") +
        _flow(f"F_{p}_03", f"T_{p}_accredit", f"T_{p}_grants") +
        _flow(f"F_{p}_04", f"T_{p}_grants", f"T_{p}_report") +
        _flow(f"F_{p}_05", f"T_{p}_report", f"End_{p}")
    )
    return _process_wrap(p, f"{org} — Education Administration", body)

def bpmn_social(pid: str, org: str, cc: str, path: str) -> str:
    """COFOG 10 — Social Protection."""
    p = pid
    body = (
        _start(f"Start_{p}", "Benefits\napplication received", f"F_{p}_01") +
        _service(f"T_{p}_eligibility", "Determine\nEligibility",
                 f"gov.{cc}.{path}.check_eligibility", f"F_{p}_01", f"F_{p}_02",
                 {"kpi": "processing_days", "cofog": "10"}) +
        _exclusive(f"GW_{p}_elig", "Eligible?", f"F_{p}_02",
                   [f"F_{p}_03a", f"F_{p}_03b"]) +
        _service(f"T_{p}_approve", "Approve Benefits\n& Disburse",
                 f"gov.{cc}.{path}.approve_benefits", f"F_{p}_03a", f"F_{p}_04",
                 {"action": "approve", "kpi": "disbursement_rate"}) +
        _service(f"T_{p}_reject", "Issue Rejection\n& Appeals Info",
                 f"gov.{cc}.{path}.reject", f"F_{p}_03b", f"F_{p}_04",
                 {"action": "reject"}) +
        _service(f"T_{p}_report", "Case\nClosing Report",
                 f"gov.{cc}.{path}.case_report", f"F_{p}_04", f"F_{p}_05") +
        _end(f"End_{p}", "Case closed", [f"F_{p}_05"]) +
        _flow(f"F_{p}_01", f"Start_{p}", f"T_{p}_eligibility") +
        _flow(f"F_{p}_02", f"T_{p}_eligibility", f"GW_{p}_elig") +
        _flow(f"F_{p}_03a", f"GW_{p}_elig", f"T_{p}_approve", "Eligible", "eligible = true") +
        _flow(f"F_{p}_03b", f"GW_{p}_elig", f"T_{p}_reject", "Not eligible", "eligible = false") +
        _flow(f"F_{p}_04", f"T_{p}_approve", f"T_{p}_report") +
        _flow(f"F_{p}_04b", f"T_{p}_reject", f"T_{p}_report") +
        _flow(f"F_{p}_05", f"T_{p}_report", f"End_{p}")
    )
    return _process_wrap(p, f"{org} — Social Protection", body)

def bpmn_international(pid: str, org: str, cc: str, path: str) -> str:
    """intl — International Organizations."""
    p = pid
    body = (
        _start(f"Start_{p}", "Multilateral\nagenda item raised", f"F_{p}_01") +
        _service(f"T_{p}_consult", "Member State\nConsultation",
                 f"gov.{cc}.{path}.consult_members", f"F_{p}_01", f"F_{p}_02",
                 {"kpi": "member_participation_rate", "cofog": "intl"}) +
        _service(f"T_{p}_draft", "Draft Resolution\n/ Treaty Text",
                 f"gov.{cc}.{path}.draft_resolution", f"F_{p}_02", f"F_{p}_03") +
        _user(f"T_{p}_negotiate", "Negotiation\n& Amendments", f"F_{p}_03", f"F_{p}_04",
              assignee="member-state-delegates") +
        _exclusive(f"GW_{p}_consensus", "Consensus\nreached?", f"F_{p}_04",
                   [f"F_{p}_05a", f"F_{p}_05b"]) +
        _service(f"T_{p}_adopt", "Adopt Resolution\n& Notify Members",
                 f"gov.{cc}.{path}.adopt_resolution", f"F_{p}_05a", f"F_{p}_06",
                 {"action": "adopt"}) +
        _service(f"T_{p}_refer", "Refer to\nCommittee",
                 f"gov.{cc}.{path}.refer_committee", f"F_{p}_05b", f"F_{p}_06",
                 {"action": "refer"}) +
        _end(f"End_{p}", "Agenda item\nresolved", [f"F_{p}_06", f"F_{p}_06b"]) +
        _flow(f"F_{p}_01", f"Start_{p}", f"T_{p}_consult") +
        _flow(f"F_{p}_02", f"T_{p}_consult", f"T_{p}_draft") +
        _flow(f"F_{p}_03", f"T_{p}_draft", f"T_{p}_negotiate") +
        _flow(f"F_{p}_04", f"T_{p}_negotiate", f"GW_{p}_consensus") +
        _flow(f"F_{p}_05a", f"GW_{p}_consensus", f"T_{p}_adopt", "Yes", "consensus = true") +
        _flow(f"F_{p}_05b", f"GW_{p}_consensus", f"T_{p}_refer", "No", "consensus = false") +
        _flow(f"F_{p}_06", f"T_{p}_adopt", f"End_{p}") +
        _flow(f"F_{p}_06b", f"T_{p}_refer", f"End_{p}")
    )
    return _process_wrap(p, f"{org} — International Coordination", body)

# COFOG → template function
COFOG_TEMPLATE = {
    "01":   bpmn_general,
    "01.6": bpmn_general,
    "02":   bpmn_defence,
    "03":   bpmn_public_order,
    "04":   bpmn_economic,
    "04.2": bpmn_economic,
    "04.5": bpmn_economic,
    "05":   bpmn_environment,
    "06":   bpmn_economic,    # Housing ≈ Economic/Licensing
    "07":   bpmn_health,
    "08":   bpmn_education,   # Recreation ≈ Education grants
    "09":   bpmn_education,
    "10":   bpmn_social,
    "intl": bpmn_international,
}

def safe_id(path: str) -> str:
    """Convert org path to XML-safe identifier (no colons, only alnum+_)."""
    return re.sub(r"[^a-z0-9]", "_", path)

def safe_fname(path: str) -> str:
    """File-safe name for the BPMN file."""
    return re.sub(r"[^a-z0-9\-]", "-", path).strip("-") + ".bpmn"

def main() -> None:
    ndjson_files = sorted(DATA.rglob("*.ndjson"))
    created = 0
    skipped = 0

    for ndjson in ndjson_files:
        cc = ndjson.parent.name
        bpmn_dir = ndjson.parent / "bpmn"
        bpmn_dir.mkdir(exist_ok=True)

        for line in ndjson.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            path     = r.get("path", "")
            if not path:
                continue  # skip contract.ndjson and other non-org records
            org_name = r.get("nameEn") or r.get("name") or path
            cofog    = r.get("cofogCode", "01")
            nanoid   = next((t for t in r.get("tags", []) if t.startswith("nanoid:")), "")
            nanoid_tag = nanoid.replace("nanoid:", "") if nanoid else path[:8]

            pid   = safe_id(f"{cc}_{path}")
            fname = safe_fname(path)
            out   = bpmn_dir / fname

            if out.exists():
                skipped += 1
                continue

            template_fn = COFOG_TEMPLATE.get(cofog, bpmn_general)
            process_xml = template_fn(pid, org_name, cc, path)

            xml = (
                _header(pid, org_name, nanoid_tag) +
                process_xml +
                _diagram(pid) +
                _footer(pid)
            )
            out.write_text(xml, encoding="utf-8")
            created += 1

    total_bpmn = sum(1 for _ in DATA.rglob("*.bpmn"))
    print(f"Created: {created}  Skipped (existing): {skipped}")
    print(f"Total BPMN files: {total_bpmn}")

if __name__ == "__main__":
    main()
