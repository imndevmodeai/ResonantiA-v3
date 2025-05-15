# --- START OF FILE tests/unit/test_spr_manager.py ---
import pytest
import os
import json
from pathlib import Path
# Assuming ResonantiA root is discoverable or added to PYTHONPATH
# Adjust import path if needed. We assume the structure allows this relative import.
try:
    from ResonantiA.ArchE.spr_manager import SPRManager
except ImportError:
    # Attempt relative import if the first fails (common in package testing)
    try:
        from ...ArchE.spr_manager import SPRManager
    except ImportError:
        # If running tests from root, try direct import
        try:
            from ArchE.spr_manager import SPRManager
        except ImportError:
             # If running tests from tests/, try parent import
             try:
                 from ..ArchE.spr_manager import SPRManager
             except ImportError:
                 print("Failed to import SPRManager. Ensure PYTHONPATH is set or tests run correctly relative to the project structure.")
                 SPRManager = None # Assign None to allow file parsing but tests will fail


# Fixture to create a temporary SPR file for testing
@pytest.fixture
def temp_spr_file(tmp_path: Path) -> str:
    """Creates a temporary JSON file for SPR definitions."""
    spr_data = [
        {"spr_id": "TestSPaR", "term": "Test SPR A", "definition": "Def A", "category": "Test"},
        {"spr_id": "AnothEr", "term": "Test SPR B", "definition": "Def B", "category": "Test", "relationships": {"related_to": ["TestSPaR"]}}
    ]
    filepath = tmp_path / "test_sprs.json"
    with open(filepath, 'w') as f:
        json.dump(spr_data, f)
    return str(filepath)

# Fixture for SPRManager instance using the temp file
@pytest.fixture
def spr_manager(temp_spr_file: str) -> SPRManager:
    """Provides an SPRManager instance initialized with the temp file."""
    if SPRManager is None:
        pytest.skip("SPRManager class not imported.")
    return SPRManager(spr_filepath=temp_spr_file)

@pytest.mark.skipif(SPRManager is None, reason="SPRManager class not imported.")
def test_spr_manager_load(spr_manager: SPRManager):
    """Test loading SPRs from the file."""
    assert len(spr_manager.sprs) == 2
    assert "TestSPaR" in spr_manager.sprs
    assert "AnothEr" in spr_manager.sprs
    assert spr_manager.sprs["AnothEr"]["relationships"]["related_to"] == ["TestSPaR"]

@pytest.mark.skipif(SPRManager is None, reason="SPRManager class not imported.")
def test_spr_manager_get_spr(spr_manager: SPRManager):
    """Test retrieving a specific SPR."""
    spr_a = spr_manager.get_spr("TestSPaR")
    assert spr_a is not None
    assert spr_a["term"] == "Test SPR A"
    # Test getting non-existent SPR
    spr_c = spr_manager.get_spr("NonExistent")
    assert spr_c is None

@pytest.mark.skipif(SPRManager is None, reason="SPRManager class not imported.")
def test_spr_manager_add_spr(spr_manager: SPRManager, tmp_path: Path):
    """Test adding a new valid SPR."""
    new_spr_def = {
        "spr_id": "NewValidSPR", "term": "New SPR",
        "definition": "A new definition.", "category": "NewCat"
    }
    added = spr_manager.add_spr(new_spr_def)
    assert added is True
    assert len(spr_manager.sprs) == 3
    assert "NewValidSPR" in spr_manager.sprs
    # Verify it was saved to file
    reloaded_manager = SPRManager(spr_manager.filepath)
    assert len(reloaded_manager.sprs) == 3
    assert "NewValidSPR" in reloaded_manager.sprs

@pytest.mark.skipif(SPRManager is None, reason="SPRManager class not imported.")
def test_spr_manager_add_duplicate_spr(spr_manager: SPRManager):
    """Test adding a duplicate SPR without overwrite."""
    duplicate_spr = {"spr_id": "TestSPaR", "term": "Duplicate", "definition": "Duplicate Def"}
    added = spr_manager.add_spr(duplicate_spr, overwrite=False)
    assert added is False # Should fail without overwrite=True
    assert len(spr_manager.sprs) == 2 # Count should not increase
    assert spr_manager.sprs["TestSPaR"]["term"] == "Test SPR A" # Original should remain

@pytest.mark.skipif(SPRManager is None, reason="SPRManager class not imported.")
def test_spr_manager_add_invalid_format(spr_manager: SPRManager):
    """Test adding an SPR with invalid format."""
    invalid_spr = {"spr_id": "invalidSPR", "term": "Invalid", "definition": "Def"} # Missing category
    added = spr_manager.add_spr(invalid_spr)
    assert added is False
    assert len(spr_manager.sprs) == 2

@pytest.mark.skipif(SPRManager is None, reason="SPRManager class not imported.")
def test_is_spr_format_validation(spr_manager: SPRManager):
    """Test the Guardian Points format validation."""
    assert spr_manager.is_spr("ValidSPR")[0] is True
    assert spr_manager.is_spr("With SpaceS")[0] is True
    assert spr_manager.is_spr("WithNumb3rS")[0] is True
    assert spr_manager.is_spr("1StartEnD1")[0] is True
    assert spr_manager.is_spr("invalid")[0] is False # No caps
    assert spr_manager.is_spr("InvalidSPR")[0] is True # Middle caps ARE allowed now
    assert spr_manager.is_spr("VALID")[0] is False # All caps > 3 chars (common acronym)
    assert spr_manager.is_spr("VLD")[0] is True # Short all caps OK
    assert spr_manager.is_spr("")[0] is False
    assert spr_manager.is_spr("A")[0] is False
    assert spr_manager.is_spr("Ab")[0] is False # Last not alphanumeric
    assert spr_manager.is_spr("aB")[0] is False # First not alphanumeric
    assert spr_manager.is_spr(None)[0] is False

# --- END OF FILE tests/unit/test_spr_manager.py --- 