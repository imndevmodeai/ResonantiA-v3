#!/usr/bin/env python3
"""
Guardian pointS Format Correction Script
ResonantiA Protocol v3.1-CA Implementation Resonance Tool

This script corrects SPR naming violations to ensure proper Guardian pointS format:
- Capitalized first alphanumeric character
- Capitalized last alphanumeric character  
- All intermediate characters lowercase (including spaces)

Maintains complete file integrity and content preservation.
"""

import json
import re
import os
import shutil
from datetime import datetime
from typing import Dict, List, Tuple, Any
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('guardian_points_correction.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class GuardianPointsCorrector:
    """
    Comprehensive Guardian pointS format correction system
    Implements Implementation resonancE through systematic SPR format alignment
    """
    
    def __init__(self):
        self.corrections_made = []
        self.files_processed = []
        self.validation_errors = []
        self.backup_dir = f"backup_guardian_correction_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Known Guardian pointS violations and their corrections
        self.known_violations = {
            "ObjectiveClarificationProtocoL": "ObjectiveclarificationprotocoL",
            "AmbiguityDetectioN": "AmbiguitydetectioN",
            "ContextualSuggestionGeneratioN": "ContextualsuggestiongeneratioN", 
            "LeadingQueryFormulationN": "LeadingqueryformulatioN",
            "PreferenceOverrideHandlinG": "PreferenceoverridehandlinG",
            "FinalizeResonantObjective": "FinalizeresonantobjectivE",
            "GeminiCodeExecutoR": "GeminicodeexecutoR",
            "GeminiFileProcessoR": "GeminifileprocessoR",
            "GroundedGeneratioN": "GroundedgeneratioN",
            "GeminiFunctionCallinG": "GeminifunctioncallinG",
            "StructuredOutputGeneratoR": "StructuredoutputgeneratoR"
        }
        
    def validate_guardian_points_format(self, spr_id: str) -> bool:
        """
        Validate if an SPR ID follows proper Guardian pointS format
        
        Args:
            spr_id: The SPR identifier to validate
            
        Returns:
            bool: True if format is correct, False otherwise
        """
        if not spr_id:
            return False
            
        # Extract alphanumeric characters
        alphanumeric_chars = re.findall(r'[a-zA-Z0-9]', spr_id)
        
        if len(alphanumeric_chars) < 2:
            return False
            
        # Check first character is uppercase
        if not alphanumeric_chars[0].isupper():
            return False
            
        # Check last character is uppercase
        if not alphanumeric_chars[-1].isupper():
            return False
            
        # Check intermediate characters are lowercase
        for char in alphanumeric_chars[1:-1]:
            if char.isupper():
                return False
                
        return True
    
    def correct_guardian_points_format(self, spr_id: str) -> str:
        """
        Correct an SPR ID to proper Guardian pointS format
        
        Args:
            spr_id: The SPR identifier to correct
            
        Returns:
            str: Corrected SPR identifier
        """
        if not spr_id:
            return spr_id
            
        # Check if it's a known violation first
        if spr_id in self.known_violations:
            return self.known_violations[spr_id]
            
        # Extract alphanumeric characters and their positions
        chars = list(spr_id)
        alphanumeric_positions = []
        
        for i, char in enumerate(chars):
            if char.isalnum():
                alphanumeric_positions.append(i)
        
        if len(alphanumeric_positions) < 2:
            return spr_id
            
        # Correct the format
        corrected_chars = chars.copy()
        
        # First alphanumeric character should be uppercase
        first_pos = alphanumeric_positions[0]
        corrected_chars[first_pos] = corrected_chars[first_pos].upper()
        
        # Last alphanumeric character should be uppercase
        last_pos = alphanumeric_positions[-1]
        corrected_chars[last_pos] = corrected_chars[last_pos].upper()
        
        # Intermediate alphanumeric characters should be lowercase
        for pos in alphanumeric_positions[1:-1]:
            corrected_chars[pos] = corrected_chars[pos].lower()
            
        return ''.join(corrected_chars)
    
    def create_backup(self, file_path: str) -> str:
        """
        Create backup of file before modification
        
        Args:
            file_path: Path to file to backup
            
        Returns:
            str: Path to backup file
        """
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
            
        backup_path = os.path.join(self.backup_dir, os.path.basename(file_path))
        shutil.copy2(file_path, backup_path)
        logger.info(f"Created backup: {backup_path}")
        return backup_path
    
    def update_spr_references(self, data: Any, old_id: str, new_id: str) -> Any:
        """
        Recursively update SPR references throughout the data structure
        
        Args:
            data: Data structure to update
            old_id: Old SPR identifier
            new_id: New SPR identifier
            
        Returns:
            Updated data structure
        """
        if isinstance(data, dict):
            updated_dict = {}
            for key, value in data.items():
                # Update key if it matches
                new_key = new_id if key == old_id else key
                # Recursively update value
                updated_dict[new_key] = self.update_spr_references(value, old_id, new_id)
            return updated_dict
        elif isinstance(data, list):
            updated_list = []
            for item in data:
                if isinstance(item, str) and item == old_id:
                    updated_list.append(new_id)
                else:
                    updated_list.append(self.update_spr_references(item, old_id, new_id))
            return updated_list
        elif isinstance(data, str):
            # Replace SPR references in text
            return data.replace(old_id, new_id)
        else:
            return data
    
    def process_spr_definitions_file(self, file_path: str) -> Dict[str, Any]:
        """
        Process a single SPR definitions file
        
        Args:
            file_path: Path to the SPR definitions file
            
        Returns:
            Dict containing processing results
        """
        logger.info(f"Processing file: {file_path}")
        
        # Create backup
        backup_path = self.create_backup(file_path)
        
        try:
            # Load JSON data
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            corrections_in_file = []
            
            # Process each SPR definition
            if 'spr_definitions' in data:
                for spr_def in data['spr_definitions']:
                    if 'spr_id' in spr_def:
                        original_id = spr_def['spr_id']
                        
                        # Check if correction is needed
                        if not self.validate_guardian_points_format(original_id):
                            corrected_id = self.correct_guardian_points_format(original_id)
                            
                            if corrected_id != original_id:
                                logger.info(f"Correcting: {original_id} -> {corrected_id}")
                                
                                # Update the SPR ID
                                spr_def['spr_id'] = corrected_id
                                
                                # Update all references throughout the entire data structure
                                data = self.update_spr_references(data, original_id, corrected_id)
                                
                                corrections_in_file.append({
                                    'original': original_id,
                                    'corrected': corrected_id,
                                    'file': file_path
                                })
                                
                                self.corrections_made.append({
                                    'original': original_id,
                                    'corrected': corrected_id,
                                    'file': file_path
                                })
            
            # Write corrected data back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Completed processing: {file_path} ({len(corrections_in_file)} corrections)")
            
            return {
                'file': file_path,
                'backup': backup_path,
                'corrections': corrections_in_file,
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
    
    def find_spr_definition_files(self, root_dir: str = '.') -> List[str]:
        """
        Find all SPR definition files in the project
        
        Args:
            root_dir: Root directory to search from
            
        Returns:
            List of file paths
        """
        spr_files = []
        
        for root, dirs, files in os.walk(root_dir):
            for file in files:
                if file == 'spr_definitions_tv.json':
                    spr_files.append(os.path.join(root, file))
        
        return spr_files
    
    def generate_correction_report(self) -> str:
        """
        Generate comprehensive correction report
        
        Returns:
            str: Formatted correction report
        """
        report = []
        report.append("=" * 80)
        report.append("GUARDIAN POINTS FORMAT CORRECTION REPORT")
        report.append("ResonantiA Protocol v3.1-CA Implementation Resonance")
        report.append("=" * 80)
        report.append(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Backup Directory: {self.backup_dir}")
        report.append("")
        
        report.append(f"FILES PROCESSED: {len(self.files_processed)}")
        for file_info in self.files_processed:
            status = "SUCCESS" if file_info['success'] else "FAILED"
            report.append(f"  [{status}] {file_info['file']}")
            if not file_info['success']:
                report.append(f"    Error: {file_info['error']}")
        
        report.append("")
        report.append(f"CORRECTIONS MADE: {len(self.corrections_made)}")
        for correction in self.corrections_made:
            report.append(f"  {correction['original']} -> {correction['corrected']}")
            report.append(f"    File: {correction['file']}")
        
        if self.validation_errors:
            report.append("")
            report.append(f"VALIDATION ERRORS: {len(self.validation_errors)}")
            for error in self.validation_errors:
                report.append(f"  {error}")
        
        report.append("")
        report.append("IMPLEMENTATION RESONANCE STATUS:")
        if self.corrections_made:
            report.append("  ✅ Guardian pointS format violations corrected")
            report.append("  ✅ 'As Above So Below' alignment restored")
            report.append("  ✅ SPR decompressoR recognition enabled")
        else:
            report.append("  ✅ No Guardian pointS violations detected")
            report.append("  ✅ Implementation resonancE maintained")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def run_correction(self, root_dir: str = '.') -> Dict[str, Any]:
        """
        Run the complete Guardian pointS correction process
        
        Args:
            root_dir: Root directory to process
            
        Returns:
            Dict containing complete results
        """
        logger.info("Starting Guardian pointS format correction process")
        
        # Find all SPR definition files
        spr_files = self.find_spr_definition_files(root_dir)
        logger.info(f"Found {len(spr_files)} SPR definition files")
        
        # Process each file
        for file_path in spr_files:
            result = self.process_spr_definitions_file(file_path)
            self.files_processed.append(result)
        
        # Generate report
        report = self.generate_correction_report()
        
        # Save report to file
        report_path = f"guardian_points_correction_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"Correction process completed. Report saved to: {report_path}")
        
        return {
            'files_processed': len(self.files_processed),
            'corrections_made': len(self.corrections_made),
            'backup_dir': self.backup_dir,
            'report_path': report_path,
            'report': report,
            'success': len([f for f in self.files_processed if f['success']]) == len(self.files_processed)
        }

def main():
    """
    Main execution function
    """
    print("Guardian pointS Format Correction Script")
    print("ResonantiA Protocol v3.1-CA Implementation Resonance Tool")
    print("=" * 60)
    
    corrector = GuardianPointsCorrector()
    results = corrector.run_correction()
    
    print("\n" + results['report'])
    
    if results['success']:
        print("\n✅ Guardian pointS correction completed successfully!")
        print(f"📁 Backups created in: {results['backup_dir']}")
        print(f"📄 Report saved to: {results['report_path']}")
    else:
        print("\n❌ Some files failed to process. Check the log for details.")
        print(f"📁 Backups available in: {results['backup_dir']}")
    
    return results

if __name__ == "__main__":
    main() 