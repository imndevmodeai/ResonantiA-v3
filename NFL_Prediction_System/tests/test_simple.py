#!/usr/bin/env python3
"""
Simple test to verify pytest functionality
"""

def test_basic_math():
    """Test basic mathematical operations"""
    assert 1 + 1 == 2
    assert 2 * 3 == 6
    assert 10 / 2 == 5.0

def test_string_operations():
    """Test string operations"""
    assert "hello" + " world" == "hello world"
    assert len("test") == 4
    assert "TEST".lower() == "test"

def test_list_operations():
    """Test list operations"""
    test_list = [1, 2, 3, 4]
    assert len(test_list) == 4
    assert sum(test_list) == 10
    assert test_list[0] == 1

def test_boolean_logic():
    """Test boolean logic"""
    assert True
    assert not False
    assert True and True
    assert not (False and True)
