import google.generativeai as genai
from typing import Tuple, List
import os

def setup_gemini(api_key: str):
    """Setup Gemini API with the provided API key."""
    genai.configure(api_key=api_key)

def generate_markdown_and_summary(text: str) -> Tuple[List[str], str]:
    """
    Generate markdown sections and a summary using Gemini.
    
    Args:
        text (str): The text extracted from the PDF
        
    Returns:
        Tuple[List[str], str]: A tuple containing the markdown sections and a summary
    """
    # Initialize the model
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    # Generate markdown sections
    markdown_prompt = f"""
    Convert the following text into well-structured markdown sections.
    Identify headings and organize the content appropriately.
    Return only the markdown content, no explanations.
    
    Text:
    {text}
    """
    
    markdown_response = model.generate_content(markdown_prompt)
    markdown_sections = markdown_response.text.split('\n\n')
    
    # Generate summary
    summary_prompt = f"""
    Provide a concise summary of the following text in 10 words.
    Focus on the main points and key takeaways.
    
    Text:
    {text}
    """
    
    summary_response = model.generate_content(summary_prompt)
    summary = summary_response.text.strip()
    
    return markdown_sections, summary 