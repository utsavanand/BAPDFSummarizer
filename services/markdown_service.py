import re
import logging
from typing import List
from pypdf import PdfReader
from pypdf.errors import PdfReadError
from services.gemini_service import generate_markdown_and_summary

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from a PDF file."""
    text = []
    
    try:
        with open(file_path, 'rb') as file:
            try:
                pdf_reader = PdfReader(file)
                
                # Get the number of pages
                num_pages = len(pdf_reader.pages)
                logger.info(f"Successfully opened PDF with {num_pages} pages")
                
                # Extract text from each page
                for page_num in range(num_pages):
                    try:
                        page = pdf_reader.pages[page_num]
                        page_text = page.extract_text()
                        if not page_text:
                            logger.warning(f"No text extracted from page {page_num + 1}")
                        text.append(page_text)
                    except Exception as e:
                        logger.error(f"Error extracting text from page {page_num + 1}: {str(e)}")
                        text.append(f"[Error extracting text from page {page_num + 1}]")
                
            except PdfReadError as e:
                logger.error(f"Failed to read PDF file: {str(e)}")
                raise PdfReadError(f"Invalid or corrupted PDF file: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error while processing PDF: {str(e)}")
                raise Exception(f"Error processing PDF: {str(e)}")
    
    except FileNotFoundError:
        logger.error(f"PDF file not found: {file_path}")
        raise FileNotFoundError(f"PDF file not found: {file_path}")
    except Exception as e:
        logger.error(f"Error opening PDF file: {str(e)}")
        raise Exception(f"Error opening PDF file: {str(e)}")
    
    if not any(text):
        logger.warning("No text was extracted from the PDF")
        return "[No text could be extracted from the PDF]"
    
    return "\n".join(text)

def convert_to_markdown(text: str) -> List[str]:
    """Convert PDF text into markdown sections using Gemini."""
    try:
        # Use Gemini to generate markdown sections
        markdown_sections, _ = generate_markdown_and_summary(text)
        logger.info(f"Successfully generated {len(markdown_sections)} markdown sections")
        return markdown_sections
    except Exception as e:
        logger.error(f"Error generating markdown with Gemini: {str(e)}")
        # Fallback to basic markdown conversion if Gemini fails
        logger.info("Falling back to basic markdown conversion")
        return basic_markdown_conversion(text)

def basic_markdown_conversion(text: str) -> List[str]:
    """Basic markdown conversion as a fallback when Gemini fails."""
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