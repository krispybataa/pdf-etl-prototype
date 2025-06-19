"""
    Rough prototype of script that captures employment information from a PDF file.
    This script is not optimized for performance and is not intended to be used in a production environment.
    It is a rough prototype that is used to test the feasibility of the idea.
    It is not intended to be used in a production environment.
    It is not intended to be used in a production environment.
    Revision 1: Contains an ETL process for extracting employment history from a PDF file.
    - Extracts content from PDF file and stores it for parsing 
    - Parses content and captures relevant information (Applicant Information, Employment History)
"""
# PDF Module 
import re
import numpy as np 
import fitz # Main import when using PyMuPDF 
# Create PDF reader object 
file_path = 'test-cv.pdf'
doc = fitz.open(file_path)
# Define employment dictionary 
target_text = np.array([
    "Experience",
    "Work Experience",
    "Professional Experience",
    "Work",
    "Employment",
    "Employment History",
])

# Store page of applicant's employment history 
employment_history_pages = []
succeeding_pages_count = 1 # In cases where employment history is spread across multiple pages, this is the number of pages to capture

# Bool flag for checking if currently on work experience 
is_work_experience = False
# Check no. of pages 
print(len(doc))
# Load and iterate all available pages 
for page_num in range(len(doc)):
    page = doc.load_page(page_num)
    text = page.get_text()