#!/usr/bin/env python3
"""
Protocol SPR Reference Corrector
ResonantiA Protocol v3.1-CA Implementation Resonance Tool

This script updates SPR references in protocol documents to match the corrected Guardian pointS format.
Ensures complete alignment between Knowledge tapestrY and protocol documentation.
"""

import re
import os
import shutil
from datetime import datetime
from typing import Dict, List, Tuple
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('protocol_spr_correction.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProtocolSPRCorrector:
    """
    Corrects SPR references in protocol documents to match Guardian pointS format
    """
    
    def __init__(self):
        self.corrections_made = []
        self.files_processed = []
        self.backup_dir = f"backup_protocol_spr_correction_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # SPR corrections mapping (old -> new)
        self.spr_corrections = {
            "ArcheSysteM": "ArchesysteM",
            "ComparativEfluxuaLprocessinG": "ComparativefluxualprocessinG",
            "PredictivemodelinGtooL": "PredictivemodelingtooL",
            "ScenarioRealismAssessmenT": "ScenariorealismassessmenT",
            "ObjectiveClarificationProtocoL": "ObjectiveclarificationprotocoL",
            "AmbiguityDetectioN": "AmbiguitydetectioN",
            "ContextualSuggestionGeneratioN": "ContextualsuggestiongeneratioN",
            "LeadingQueryFormulationN": "LeadingqueryformulatioN",
            "PreferenceOverrideHandlinG": "PreferenceoverridehandlinG",
            "FinalizeResonantObjective": "FinalizeresonantobjectivE",
            "ResonantGratiDSouL": "ResonantgratidsouL",
            "GeminiCodeExecutoR": "GeminicodeexecutoR",
            "GeminiFileProcessoR": "GeminifileprocessoR",
            "GroundedGeneratioN": "GroundedgeneratioN",
            "GeminiFunctionCallinG": "GeminifunctioncallinG",
            "StructuredOutputGeneratoR": "StructuredoutputgeneratoR"
        }
        
    def create_backup(self, file_path: str) -> str:
        """Create backup of file before modification"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
            
        backup_path = os.path.join(self.backup_dir, os.path.basename(file_path))
        shutil.copy2(file_path, backup_path)
        logger.info(f"Created backup: {backup_path}")
        return backup_path
    
    def correct_spr_references(self, content: str) -> Tuple[str, List[Dict]]:
        """
        Correct SPR references in text content
        
        Args:
            content: Text content to process
            
        Returns:
            Tuple of (corrected_content, corrections_made)
        """
        corrected_content = content
        corrections_in_content = []
        
        for old_spr, new_spr in self.spr_corrections.items():
            # Count occurrences before replacement
            count = corrected_content.count(old_spr)
            
            if count > 0:
                # Replace all occurrences
                corrected_content = corrected_content.replace(old_spr, new_spr)
                
                corrections_in_content.append({
                    'original': old_spr,
                    'corrected': new_spr,
                    'occurrences': count
                })
                
                logger.info(f"Corrected {count} occurrences: {old_spr} -> {new_spr}")
        
        return corrected_content, corrections_in_content
    
    def process_protocol_file(self, file_path: str) -> Dict:
        """
        Process a single protocol file
        
        Args:
            file_path: Path to the protocol file
            
        Returns:
            Dict containing processing results
        """
        logger.info(f"Processing protocol file: {file_path}")
        
        # Create backup
        backup_path = self.create_backup(file_path)
        
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Correct SPR references
            corrected_content, corrections_in_file = self.correct_spr_references(original_content)
            
            # Write corrected content back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(corrected_content)
            
            # Track corrections
            for correction in corrections_in_file:
                correction['file'] = file_path
                self.corrections_made.append(correction)
            
            logger.info(f"Completed processing: {file_path} ({len(corrections_in_file)} SPR types corrected)")
            
            return {
                'file': file_path,
                'backup': backup_path,
                'corrections': corrections_in_file,
                'total_corrections': sum(c['occurrences'] for c in corrections_in_file),
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
            return {
                'file': file_path,
                'backup': backup_path,
                'error': str(e),
                'success': False
            }
    
    def find_protocol_files(self, root_dir: str = '.') -> List[str]:
        """
        Find all protocol files that need SPR reference correction
        
        Args:
            root_dir: Root directory to search from
            
        Returns:
            List of file paths
        """
        protocol_files = []
        
        # Define file patterns to search
        file_patterns = [
            'ResonantiA_Protocol_v3.0.md',
            'ResonantiA_Protocol_v3.1-CA.md',
            'CRITICAL_MANDATES.md'
        ]
        
        for root, dirs, files in os.walk(root_dir):
            for file in files:
                if any(pattern in file for pattern in file_patterns):
                    protocol_files.append(os.path.join(root, file))
        
        return protocol_files
    
    def generate_correction_report(self) -> str:
        """
        Generate comprehensive correction report
        
        Returns:
            str: Formatted correction report
        """
        report = []
        report.append("=" * 80)
        report.append("PROTOCOL SPR REFERENCE CORRECTION REPORT")
        report.append("ResonantiA Protocol v3.1-CA Implementation Resonance")
        report.append("=" * 80)
        report.append(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Backup Directory: {self.backup_dir}")
        report.append("")
        
        report.append(f"FILES PROCESSED: {len(self.files_processed)}")
        for file_info in self.files_processed:
            status = "SUCCESS" if file_info['success'] else "FAILED"
            corrections = file_info.get('total_corrections', 0)
            report.append(f"  [{status}] {file_info['file']} ({corrections} corrections)")
            if not file_info['success']:
                report.append(f"    Error: {file_info['error']}")
        
        report.append("")
        report.append("SPR CORRECTIONS SUMMARY:")
        
        # Group corrections by SPR type
        spr_summary = {}
        for correction in self.corrections_made:
            spr_key = f"{correction['original']} -> {correction['corrected']}"
            if spr_key not in spr_summary:
                spr_summary[spr_key] = {'files': [], 'total_occurrences': 0}
            spr_summary[spr_key]['files'].append(correction['file'])
            spr_summary[spr_key]['total_occurrences'] += correction['occurrences']
        
        for spr_correction, details in spr_summary.items():
            report.append(f"  {spr_correction}")
            report.append(f"    Total occurrences: {details['total_occurrences']}")
            report.append(f"    Files affected: {len(details['files'])}")
        
        report.append("")
        report.append("IMPLEMENTATION RESONANCE STATUS:")
        if self.corrections_made:
            report.append("  ✅ Protocol SPR references corrected")
            report.append("  ✅ Documentation synchronization complete")
            report.append("  ✅ 'As Above So Below' alignment restored")
        else:
            report.append("  ✅ No SPR reference corrections needed")
            report.append("  ✅ Protocol documentation already aligned")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def run_correction(self, root_dir: str = '.') -> Dict:
        """
        Run the complete protocol SPR reference correction process
        
        Args:
            root_dir: Root directory to process
            
        Returns:
            Dict containing complete results
        """
        logger.info("Starting protocol SPR reference correction process")
        
        # Find all protocol files
        protocol_files = self.find_protocol_files(root_dir)
        logger.info(f"Found {len(protocol_files)} protocol files")
        
        # Process each file
        for file_path in protocol_files:
            result = self.process_protocol_file(file_path)
            self.files_processed.append(result)
        
        # Generate report
        report = self.generate_correction_report()
        
        # Save report to file
        report_path = f"protocol_spr_correction_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"Protocol correction process completed. Report saved to: {report_path}")
        
        return {
            'files_processed': len(self.files_processed),
            'corrections_made': len(self.corrections_made),
            'total_corrections': sum(c['occurrences'] for c in self.corrections_made),
            'backup_dir': self.backup_dir,
            'report_path': report_path,
            'report': report,
            'success': len([f for f in self.files_processed if f['success']]) == len(self.files_processed)
        }

def main():
    """
    Main execution function
    """
    print("Protocol SPR Reference Correction Script")
    print("ResonantiA Protocol v3.1-CA Implementation Resonance Tool")
    print("=" * 65)
    
    corrector = ProtocolSPRCorrector()
    results = corrector.run_correction()
    
    print("\n" + results['report'])
    
    if results['success']:
        print("\n✅ Protocol SPR reference correction completed successfully!")
        print(f"📁 Backups created in: {results['backup_dir']}")
        print(f"📄 Report saved to: {results['report_path']}")
        print(f"🔧 Total corrections made: {results['total_corrections']}")
    else:
        print("\n❌ Some files failed to process. Check the log for details.")
        print(f"📁 Backups available in: {results['backup_dir']}")
    
    return results

if __name__ == "__main__":
    main() 