"""
Patient History Documentation and Summarization (UC-07)
Author: Sarvadnya Kamble

Aggregates longitudinal patient history, performs trend analysis,
detects data gaps, and generates comprehensive medical summaries.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import statistics

from database_config import (
    get_patient_medical_records, 
    get_patient_fhir_bundles,
    get_patient_safety_flags
)


class PatientHistoryAnalyzer:
    """
    Analyzes patient medical history across multiple records
    Generates timelines, detects trends, and identifies data gaps
    """
    
    def __init__(self, patient_id: str):
        self.patient_id = patient_id
        self.medical_records = []
        self.fhir_bundles = []
        self.timeline_events = []
        self.trends = {}
        self.data_gaps = []
        self.health_patterns = {}
        
    def aggregate_patient_data(self) -> Dict[str, Any]:
        """
        Main method: Aggregates all patient data from FHIR bundles
        """
        print(f"\n{'='*60}")
        print(f"📊 Patient History Aggregation")
        print(f"{'='*60}")
        print(f"Patient ID: {self.patient_id}")
        
        # Get medical records
        self.medical_records = get_patient_medical_records(self.patient_id)
        print(f"✓ Found {len(self.medical_records)} medical records")
        
        # Get FHIR bundles
        self.fhir_bundles = get_patient_fhir_bundles(self.patient_id)
        print(f"✓ Found {len(self.fhir_bundles)} valid FHIR bundles")
        
        if not self.fhir_bundles:
            return {
                'success': False,
                'message': 'No processed medical records found for this patient',
                'patient_id': self.patient_id
            }
        
        # Extract clinical data from FHIR bundles
        aggregated_data = self._extract_fhir_data()
        
        # Build timeline
        self.timeline_events = self._build_timeline(aggregated_data)
        print(f"✓ Built timeline with {len(self.timeline_events)} events")
        
        # Analyze trends
        self.trends = self._analyze_trends(aggregated_data)
        print(f"✓ Analyzed {len(self.trends)} clinical trends")
        
        # Detect data gaps
        self.data_gaps = self._detect_data_gaps(aggregated_data)
        print(f"✓ Detected {len(self.data_gaps)} data gaps")
        
        # Identify health patterns
        self.health_patterns = self._identify_patterns(aggregated_data)
        print(f"✓ Identified {len(self.health_patterns)} health patterns")
        
        # Generate summary
        summary = self._generate_comprehensive_summary(aggregated_data)
        
        print(f"{'='*60}\n")
        
        return {
            'success': True,
            'patient_id': self.patient_id,
            'aggregated_data': aggregated_data,
            'timeline': self.timeline_events,
            'trends': self.trends,
            'data_gaps': self.data_gaps,
            'health_patterns': self.health_patterns,
            'summary': summary,
            'total_records': len(self.medical_records),
            'date_range': self._get_date_range()
        }
    
    def _extract_fhir_data(self) -> Dict[str, List[Dict]]:
        """
        Extract clinical entities from FHIR bundles
        """
        aggregated = {
            'conditions': [],
            'medications': [],
            'observations': [],
            'procedures': [],
            'encounters': [],
            'practitioners': set(),
            'organizations': set()
        }
        
        for fhir_bundle_obj in self.fhir_bundles:
            try:
                fhir_bundle = json.loads(fhir_bundle_obj.json_data)
                
                for entry in fhir_bundle.get('entry', []):
                    resource = entry.get('resource', {})
                    resource_type = resource.get('resourceType')
                    
                    # Extract date/time for timeline
                    date = self._extract_date_from_resource(resource)
                    
                    if resource_type == 'Condition':
                        condition_data = {
                            'text': self._get_code_text(resource.get('code', {})),
                            'status': resource.get('clinicalStatus', {}).get('text', 'unknown'),
                            'date': date,
                            'onset': resource.get('onsetDateTime'),
                            'resource_id': resource.get('id'),
                            'record_id': fhir_bundle_obj.medical_record_id
                        }
                        aggregated['conditions'].append(condition_data)
                    
                    elif resource_type == 'MedicationStatement':
                        med_data = {
                            'text': self._get_code_text(resource.get('medicationCodeableConcept', {})),
                            'status': resource.get('status', 'active'),
                            'date': date,
                            'dosage': resource.get('dosage', [{}])[0].get('text') if resource.get('dosage') else None,
                            'resource_id': resource.get('id'),
                            'record_id': fhir_bundle_obj.medical_record_id
                        }
                        aggregated['medications'].append(med_data)
                    
                    elif resource_type == 'Observation':
                        obs_data = {
                            'text': self._get_code_text(resource.get('code', {})),
                            'date': date,
                            'value': self._extract_observation_value(resource),
                            'resource_id': resource.get('id'),
                            'record_id': fhir_bundle_obj.medical_record_id
                        }
                        aggregated['observations'].append(obs_data)
                    
                    elif resource_type == 'Procedure':
                        proc_data = {
                            'text': self._get_code_text(resource.get('code', {})),
                            'status': resource.get('status', 'completed'),
                            'date': date,
                            'resource_id': resource.get('id'),
                            'record_id': fhir_bundle_obj.medical_record_id
                        }
                        aggregated['procedures'].append(proc_data)
                    
                    elif resource_type == 'Encounter':
                        enc_data = {
                            'status': resource.get('status', 'finished'),
                            'class': resource.get('class', {}).get('code', 'unknown'),
                            'date': date,
                            'resource_id': resource.get('id'),
                            'record_id': fhir_bundle_obj.medical_record_id
                        }
                        aggregated['encounters'].append(enc_data)
                    
                    elif resource_type == 'Practitioner':
                        name = self._get_name(resource.get('name', []))
                        if name:
                            aggregated['practitioners'].add(name)
                    
                    elif resource_type == 'Organization':
                        org_name = resource.get('name')
                        if org_name:
                            aggregated['organizations'].add(org_name)
            
            except Exception as e:
                print(f"⚠ Error extracting FHIR data: {e}")
                continue
        
        # Convert sets to lists for JSON serialization
        aggregated['practitioners'] = list(aggregated['practitioners'])
        aggregated['organizations'] = list(aggregated['organizations'])
        
        return aggregated
    
    def _build_timeline(self, aggregated_data: Dict) -> List[Dict]:
        """
        Build chronological timeline of all medical events
        """
        timeline = []
        
        # Add conditions
        for condition in aggregated_data['conditions']:
            if condition.get('date'):
                timeline.append({
                    'date': condition['date'],
                    'type': 'condition',
                    'text': condition['text'],
                    'status': condition.get('status'),
                    'icon': 'heart-pulse',
                    'color': 'danger'
                })
        
        # Add medications
        for med in aggregated_data['medications']:
            if med.get('date'):
                timeline.append({
                    'date': med['date'],
                    'type': 'medication',
                    'text': med['text'],
                    'dosage': med.get('dosage'),
                    'icon': 'capsule',
                    'color': 'success'
                })
        
        # Add observations
        for obs in aggregated_data['observations']:
            if obs.get('date'):
                timeline.append({
                    'date': obs['date'],
                    'type': 'observation',
                    'text': obs['text'],
                    'value': obs.get('value'),
                    'icon': 'clipboard-data',
                    'color': 'info'
                })
        
        # Add procedures
        for proc in aggregated_data['procedures']:
            if proc.get('date'):
                timeline.append({
                    'date': proc['date'],
                    'type': 'procedure',
                    'text': proc['text'],
                    'icon': 'activity',
                    'color': 'warning'
                })
        
        # Sort by date (most recent first)
        timeline.sort(key=lambda x: x['date'], reverse=True)
        
        return timeline
    
    def _analyze_trends(self, aggregated_data: Dict) -> Dict[str, Any]:
        """
        Analyze medical trends and progression over time
        """
        trends = {
            'condition_progression': [],
            'medication_changes': [],
            'observation_trends': [],
            'treatment_response': 'unknown'
        }
        
        # Analyze condition progression
        conditions_by_type = defaultdict(list)
        for condition in aggregated_data['conditions']:
            conditions_by_type[condition['text']].append(condition)
        
        for condition_name, instances in conditions_by_type.items():
            if len(instances) > 1:
                trend = {
                    'condition': condition_name,
                    'first_recorded': min([c['date'] for c in instances if c.get('date')]),
                    'last_recorded': max([c['date'] for c in instances if c.get('date')]),
                    'occurrences': len(instances),
                    'status_changes': [c.get('status') for c in instances]
                }
                trends['condition_progression'].append(trend)
        
        # Analyze medication changes
        meds_by_type = defaultdict(list)
        for med in aggregated_data['medications']:
            meds_by_type[med['text']].append(med)
        
        for med_name, instances in meds_by_type.items():
            if len(instances) > 1:
                trend = {
                    'medication': med_name,
                    'start_date': min([m['date'] for m in instances if m.get('date')]),
                    'changes': len(instances),
                    'current_status': instances[-1].get('status') if instances else 'unknown'
                }
                trends['medication_changes'].append(trend)
        
        # Analyze observation trends (for numeric values)
        obs_by_type = defaultdict(list)
        for obs in aggregated_data['observations']:
            if obs.get('value') and isinstance(obs['value'], (int, float)):
                obs_by_type[obs['text']].append(obs)
        
        for obs_name, instances in obs_by_type.items():
            if len(instances) >= 2:
                values = [o['value'] for o in instances if o.get('value')]
                if values:
                    trend = {
                        'observation': obs_name,
                        'min': min(values),
                        'max': max(values),
                        'mean': statistics.mean(values),
                        'latest': values[-1],
                        'direction': 'improving' if values[-1] < values[0] else 'stable' if values[-1] == values[0] else 'declining',
                        'data_points': len(values)
                    }
                    trends['observation_trends'].append(trend)
        
        return trends
    
    def _detect_data_gaps(self, aggregated_data: Dict) -> List[Dict]:
        """
        Detect gaps and inconsistencies in medical history
        """
        gaps = []
        
        # Check for missing vital information
        if not aggregated_data['conditions']:
            gaps.append({
                'type': 'missing_conditions',
                'severity': 'medium',
                'description': 'No medical conditions recorded',
                'recommendation': 'Request patient to upload recent medical reports'
            })
        
        if not aggregated_data['medications']:
            gaps.append({
                'type': 'missing_medications',
                'severity': 'medium',
                'description': 'No medications recorded',
                'recommendation': 'Confirm if patient is currently on any medications'
            })
        
        if not aggregated_data['observations']:
            gaps.append({
                'type': 'missing_observations',
                'severity': 'low',
                'description': 'No lab results or vital signs recorded',
                'recommendation': 'Request recent lab test results'
            })
        
        # Check for time gaps in records
        if len(self.medical_records) > 1:
            dates = sorted([r.uploaded_at for r in self.medical_records if r.uploaded_at])
            if len(dates) >= 2:
                for i in range(len(dates) - 1):
                    gap_days = (dates[i+1] - dates[i]).days
                    if gap_days > 180:  # More than 6 months gap
                        gaps.append({
                            'type': 'temporal_gap',
                            'severity': 'low',
                            'description': f'{gap_days} days gap between records',
                            'date_range': f'{dates[i].strftime("%Y-%m-%d")} to {dates[i+1].strftime("%Y-%m-%d")}',
                            'recommendation': 'Check if any medical events occurred during this period'
                        })
        
        return gaps
    
    def _identify_patterns(self, aggregated_data: Dict) -> Dict[str, Any]:
        """
        Identify health patterns and progression
        """
        patterns = {
            'chronic_conditions': [],
            'recurring_medications': [],
            'concerning_trends': [],
            'improvement_indicators': []
        }
        
        # Identify chronic conditions (appearing multiple times)
        condition_counts = defaultdict(int)
        for condition in aggregated_data['conditions']:
            condition_counts[condition['text']] += 1
        
        patterns['chronic_conditions'] = [
            {'name': name, 'occurrences': count}
            for name, count in condition_counts.items()
            if count >= 2
        ]
        
        # Identify long-term medications
        med_counts = defaultdict(int)
        for med in aggregated_data['medications']:
            if med.get('status') == 'active':
                med_counts[med['text']] += 1
        
        patterns['recurring_medications'] = [
            {'name': name, 'occurrences': count}
            for name, count in med_counts.items()
            if count >= 2
        ]
        
        return patterns
    
    def _generate_comprehensive_summary(self, aggregated_data: Dict) -> str:
        """
        Generate a comprehensive medical summary
        """
        summary_parts = []
        
        # Patient overview
        summary_parts.append(f"**Patient Medical History Summary**")
        summary_parts.append(f"Patient ID: {self.patient_id}")
        summary_parts.append(f"Records Analyzed: {len(self.medical_records)}")
        summary_parts.append(f"Date Range: {self._get_date_range()}")
        summary_parts.append("")
        
        # Conditions
        if aggregated_data['conditions']:
            summary_parts.append("**Documented Conditions:**")
            unique_conditions = set([c['text'] for c in aggregated_data['conditions']])
            for condition in sorted(unique_conditions):
                summary_parts.append(f"  • {condition}")
            summary_parts.append("")
        
        # Medications
        if aggregated_data['medications']:
            summary_parts.append("**Medications:**")
            active_meds = [m for m in aggregated_data['medications'] if m.get('status') == 'active']
            unique_meds = set([m['text'] for m in active_meds])
            for med in sorted(unique_meds):
                summary_parts.append(f"  • {med}")
            summary_parts.append("")
        
        # Recent observations
        if aggregated_data['observations']:
            summary_parts.append("**Recent Observations:**")
            recent_obs = sorted(aggregated_data['observations'], 
                               key=lambda x: x.get('date', ''), 
                               reverse=True)[:5]
            for obs in recent_obs:
                value_str = f": {obs['value']}" if obs.get('value') else ""
                summary_parts.append(f"  • {obs['text']}{value_str}")
            summary_parts.append("")
        
        # Care team
        if aggregated_data['practitioners']:
            summary_parts.append("**Care Team:**")
            for practitioner in aggregated_data['practitioners']:
                summary_parts.append(f"  • {practitioner}")
            summary_parts.append("")
        
        return "\n".join(summary_parts)
    
    # Helper methods
    
    def _get_code_text(self, code_obj: Dict) -> str:
        """Extract text from FHIR CodeableConcept"""
        if code_obj.get('text'):
            return code_obj['text']
        if code_obj.get('coding') and code_obj['coding']:
            return code_obj['coding'][0].get('display', 'Unknown')
        return 'Unknown'
    
    def _get_name(self, name_list: List) -> Optional[str]:
        """Extract name from FHIR name list"""
        if name_list and len(name_list) > 0:
            name_obj = name_list[0]
            if isinstance(name_obj, dict):
                return name_obj.get('text', '')
        return None
    
    def _extract_date_from_resource(self, resource: Dict) -> Optional[str]:
        """Extract date from FHIR resource"""
        # Try common date fields
        for field in ['onsetDateTime', 'effectiveDateTime', 'performedDateTime', 'issued', 'date']:
            if resource.get(field):
                return resource[field]
        
        # Try period fields
        if resource.get('period'):
            return resource['period'].get('start') or resource['period'].get('end')
        
        return None
    
    def _extract_observation_value(self, resource: Dict) -> Any:
        """Extract value from Observation resource"""
        if resource.get('valueQuantity'):
            return resource['valueQuantity'].get('value')
        elif resource.get('valueString'):
            return resource['valueString']
        elif resource.get('valueCodeableConcept'):
            return self._get_code_text(resource['valueCodeableConcept'])
        return None
    
    def _get_date_range(self) -> str:
        """Get date range of medical records"""
        if not self.medical_records:
            return "No records"
        
        dates = [r.uploaded_at for r in self.medical_records if r.uploaded_at]
        if not dates:
            return "Unknown"
        
        earliest = min(dates).strftime("%Y-%m-%d")
        latest = max(dates).strftime("%Y-%m-%d")
        
        if earliest == latest:
            return earliest
        return f"{earliest} to {latest}"


# =====================
# Quality Assurance Functions
# =====================

def assess_data_quality(aggregated_data: Dict) -> Dict[str, Any]:
    """
    Assess overall data quality and completeness
    """
    quality_score = 0
    max_score = 0
    issues = []
    
    # Check for essential data
    if aggregated_data.get('conditions'):
        quality_score += 20
    else:
        issues.append("Missing condition data")
    max_score += 20
    
    if aggregated_data.get('medications'):
        quality_score += 20
    else:
        issues.append("Missing medication data")
    max_score += 20
    
    if aggregated_data.get('observations'):
        quality_score += 20
    else:
        issues.append("Missing observation data")
    max_score += 20
    
    if aggregated_data.get('encounters'):
        quality_score += 10
    max_score += 10
    
    if aggregated_data.get('practitioners'):
        quality_score += 15
    max_score += 15
    
    if aggregated_data.get('organizations'):
        quality_score += 15
    max_score += 15
    
    quality_percentage = (quality_score / max_score * 100) if max_score > 0 else 0
    
    return {
        'quality_score': quality_score,
        'max_score': max_score,
        'quality_percentage': round(quality_percentage, 1),
        'rating': 'Excellent' if quality_percentage >= 80 else 'Good' if quality_percentage >= 60 else 'Fair' if quality_percentage >= 40 else 'Poor',
        'issues': issues
    }

