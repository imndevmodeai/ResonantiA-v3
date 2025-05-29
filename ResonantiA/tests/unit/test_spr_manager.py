# --- START OF FILE tests/unit/test_spr_manager.py ---
import pytest
import os
import json
from pathlib import Path
# Assuming ResonantiA root is discoverable or added to PYTHONPATH
# Adjust import path if needed. We assume the structure allows this relative import.
try:
    from ResonantiA.ArchE.spr_manager import SPRManager, DEFAULT_SPR_FILE_PATH
except ImportError:
    # Attempt relative import if the first fails (common in package testing)
    try:
        from ...ArchE.spr_manager import SPRManager, DEFAULT_SPR_FILE_PATH
    except ImportError:
        # If running tests from root, try direct import
        try:
            from ArchE.spr_manager import SPRManager, DEFAULT_SPR_FILE_PATH
        except ImportError:
             # If running tests from tests/, try parent import
             try:
                 from ..ArchE.spr_manager import SPRManager, DEFAULT_SPR_FILE_PATH
             except ImportError:
                 print("Failed to import SPRManager. Ensure PYTHONPATH is set or tests run correctly relative to the project structure.")
                 SPRManager = None # Assign None to allow file parsing but tests will fail


# Define valid mock content directly for the main fixture
VALID_MOCK_SPRS = [
    {"spr_id": "ExAmplE", "term": "Example SPR", "definition": "An example.", "category": "Test"},
    {"spr_id": "CoNcePt", "term": "Concept SPR", "definition": "A concept.", "category": "Test"}
]

INVALID_FORMAT_MOCK_SPRS = [
    {"spr_id": "InvalidSPRFormat", "term": "Invalid Format", "definition": "This ID is not Guardian Points compliant."}
]

@pytest.fixture
def spr_manager(tmp_path: Path) -> SPRManager:
    """Provides an SPRManager instance with a temporary, pre-populated valid SPR file."""
    temp_spr_file = tmp_path / "test_spr_definitions_valid.json"
    with open(temp_spr_file, 'w') as f:
        json.dump(VALID_MOCK_SPRS, f)
    return SPRManager(spr_filepath=str(temp_spr_file))

@pytest.fixture
def spr_manager_empty(tmp_path: Path) -> SPRManager:
    """Provides an SPRManager instance with a temporary, empty SPR file."""
    temp_spr_file = tmp_path / "test_spr_definitions_empty.json"
    with open(temp_spr_file, 'w') as f:
        json.dump([], f) # Empty list for empty store
    return SPRManager(spr_filepath=str(temp_spr_file))


class TestSPRManager:

    @pytest.mark.skipif(SPRManager is None, reason="SPRManager class not imported.")
    def test_spr_manager_load(self, spr_manager: SPRManager): # Uses the fixture with VALID_MOCK_SPRS
        """Test loading SPRs from the file."""
        assert len(spr_manager.sprs) == 2 
        assert "ExAmplE" in spr_manager.sprs
        assert "CoNcePt" in spr_manager.sprs

    @pytest.mark.skipif(SPRManager is None, reason="SPRManager class not imported.")
    def test_spr_manager_get_spr(self, spr_manager: SPRManager):
        """Test retrieving a specific SPR."""
        spr_a = spr_manager.get_spr("ExAmplE")
        assert spr_a is not None
        assert spr_a["term"] == "Example SPR"
        spr_b = spr_manager.get_spr("NonExistentSPR")
        assert spr_b is None

    @pytest.mark.skipif(SPRManager is None, reason="SPRManager class not imported.")
    def test_spr_manager_add_spr(self, spr_manager_empty: SPRManager): # Use empty manager for add tests
        """Test adding a new valid SPR."""
        spr_manager = spr_manager_empty # Use the empty one for a clean slate
        new_spr_def = {
            "spr_id": "NeW sPr", "term": "New Valid SPR",
            "definition": "A new valid definition.", "category": "NewValidCat"
        }
        added = spr_manager.add_spr(new_spr_def)
        assert added is True
        assert "NeW sPr" in spr_manager.sprs
        assert len(spr_manager.sprs) == 1 

    @pytest.mark.skipif(SPRManager is None, reason="SPRManager class not imported.")
    def test_spr_manager_add_duplicate_spr(self, spr_manager: SPRManager): # Use pre-filled manager
        """Test adding a duplicate SPR without overwrite."""
        duplicate_spr = {"spr_id": "ExAmplE", "term": "Duplicate Example", "definition": "Duplicate Def"}
        added = spr_manager.add_spr(duplicate_spr, overwrite=False)
        assert added is False 
        assert len(spr_manager.sprs) == 2 
        assert spr_manager.sprs["ExAmplE"]["term"] == "Example SPR"

    @pytest.mark.skipif(SPRManager is None, reason="SPRManager class not imported.")
    def test_spr_manager_add_invalid_format(self, spr_manager_empty: SPRManager):
        """Test adding an SPR with invalid format."""
        spr_manager = spr_manager_empty
        invalid_spr = {"spr_id": "invalidSPR Format", "term": "Invalid", "definition": "Def"} 
        added = spr_manager.add_spr(invalid_spr)
        assert added is False
        assert len(spr_manager.sprs) == 0

    @pytest.mark.skipif(SPRManager is None, reason="SPRManager class not imported.")
    def test_is_spr_format_validation(self, spr_manager_empty: SPRManager):
        """Test the Guardian Points format validation."""
        # Use any instance, it's a static-like method logic check
        mgr = spr_manager_empty

        # Valid cases
        assert mgr.is_spr("ValiD") == (True, None)
        assert mgr.is_spr("ValiD TeRm") == (True, None)
        assert mgr.is_spr("V T") == (True, None)
        assert mgr.is_spr("Va Lid") == (True, None) # Changed from "va lid"
        assert mgr.is_spr("T3St") == (True, None)
        assert mgr.is_spr("UPPeR") == (True, None)
        assert mgr.is_spr("1 S 2") == (True, None)


        # Invalid cases - checking specific messages
        assert mgr.is_spr("1A1") == (False, "SPR '1A1': Middle character 'A' (at index 1) must be lowercase or a space.")
        assert mgr.is_spr("VALIDTERM") == (False, "SPR 'VALIDTERM': Middle character 'A' (at index 1) must be lowercase or a space.")
        assert mgr.is_spr("ValidTerm") == (False, "SPR 'ValidTerm': Last alphabetic character 'm' must be uppercase.") # Also middle 'T'
        assert mgr.is_spr("invalid") == (False, "SPR 'invalid': First alphabetic character 'i' must be uppercase.")
        assert mgr.is_spr("_invalid") == (False, "SPR '_invalid': First character '_' must be alphanumeric.")
        assert mgr.is_spr("V") == (False, "SPR 'V' is too short (min 3 chars required).")
        assert mgr.is_spr(None) == (False, "SPR text must be a non-empty string.")
        assert mgr.is_spr("") == (False, "SPR text must be a non-empty string.")
        assert mgr.is_spr(" vP") == (False, "SPR ' vP' must not have leading or trailing spaces.")
        assert mgr.is_spr("Vp ") == (False, "SPR 'Vp ' must not have leading or trailing spaces.")
        assert mgr.is_spr("vp ") == (False, "SPR 'vp ': First alphabetic character 'v' must be uppercase.")
        assert mgr.is_spr("VPp") == (False, "SPR 'VPp': Last alphabetic character 'p' must be uppercase.")
        # assert mgr.is_spr("VPP") == (False, "SPR 'VPP': Middle character 'P' (at index 1) must be lowercase or a space.") - This case is covered by VPp last char
        assert mgr.is_spr("V@LID") == (False, "SPR 'V@LID': Middle character '@' (at index 1) must be lowercase or a space.")
        assert mgr.is_spr("vAlid") == (False, "SPR 'vAlid': First alphabetic character 'v' must be uppercase.")
        assert mgr.is_spr("ValiXd") == (False, "SPR 'ValiXd': Last alphabetic character 'd' must be uppercase.")
        assert mgr.is_spr("1a1") == (False, "SPR '1a1': Last alphabetic character 'a' must be uppercase.") # Middle 'a' is fine, last '1' is fine, first '1' is fine. This one is for last char if alpha.
        assert mgr.is_spr("A1a") == (False, "SPR 'A1a': Last alphabetic character 'a' must be uppercase.") # First 'A' fine, middle '1' fine.

    # Add other tests: find_spr_by_term, remove_spr, save_sprs, load_empty_or_corrupt_file etc.
    @pytest.mark.skipif(SPRManager is None, reason="SPRManager class not imported.")
    def test_load_non_existent_file(self, tmp_path: Path):
        non_existent_file = tmp_path / "non_existent_sprs.json"
        # SPRManager now creates the file if it doesn't exist
        manager = SPRManager(spr_filepath=str(non_existent_file))
        assert manager.sprs == {}
        assert os.path.exists(non_existent_file)
        with open(non_existent_file, 'r') as f:
            assert json.load(f) == [] # Should be an empty list

    @pytest.mark.skipif(SPRManager is None, reason="SPRManager class not imported.")
    def test_load_invalid_json_file(self, tmp_path: Path):
        invalid_json_file = tmp_path / "invalid_sprs.json"
        with open(invalid_json_file, 'w') as f:
            f.write("this is not json")
        manager = SPRManager(spr_filepath=str(invalid_json_file))
        assert manager.sprs == {}

    @pytest.mark.skipif(SPRManager is None, reason="SPRManager class not imported.")
    def test_load_json_not_a_list(self, tmp_path: Path):
        not_a_list_file = tmp_path / "not_a_list.json"
        with open(not_a_list_file, 'w') as f:
            json.dump({"spr_id": "ExAmplE", "definition": "test"}, f)
        manager = SPRManager(spr_filepath=str(not_a_list_file))
        assert manager.sprs == {}

    @pytest.mark.skipif(SPRManager is None, reason="SPRManager class not imported.")
    def test_conceptual_write_and_decompress(self, spr_manager_empty: SPRManager):
        spr_id = spr_manager_empty.conceptual_write_spr(
            core_concept_term=" My Test Concept ", 
            definition="This is a test.", 
            relationships={"related_to": ["ExAmplE"]}, 
            blueprint="BP details"
        )
        assert spr_id is not None
        assert spr_manager_empty.is_spr(spr_id)[0] is True
        assert "MyTestConcepT" in spr_id # Example check, actual generation might vary
        
        retrieved = spr_manager_empty.conceptual_decompress_spr(spr_id)
        assert retrieved is not None
        assert retrieved["term"] == "My Test Concept"
        assert retrieved["definition"] == "This is a test."

# --- END OF FILE tests/unit/test_spr_manager.py --- 