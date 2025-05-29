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
    {"spr_id": "KnO", "term": "Knowledge Object", "definition": "A knowledge object.", "category": "Test"},
    {"spr_id": "ExamplE", "term": "Example SPR", "definition": "An example.", "category": "Test"},
    {"spr_id": "KnowledgetapestrY", "term": "Knowledge Tapestry", "definition": "The entire tapestry.", "category": "Metaconcept"},
    {"spr_id": "Val id TaG", "term": "Valid Tag", "definition": "A valid tag with space.", "category": "Test"}
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
        assert len(spr_manager.sprs) == 4
        assert "KnO" in spr_manager.sprs
        assert "ExamplE" in spr_manager.sprs
        assert "KnowledgetapestrY" in spr_manager.sprs
        assert "Val id TaG" in spr_manager.sprs

    @pytest.mark.skipif(SPRManager is None, reason="SPRManager class not imported.")
    def test_spr_manager_get_spr(self, spr_manager: SPRManager):
        """Test retrieving a specific SPR."""
        spr_a = spr_manager.get_spr("ExamplE")
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
        duplicate_spr = {"spr_id": "KnO", "term": "Duplicate Knowledge Object", "definition": "Duplicate Def"}
        added = spr_manager.add_spr(duplicate_spr, overwrite=False)
        assert added is False 
        assert len(spr_manager.sprs) == 4
        assert spr_manager.sprs["KnO"]["term"] == "Knowledge Object"

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
        """Test the Guardian Points format validation with updated rules."""
        mgr = spr_manager_empty

        # Valid cases
        assert mgr.is_spr("ValiD")[0] is True
        assert mgr.is_spr("V T")[0] is True, "Short SPR with space should be valid if chars are correct."
        assert mgr.is_spr("KnO")[0] is True
        assert mgr.is_spr("KnowledgetapestrY")[0] is True
        assert mgr.is_spr("K Y")[0] is True, "Two letter SPR with space in middle still needs len 3"
        assert mgr.is_spr("A b C")[0] is True # Min length 3, space allowed, correct casing
        assert mgr.is_spr("AB1")[0] is True
        assert mgr.is_spr("1bA")[0] is True
        assert mgr.is_spr("A B1")[0] is True
        assert mgr.is_spr("SessiocontextcaptureE")[0] is True # Example from conversion

        # Invalid cases - Length
        assert mgr.is_spr("V")[0] is False
        assert mgr.is_spr("V")[1] == "SPR 'V' is too short (min 3 chars required)."
        assert mgr.is_spr("Va")[0] is False
        assert mgr.is_spr("Va")[1] == "SPR 'Va' is too short (min 3 chars required)."
        assert mgr.is_spr("K Y")[1] == "SPR 'K Y' is too short (min 3 chars required)." # This was True before, now len 3 fails


        # Invalid cases - First/Last char casing or type
        assert mgr.is_spr("invalid")[0] is False
        assert "First alphabetic character 'i' must be uppercase" in mgr.is_spr("invalid")[1]
        assert mgr.is_spr("_invalid")[0] is False
        assert "First character '_' must be alphanumeric" in mgr.is_spr("_invalid")[1]
        assert mgr.is_spr("va lid")[0] is False
        assert "First alphabetic character 'v' must be uppercase" in mgr.is_spr("va lid")[1]
        assert mgr.is_spr("Kno")[0] is False
        assert "Last alphabetic character 'o' must be uppercase" in mgr.is_spr("Kno")[1]
        assert mgr.is_spr("knO")[0] is False
        assert "First alphabetic character 'k' must be uppercase" in mgr.is_spr("knO")[1]
        assert mgr.is_spr("k Y")[0] is False # First char lowercase
        assert mgr.is_spr("K y")[0] is False # Last char lowercase
        assert mgr.is_spr("A b1")[0] is False # Last char is num, but b is lower, middle must be lower or space
        assert "Last alphabetic character 'b' must be uppercase" in mgr.is_spr("A b1")[1] 

        # Invalid cases - Middle char casing
        assert mgr.is_spr("ValiD TeRm")[0] is False
        assert "Middle character 'T' (at index 6) must be lowercase or a space" in mgr.is_spr("ValiD TeRm")[1]
        assert mgr.is_spr("VALIDTERM")[0] is False
        assert "Middle character 'A' (at index 2) must be lowercase or a space" in mgr.is_spr("VALIDTERM")[1]
        assert mgr.is_spr("ValidTerm")[0] is False
        assert "Middle character 'T' (at index 6) must be lowercase or a space" in mgr.is_spr("ValidTerm")[1]
        assert mgr.is_spr("KnowledgeTapestry")[0] is False
        assert "Middle character 'T' (at index 10) must be lowercase or a space" in mgr.is_spr("KnowledgeTapestry")[1]
        assert mgr.is_spr("K UppercaS E")[0] is False
        assert "Middle character 'U' (at index 2) must be lowercase or a space" in mgr.is_spr("K UppercaS E")[1]

        # Invalid cases - Leading/Trailing spaces
        assert mgr.is_spr(" Valid")[0] is False
        assert "must not have leading or trailing spaces" in mgr.is_spr(" Valid")[1]
        assert mgr.is_spr("Valid ")[0] is False
        assert "must not have leading or trailing spaces" in mgr.is_spr("Valid ")[1]

        # None or Empty
        assert mgr.is_spr(None)[0] is False
        assert mgr.is_spr("")[0] is False

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
            json.dump({"spr_id": "ExAmple", "definition": "test"}, f)
        manager = SPRManager(spr_filepath=str(not_a_list_file))
        assert manager.sprs == {}

    @pytest.mark.skipif(SPRManager is None, reason="SPRManager class not imported.")
    def test_conceptual_write_and_decompress(self, spr_manager_empty: SPRManager):
        spr_id = spr_manager_empty.conceptual_write_spr(
            core_concept_term=" My Test Concept ", 
            definition="This is a test.", 
            relationships={"related_to": ["ExamplE"]},
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