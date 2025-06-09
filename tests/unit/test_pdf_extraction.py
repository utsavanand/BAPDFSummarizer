import pytest
from services.markdown_service import extract_text_from_pdf
import os
import tempfile

def test_extract_text_from_pdf():
    # Create a simple PDF file for testing
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
        # Write a minimal valid PDF structure
        pdf_content = b'''%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> /Contents 4 0 R >>
endobj
4 0 obj
<< /Length 44 >>
stream
BT /F1 12 Tf 100 700 Td (Test PDF content) Tj ET
endstream
endobj
xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000056 00000 n
0000000111 00000 n
0000000212 00000 n
trailer
<< /Size 5 /Root 1 0 R >>
startxref
364
%%EOF'''
        temp_file.write(pdf_content)
        temp_path = temp_file.name

    try:
        # Test the extraction function
        text = extract_text_from_pdf(temp_path)
        assert isinstance(text, str)
        assert "Test PDF content" in text
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_path):
            os.unlink(temp_path)

def test_extract_text_from_nonexistent_pdf():
    with pytest.raises(FileNotFoundError):
        extract_text_from_pdf('nonexistent.pdf') 