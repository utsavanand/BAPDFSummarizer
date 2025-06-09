import pytest
from services.markdown_service import convert_to_markdown

def test_convert_to_markdown():
    # Test text with potential headings
    test_text = """
    INTRODUCTION
    This is the introduction text.

    METHODS
    Here are the methods used.

    RESULTS
    These are the results.
    """
    
    sections = convert_to_markdown(test_text)
    
    # Check that we got a list of sections
    assert isinstance(sections, list)
    assert len(sections) > 0
    
    # Check that headings are properly formatted
    for section in sections:
        assert isinstance(section, str)
        if section.startswith('##'):
            assert ' ' in section  # Should have space after ##

def test_convert_to_markdown_empty():
    # Test with empty text
    sections = convert_to_markdown("")
    assert isinstance(sections, list)
    assert len(sections) == 0

def test_convert_to_markdown_no_headings():
    # Test with text that has no headings
    test_text = "This is a paragraph. This is another paragraph."
    sections = convert_to_markdown(test_text)
    assert isinstance(sections, list)
    assert len(sections) == 1  # Should be one section without headings 