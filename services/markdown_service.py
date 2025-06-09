import re
from typing import List
from pypdf import PdfReader

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from a PDF file."""
    text = []
    
    with open(file_path, 'rb') as file:
        pdf_reader = PdfReader(file)
        
        # Get the number of pages
        num_pages = len(pdf_reader.pages)
        
        # Extract text from each page
        for page_num in range(num_pages):
            page = pdf_reader.pages[page_num]
            text.append(page.extract_text())
    
    return "\n".join(text)

def convert_to_markdown(text: str) -> List[str]:
    """Convert PDF text into markdown sections."""
    # Split text into paragraphs
    paragraphs = re.split(r'\n\s*\n', text)
    
    markdown_sections = []
    current_section = []
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
            
        # Check if paragraph might be a heading (short text, ends with colon, or all caps)
        if (len(para) < 100 and (para.endswith(':') or para.isupper())) or \
           (len(para) < 50 and para[0].isupper()):
            # If we have content in current_section, add it as a section
            if current_section:
                markdown_sections.append('\n'.join(current_section))
                current_section = []
            # Add the heading
            current_section.append(f"## {para}\n")
        else:
            # Add paragraph to current section
            current_section.append(para)
    
    # Add the last section if it exists
    if current_section:
        markdown_sections.append('\n'.join(current_section))
    
    return markdown_sections 