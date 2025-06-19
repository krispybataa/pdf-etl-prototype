"""
    Prototype of ETL implementation for parsing application information from a PDF file. 
    Extract: Collects all available information from applicant CV 
    Transform: Parses information and stores specified sections. Also contains any normalization and cleaning of data.
    Load: Stores data in format friendly for database and website usage. 
    This is a rough prototype and is not optimized for performance and is not intended to be used in a production environment.
    It is a rough prototype that is used to test the feasibility of the idea.
    It is not intended to be used in a production environment.
    It is not intended to be used in a production environment.
"""
# Environment 
import fitz # Main import when using PyMuPDF 
import re 
import numpy as np # For defining boundaries in segregation of info 
import json # Temporary storage of structured data for auto-fill purposes 

# Core Function Definitions 

# Stage 1 - Extract Function 
def extract_into_text(doc_path):
    """
        Extracts all available information from applicant CV and stores it in a text format.
        This function is used to extract information from the CV file.
        It is not used to parse information and is not used to store information.
        It is used to extract information from the CV file.
    """
    # Load CV file 
    doc = fitz.open(doc_path)

    # Structure to store CV content 
    extracted_info = []

    # Iterate over CV file 
    for page_num in range(len(doc)):
        page = doc.load_page(page_num) # Load current page 
        text = page.get_text() # Get text from current page 
        extracted_info.append(text) # Store text from current page and update extract array 
    
    # Return complete array 
    return extracted_info

# Stage 2 - Transform Functions (Inclusive of Helper Functions )
def clean_text(raw_text):
    """
        Cleans the raw text by removing excess whitespace, but preserves newlines between sections for 
        easier segregation of information.
    """
    # Replace multiple spaces/tabs with one space, but keep newlines
    cleaned_text = re.sub(r'[ \t]+', ' ', raw_text)
    # Replace multiple newlines with a single newline
    cleaned_text = re.sub(r'\n+', '\n', cleaned_text)
    # Remove leading/trailing whitespace on each line
    cleaned_text = '\n'.join(line.strip() for line in cleaned_text.split('\n'))
    return cleaned_text.strip()

def normalize_phone_number(raw_phone):
    """
    Normalize phone numbers to the format: 999 888 7777
    - Removes country codes (+63, (63), etc.)
    - Removes dashes, parentheses, and non-digit characters
    - Removes leading zeros
    - Formats as XXX XXX XXXX if possible
    """
    if not raw_phone:
        return None

    # Remove country code patterns like +63, (63), 63-
    phone = re.sub(r'^(\+|\()?63[\)\-\s]*', '', raw_phone)
    # Remove all non-digit characters
    phone = re.sub(r'[^\d]', '', phone)
    # Remove leading zeros
    phone = phone.lstrip('0')
    # Format as XXX XXX XXXX (if 10 digits)
    if len(phone) == 10:
        return f'{phone[:3]} {phone[3:6]} {phone[6:]}'
    elif len(phone) == 11 and phone.startswith('9'):
        return f'{phone[:3]} {phone[3:7]} {phone[7:]}'
    elif len(phone) > 7:
        return f'{phone[:-7]} {phone[-7:-4]} {phone[-4:]}'
    else:
        return phone  # fallback: return as is

def remove_unicode_controls(text):
    """
    Remove common Unicode control characters (e.g., LRM, RLM, PDF direction marks) from text.
    """
    # Covers \u202a-\u202e (directional marks), \u200e, \u200f (LRM/RLM), and similar
    return re.sub(r'[\u202a-\u202e\u200e\u200f]', '', text)

def extract_applicant_information(extracted_info): 
    """
        Extracts the applicant information from the extracted information.
        This function is used to extract the applicant information from the extracted information.
        It is not used to store information and is not used to load information.
        It is used to extract the applicant information from the extracted information.
    """
    applicant_info = {} # Structure containing applicant information 

    # Remove Unicode control characters
    cleaned_info = remove_unicode_controls(extracted_info)

    # Collected Information: Extract name, email, phone, and address
    # Regex patterns for basic info (improved for robustness)
    name_pattern = r"\b([A-Z][a-zA-Z'’\-]+(?: [A-Z][a-zA-Z'’\-]+| [A-Z]\.){1,6})\b"
    email_pattern = r"\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b"
    phone_pattern = r"\b((?:\+?\d{1,3}[\s\-\.]*)?(?:\(?\d{2,4}\)?[\s\-\.]*)?\d{3,4}[\s\-\.]?\d{3,4}(?:[\s\-\.]?\d{3,4})?)\b"
    address_pattern = r"(\d{1,6}\s+[A-Za-z0-9.,'’\- ]+(?:Apt\.?|Suite|Unit)?\s*\d*\s*,?\s*[A-Za-z .'-]+,\s*[A-Za-z .'-]+(?:\s*\d{5}(?:-\d{4})?)?)"

    # Debug 
    #print(cleaned_info) # debug 
    # Using the re module to search for the patterns in the text and store all pertinent information in JSON 
    name_match = re.search(name_pattern, cleaned_info)
    applicant_info['name'] = name_match.group(1) if name_match else None

    email_match = re.search(email_pattern, cleaned_info)
    applicant_info['email'] = email_match.group(1) if email_match else None

    phone_match = re.search(phone_pattern, cleaned_info)
    raw_phone = phone_match.group(1) if phone_match else None
    applicant_info['phone'] = normalize_phone_number(raw_phone)

    address_match = re.search(address_pattern, cleaned_info)
    applicant_info['address'] = address_match.group(1) if address_match else None

    return applicant_info

def extract_work_history(cleaned_text):
    """
    Extracts the applicant work history from the cleaned text by identifying job titles, companies, and dates.
    Falls back to the original logic if no matches are found.
    """
    work_experience = []
    # Regex for "Job Title at Company Dates"
    # Accepts: "SEO Specialist at e&Co Solutions Jan 2022 - Aug 2022"
    job_pattern = re.compile(
        r"([A-Za-z][A-Za-z\s/&\-.]+?)\s+at\s+([A-Za-z0-9&.\- ]+?)\s+((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?\.?\s?\d{4}\s*[-–]\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?\.?\s?\d{4}|Present|\d{4}\s*[-–]\s*\d{4}|Present)",
        re.IGNORECASE
    )
    lines = cleaned_text.split('\n')
    for line in lines:
        match = job_pattern.search(line)
        if match:
            work_experience.append({
                'title': match.group(1).strip(),
                'company': match.group(2).strip(),
                'dates': match.group(3).strip()
            })
    # Fallback: use the original logic if nothing was found
    if not work_experience:
        # Use the original extract_work_history logic, but with cleaned_text
        work_experience = original_extract_work_history_fallback(cleaned_text)
    return work_experience

def original_extract_work_history_fallback(extracted_info):
    """
    Original work history extraction logic as a fallback.
    """
    work_experience = []

    section_headers = [
        "Work Experience", "Experience", "Professional Experience", "Employment History", "Employment", "Work"
    ]
    stop_headers = [
        "Objective", "Education", "Skills", "Projects", "Awards", "Interests", "Summary", "Competencies", "Leadership", "Activities"
    ]

    lines = extracted_info.split('\n') if '\n' in extracted_info else extracted_info.split('. ')
    start_idx = None
    for i, line in enumerate(lines):
        for header in section_headers:
            if header.lower() in line.lower():
                start_idx = i
                break
        if start_idx is not None:
            break
    if start_idx is None:
        return work_experience  # No section found

    end_idx = len(lines)
    for i in range(start_idx + 1, len(lines)):
        for stop in stop_headers:
            if stop.lower() in lines[i].lower():
                end_idx = i
                break
        if end_idx != len(lines):
            break

    section_lines = lines[start_idx+1:end_idx]

    job = {}
    job_lines = []
    date_pattern = re.compile(r'(\d{4})\s*[-–]\s*(\d{4}|Present)')
    prev_dates = None
    for line in section_lines:
        line = line.strip()
        if not line:
            continue
        date_match = date_pattern.search(line)
        if date_match:
            if job_lines:
                job_text = ' '.join(job_lines)
                parts = [p.strip() for p in re.split(r'[,-]', job_text) if p.strip()]
                if len(parts) >= 2:
                    job['position'] = parts[0]
                    job['company'] = parts[-1]
                else:
                    job['position'] = job_text
                    job['company'] = None
                job['dates'] = prev_dates if 'dates' not in job else job['dates']
                work_experience.append(job)
                job = {}
                job_lines = []
            job['dates'] = date_match.group(0)
            prev_dates = job['dates']
            line_wo_dates = date_pattern.sub('', line).strip(' ,.-')
            if line_wo_dates:
                job_lines.append(line_wo_dates)
        else:
            job_lines.append(line)
    if job_lines:
        job_text = ' '.join(job_lines)
        parts = [p.strip() for p in re.split(r'[,-]', job_text) if p.strip()]
        if len(parts) >= 2:
            job['position'] = parts[0]
            job['company'] = parts[-1]
        else:
            job['position'] = job_text
            job['company'] = None
        job['dates'] = job.get('dates', prev_dates if prev_dates is not None else None)
        work_experience.append(job)

    return work_experience

def clean_entity_unicode_and_newlines(obj):
    """
    Recursively remove unicode control characters, newlines, and non-ASCII characters from all string values in a dict/list structure.
    """
    if isinstance(obj, dict):
        return {k: clean_entity_unicode_and_newlines(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_entity_unicode_and_newlines(v) for v in obj]
    elif isinstance(obj, str):
        # Remove unicode control characters and newlines
        cleaned = remove_unicode_controls(obj)
        cleaned = cleaned.replace('\n', ' ').replace('\r', ' ')
        cleaned = re.sub(r'[\u202a-\u202e\u200e\u200f]', '', cleaned)  # extra safety
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        # Remove all non-ASCII characters
        cleaned = re.sub(r'[^\x20-\x7E]', '', cleaned)
        return cleaned
    else:
        return obj

def convert_to_text(extracted_info):
    """
        Converts the extracted information into a text format.
    """
    applicant_info = {}
    work_experience = []

    # Combine all pages into one text block for easier parsing
    full_text = " ".join(extracted_info)

    # Remove unicode control characters globally
    full_text = remove_unicode_controls(full_text)

    # Clean up the extracted text (now preserves newlines)
    cleaned_text = clean_text(full_text)
    #print(cleaned_text)

    # Extract applicant info and work experience
    applicant_info = extract_applicant_information(cleaned_text)
    work_experience = extract_work_history(cleaned_text)

    # Clean unicode and newlines from all entity fields
    result = {
        'applicant_info': applicant_info,
        'work_experience': work_experience
    }
    result = clean_entity_unicode_and_newlines(result)
    return result

# Local implemetation specifics (FILE PATHS)
test_1 = "test-cvs/test-cv.pdf" # Applicant CV 1 
test_2 = "test-cvs/test-cv-2.pdf" # Applicant CV 2 
test_3 = "test-cvs/test-cv-3.pdf" # Applicant CV 3 
test_4 = "test-cvs/test-cv-4.pdf" # Applicant CV 4 
test_5 = "test-cvs/test-cv-5.pdf" # Applicant CV 5 
test_6 = "test-cvs/test-cv-6.pdf" # Applicant CV 6 

"""
    Case 1: Applicant CV 1 
    Design: Plaintext with some formatting and atypical characters (Icons, etc.)
    Structure 
    - Applicant Information 
    - Objective Statement
    - Work Experience 
    - Education History 
    - Projects 
    - Skills and Interests 
"""
# Stage 1 - Extract Information 
case_1_extract = extract_into_text(test_1)
#print(case_1_extract) # debug 
# Stage 2 - Transform Information 
case_1_result = convert_to_text(case_1_extract)
print(json.dumps(case_1_result, indent=4))
# Stage 3 - Load/Store Information 

"""
    Case 2: Applicant CV 2
    Design: Plaintext with cosmetics (Colored Shapes, etc)
    Structure 
    - Applicant Information 
    - "Skills and Interests" 
    - Work Experience 
    - Education History 
    - Projects 
"""
# Stage 1 - Extract Information 
case_2_extract = extract_into_text(test_2)
#print(case_2_extract) # debug 
# Stage 2 - Transform Information 
case_2_result = convert_to_text(case_2_extract)
print(json.dumps(case_2_result, indent=4))
# Stage 3 - Load/Store Information 

"""
    Case 3: Applicant CV 3 
    Design: Plaintext with colored text 
    Structure 
    - Applicant Information 
    - "Professional Summary" 
    - Education History 
    - Projects 
    - Experience 
    - Awards & Recognitions 
    - Technical Skills 
    - Competencies 
"""
# Stage 1 - Extract Information 
case_3_extract = extract_into_text(test_3)

# Stage 2 - Transform Information 
case_3_result = convert_to_text(case_3_extract)
print(json.dumps(case_3_result, indent=4))
# Stage 3 - Load/Store Information 

"""
    Case 4: Applicant CV 4 
    Design: Plaintext with underlines and bold text 
    Structure 
    - Education History 
    - Leadership & Activities 
    - Projects 
    - Skills 
    - Awards 
"""
# Stage 1 - Extract Information 
case_4_extract = extract_into_text(test_4)
# Stage 2 - Transform Information 
case_4_result = convert_to_text(case_4_extract)
print(json.dumps(case_4_result, indent=4))
# Stage 3 - Load/Store Information 

""" 
    Case 5: Applicant CV 5 
    Design: Plaintext 
    Structure
    - Education 
    - Projects 
    - Leadership Experience
    - Skills & Interests 
"""
# Stage 1 - Extract Information 
case_5_extract = extract_into_text(test_5)
#print(case_5_extract) # debug 
# Stage 2 - Transform Information 
case_5_result = convert_to_text(case_5_extract)
print(json.dumps(case_5_result, indent=4))
# Stage 3 - Load/Store Information 

"""
    Case 6: Applicant CV 6
    Design: Plaintext with colored text
    Structure 
    - Education
    - Leadership and Activities 
    - Skills and Interests 
"""
# Stage 1 - Extract Information 
case_6_extract = extract_into_text(test_6)
# Stage 2 - Transform Information 
case_6_result = convert_to_text(case_6_extract)
print(json.dumps(case_6_result, indent=4))
# Stage 3 - Load/Store Information 