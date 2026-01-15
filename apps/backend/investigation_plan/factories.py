"""
Investigation Plan Factories
============================

Factory functions for creating investigation plans from various inputs.
"""

from datetime import datetime
from pathlib import Path

from .enums import CaseType, InvestigationPhaseType, EvidenceType
from .phase import InvestigationPhase
from .plan import InvestigationPlan
from .step import InvestigationStep


class InvestigationPlanFactory:
    """Factory for creating investigation plans."""
    
    @staticmethod
    def create_from_case_requirements(
        case_id: str,
        case_name: str,
        case_type: CaseType,
        evidence_sources: list[dict],
        investigation_objectives: list[str],
        client: str = "",
    ) -> InvestigationPlan:
        """
        Create an investigation plan from case requirements.
        
        Args:
            case_id: Unique case identifier
            case_name: Human-readable case name
            case_type: Type of incident/investigation
            evidence_sources: List of evidence source definitions
            investigation_objectives: What the investigation should determine
            client: Client name (optional)
            
        Returns:
            InvestigationPlan with standard phases based on case type
        """
        # Create base plan
        plan = InvestigationPlan(
            case_id=case_id,
            case_name=case_name,
            case_type=case_type,
            client=client,
            evidence_sources=[e.get("name", "") for e in evidence_sources],
            investigation_objectives=investigation_objectives,
            final_deliverables=[
                "Executive Summary Report",
                "Technical Investigation Report",
                "IOC Export (JSON/CSV)",
                "Timeline Report",
                "Remediation Recommendations",
            ],
            created_at=datetime.now().isoformat(),
        )
        
        # Add standard phases based on case type
        phases = InvestigationPlanFactory._get_standard_phases(case_type, evidence_sources)
        plan.phases = phases
        
        return plan
    
    @staticmethod
    def _get_standard_phases(
        case_type: CaseType,
        evidence_sources: list[dict],
    ) -> list[InvestigationPhase]:
        """Get standard investigation phases for a case type."""
        phases = []
        
        # Phase 1: Evidence Collection & Preservation
        phase1_steps = []
        for i, source in enumerate(evidence_sources):
            phase1_steps.append(InvestigationStep(
                id=f"collect-{i+1}",
                description=f"Collect and verify {source.get('name', 'evidence')}",
                evidence_sources=[source.get("name", "")],
                analysis_tools=["sha256sum", "file", "stat"],
            ))
        
        phases.append(InvestigationPhase(
            phase=1,
            name="Evidence Collection & Preservation",
            phase_type=InvestigationPhaseType.EVIDENCE_COLLECTION,
            description="Collect, hash, and preserve all evidence sources",
            steps=phase1_steps,
            expected_outputs=["evidence_inventory.json", "chain_of_custody.log"],
        ))
        
        # Phase 2: Initial Triage
        phases.append(InvestigationPhase(
            phase=2,
            name="Initial Triage",
            phase_type=InvestigationPhaseType.ANALYSIS,
            description="Quick assessment to identify scope and severity",
            steps=[
                InvestigationStep(
                    id="triage-1",
                    description="Identify timeframe of incident",
                    evidence_sources=[e.get("name", "") for e in evidence_sources],
                ),
                InvestigationStep(
                    id="triage-2",
                    description="Identify affected systems and users",
                    depends_on=["triage-1"],
                ),
                InvestigationStep(
                    id="triage-3",
                    description="Initial IOC extraction",
                    depends_on=["triage-1"],
                ),
            ],
            depends_on=[1],
            expected_outputs=["triage_summary.md", "initial_iocs.json"],
        ))
        
        # Phase 3: Deep Analysis (varies by case type)
        analysis_steps = InvestigationPlanFactory._get_analysis_steps(case_type, evidence_sources)
        phases.append(InvestigationPhase(
            phase=3,
            name="Deep Analysis",
            phase_type=InvestigationPhaseType.ANALYSIS,
            description=f"Detailed analysis for {case_type.value} investigation",
            steps=analysis_steps,
            depends_on=[2],
            parallel_safe=True,
            expected_outputs=["analysis/findings/*.json"],
        ))
        
        # Phase 4: IOC Extraction & Enrichment
        phases.append(InvestigationPhase(
            phase=4,
            name="IOC Extraction & Enrichment",
            phase_type=InvestigationPhaseType.IOC_EXTRACTION,
            description="Extract and enrich all indicators of compromise",
            steps=[
                InvestigationStep(
                    id="ioc-1",
                    description="Extract network IOCs (IPs, domains, URLs)",
                    analysis_tools=["ioc_extractor"],
                ),
                InvestigationStep(
                    id="ioc-2",
                    description="Extract file IOCs (hashes, paths, names)",
                    analysis_tools=["ioc_extractor"],
                ),
                InvestigationStep(
                    id="ioc-3",
                    description="Extract host IOCs (registry, services, tasks)",
                    analysis_tools=["ioc_extractor"],
                ),
                InvestigationStep(
                    id="ioc-4",
                    description="Enrich IOCs with threat intelligence",
                    depends_on=["ioc-1", "ioc-2", "ioc-3"],
                    analysis_tools=["threat_intel_enricher"],
                ),
            ],
            depends_on=[3],
            expected_outputs=["analysis/iocs/extracted_iocs.json", "analysis/enrichment/threat_intel_enrichment.json"],
        ))
        
        # Phase 5: Timeline Reconstruction
        phases.append(InvestigationPhase(
            phase=5,
            name="Timeline Reconstruction",
            phase_type=InvestigationPhaseType.TIMELINE_RECONSTRUCTION,
            description="Build comprehensive attack timeline",
            steps=[
                InvestigationStep(
                    id="timeline-1",
                    description="Correlate events across evidence sources",
                    analysis_tools=["timeline_builder"],
                ),
                InvestigationStep(
                    id="timeline-2",
                    description="Map events to MITRE ATT&CK framework",
                    depends_on=["timeline-1"],
                    analysis_tools=["mitre_mapper"],
                ),
                InvestigationStep(
                    id="timeline-3",
                    description="Identify attack chain and kill chain phases",
                    depends_on=["timeline-2"],
                ),
            ],
            depends_on=[4],
            expected_outputs=["analysis/timeline/timeline.json", "analysis/timeline/timeline_report.md"],
        ))
        
        # Phase 6: Validation
        phases.append(InvestigationPhase(
            phase=6,
            name="Validation",
            phase_type=InvestigationPhaseType.VALIDATION,
            description="Validate findings and evidence integrity",
            steps=[
                InvestigationStep(
                    id="validate-1",
                    description="Verify evidence integrity (hash verification)",
                ),
                InvestigationStep(
                    id="validate-2",
                    description="Cross-reference findings across sources",
                ),
                InvestigationStep(
                    id="validate-3",
                    description="Validate IOC confidence levels",
                ),
                InvestigationStep(
                    id="validate-4",
                    description="Review chain of custody documentation",
                ),
            ],
            depends_on=[5],
            expected_outputs=["validation_report.md"],
        ))
        
        # Phase 7: Reporting
        phases.append(InvestigationPhase(
            phase=7,
            name="Reporting",
            phase_type=InvestigationPhaseType.REPORTING,
            description="Generate investigation reports",
            steps=[
                InvestigationStep(
                    id="report-1",
                    description="Generate executive summary",
                    analysis_tools=["report_generator"],
                ),
                InvestigationStep(
                    id="report-2",
                    description="Generate technical investigation report",
                    analysis_tools=["report_generator"],
                ),
                InvestigationStep(
                    id="report-3",
                    description="Export IOCs in standard formats",
                    analysis_tools=["ioc_exporter"],
                ),
                InvestigationStep(
                    id="report-4",
                    description="Generate remediation recommendations",
                    analysis_tools=["report_generator"],
                ),
            ],
            depends_on=[6],
            expected_outputs=[
                "analysis/reports/executive_summary.md",
                "analysis/reports/technical_report.md",
                "analysis/reports/ioc_export.json",
                "analysis/reports/remediation_report.md",
            ],
        ))
        
        return phases
    
    @staticmethod
    def _get_analysis_steps(
        case_type: CaseType,
        evidence_sources: list[dict],
    ) -> list[InvestigationStep]:
        """Get analysis steps based on case type."""
        steps = []
        step_num = 1
        
        # Common analysis steps
        steps.append(InvestigationStep(
            id=f"analysis-{step_num}",
            description="Analyze authentication and access logs",
        ))
        step_num += 1
        
        # Case-type specific steps
        if case_type in [CaseType.MALWARE, CaseType.RANSOMWARE]:
            steps.extend([
                InvestigationStep(
                    id=f"analysis-{step_num}",
                    description="Analyze process execution artifacts",
                ),
                InvestigationStep(
                    id=f"analysis-{step_num + 1}",
                    description="Analyze persistence mechanisms",
                ),
                InvestigationStep(
                    id=f"analysis-{step_num + 2}",
                    description="Analyze file system changes",
                ),
                InvestigationStep(
                    id=f"analysis-{step_num + 3}",
                    description="Analyze network connections and C2 traffic",
                ),
            ])
            
        elif case_type == CaseType.PHISHING:
            steps.extend([
                InvestigationStep(
                    id=f"analysis-{step_num}",
                    description="Analyze email headers and routing",
                ),
                InvestigationStep(
                    id=f"analysis-{step_num + 1}",
                    description="Analyze email attachments/links",
                ),
                InvestigationStep(
                    id=f"analysis-{step_num + 2}",
                    description="Identify affected users and actions taken",
                ),
            ])
            
        elif case_type == CaseType.DATA_BREACH:
            steps.extend([
                InvestigationStep(
                    id=f"analysis-{step_num}",
                    description="Analyze data access patterns",
                ),
                InvestigationStep(
                    id=f"analysis-{step_num + 1}",
                    description="Identify exfiltration vectors",
                ),
                InvestigationStep(
                    id=f"analysis-{step_num + 2}",
                    description="Determine scope of data exposure",
                ),
            ])
            
        elif case_type == CaseType.INSIDER_THREAT:
            steps.extend([
                InvestigationStep(
                    id=f"analysis-{step_num}",
                    description="Analyze user activity patterns",
                ),
                InvestigationStep(
                    id=f"analysis-{step_num + 1}",
                    description="Analyze file access and transfers",
                ),
                InvestigationStep(
                    id=f"analysis-{step_num + 2}",
                    description="Analyze communication patterns",
                ),
            ])
            
        elif case_type == CaseType.UNAUTHORIZED_ACCESS:
            steps.extend([
                InvestigationStep(
                    id=f"analysis-{step_num}",
                    description="Analyze authentication failures and successes",
                ),
                InvestigationStep(
                    id=f"analysis-{step_num + 1}",
                    description="Analyze privilege escalation attempts",
                ),
                InvestigationStep(
                    id=f"analysis-{step_num + 2}",
                    description="Analyze lateral movement indicators",
                ),
            ])
        
        else:
            # Generic analysis steps
            steps.extend([
                InvestigationStep(
                    id=f"analysis-{step_num}",
                    description="Analyze system and application logs",
                ),
                InvestigationStep(
                    id=f"analysis-{step_num + 1}",
                    description="Analyze network traffic patterns",
                ),
                InvestigationStep(
                    id=f"analysis-{step_num + 2}",
                    description="Analyze file system artifacts",
                ),
            ])
        
        return steps
    
    @staticmethod
    def create_triage_plan(
        case_id: str,
        case_name: str,
        evidence_sources: list[dict],
    ) -> InvestigationPlan:
        """Create a quick triage investigation plan."""
        plan = InvestigationPlan(
            case_id=case_id,
            case_name=case_name,
            case_type=CaseType.TRIAGE,
            evidence_sources=[e.get("name", "") for e in evidence_sources],
            investigation_objectives=[
                "Determine if incident is real or false positive",
                "Identify scope and severity",
                "Extract initial IOCs for blocking",
                "Recommend next steps",
            ],
            final_deliverables=[
                "Triage Summary",
                "Initial IOC List",
                "Severity Assessment",
                "Recommended Actions",
            ],
            created_at=datetime.now().isoformat(),
        )
        
        # Single triage phase
        plan.phases = [
            InvestigationPhase(
                phase=1,
                name="Rapid Triage",
                phase_type=InvestigationPhaseType.ANALYSIS,
                description="Quick assessment of incident",
                steps=[
                    InvestigationStep(
                        id="triage-1",
                        description="Review alert/incident details",
                    ),
                    InvestigationStep(
                        id="triage-2",
                        description="Quick evidence review",
                        evidence_sources=[e.get("name", "") for e in evidence_sources],
                    ),
                    InvestigationStep(
                        id="triage-3",
                        description="Extract critical IOCs",
                        depends_on=["triage-2"],
                    ),
                    InvestigationStep(
                        id="triage-4",
                        description="Assess severity and scope",
                        depends_on=["triage-2", "triage-3"],
                    ),
                    InvestigationStep(
                        id="triage-5",
                        description="Generate triage summary",
                        depends_on=["triage-4"],
                    ),
                ],
                expected_outputs=["triage_summary.md", "initial_iocs.json"],
            )
        ]
        
        return plan
