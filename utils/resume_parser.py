"""
utils/resume_parser.py
Scans ONLY the Work Experience / Experience section of a resume
for date ranges and sums them up correctly.
"""

import re
import pdfplumber
import docx as python_docx
from datetime import datetime


# ──────────────────────────────────────────────────────────
# Text Extraction
# ──────────────────────────────────────────────────────────

def extract_text(file) -> str:
    text = ""
    try:
        if file.name.lower().endswith(".pdf"):
            with pdfplumber.open(file) as pdf:
                for page in pdf.pages:
                    content = page.extract_text()
                    if content:
                        text += content + "\n"
        elif file.name.lower().endswith(".docx"):
            document = python_docx.Document(file)
            for para in document.paragraphs:
                text += para.text + "\n"
    except Exception as e:
        text = f"[Error: {e}]"
    return text.strip()


# ──────────────────────────────────────────────────────────
# Section Isolation
# ──────────────────────────────────────────────────────────

# Headers that START the experience section
EXPERIENCE_SECTION_HEADERS = re.compile(
    r"^\s*(?:"
    r"work\s+experience|professional\s+experience|employment\s+history|"
    r"work\s+history|career\s+history|experience|internships?\s+(?:&\s+)?experience|"
    r"relevant\s+experience|industry\s+experience|job\s+experience|"
    r"positions?\s+held|employment|professional\s+background"
    r")\s*:?\s*$",
    re.IGNORECASE | re.MULTILINE,
)

# Headers that END the experience section (next major section)
NEXT_SECTION_HEADERS = re.compile(
    r"^\s*(?:"
    r"education|academic|qualification|certification|skills?|technical\s+skills?|"
    r"projects?|achievements?|awards?|publications?|languages?|interests?|"
    r"hobbies|references?|summary|objective|profile|contact|volunteer|"
    r"extracurricular|activities|honors?|courses?|training|research|"
    r"personal\s+details?|declaration"
    r")\s*:?\s*$",
    re.IGNORECASE | re.MULTILINE,
)


def _extract_experience_section(full_text: str) -> str:
    """
    Isolate text between the Experience section header
    and the next major section header.
    Returns the isolated block, or full_text as fallback.
    """
    lines = full_text.splitlines()
    start_idx = None
    end_idx   = len(lines)

    for i, line in enumerate(lines):
        stripped = line.strip()
        if start_idx is None:
            if EXPERIENCE_SECTION_HEADERS.match(stripped):
                start_idx = i + 1   # content starts after the header
        else:
            # Look for end of section
            if stripped and NEXT_SECTION_HEADERS.match(stripped):
                end_idx = i
                break

    if start_idx is not None:
        section = "\n".join(lines[start_idx:end_idx])
        return section if section.strip() else full_text

    # No header found — fall back to full text
    return full_text


# ──────────────────────────────────────────────────────────
# Date Parsing
# ──────────────────────────────────────────────────────────

MONTH_MAP = {
    "jan":1, "feb":2, "mar":3, "apr":4,  "may":5,  "jun":6,
    "jul":7, "aug":8, "sep":9, "oct":10, "nov":11, "dec":12,
    "january":1,"february":2,"march":3,"april":4,"june":6,
    "july":7,"august":8,"september":9,"october":10,"november":11,"december":12,
}


def _parse_year(s: str):
    m = re.search(r"\b(19|20)\d{2}\b", s)
    return int(m.group(0)) if m else None


def _parse_month_year(token: str):
    """
    Parse a date token like 'Jan 2020', 'March 2019', '2020',
    'Present', 'Current', 'Now'.
    Returns (year, month) or (None, None).
    """
    t = token.strip().lower()

    if any(w in t for w in ["present", "current", "now", "today", "till date", "to date"]):
        n = datetime.now()
        return n.year, n.month

    # Try month name + year
    for mname, mnum in MONTH_MAP.items():
        if mname in t:
            yr = _parse_year(t)
            if yr:
                return yr, mnum

    # Year only
    yr = _parse_year(t)
    if yr:
        return yr, 6       # assume mid-year for year-only entries
    return None, None


# ──────────────────────────────────────────────────────────
# Experience Calculation
# ──────────────────────────────────────────────────────────

# Matches:  Jan 2019 – Mar 2022  |  2018 - Present  |  June 2020 to Dec 2023
DATE_TOKEN = (
    r"(?:"
    r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
    r"Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
    r"\.?\s+\d{4}"          # Month Year
    r"|"
    r"\d{4}"                # Year only
    r"|"
    r"[Pp]resent|[Cc]urrent|[Nn]ow|[Tt]ill\s+[Dd]ate|[Tt]o\s+[Dd]ate"
    r")"
)

DATE_RANGE_RE = re.compile(
    rf"({DATE_TOKEN})"
    rf"\s*(?:[-–—]+|to|till|until)\s*"
    rf"({DATE_TOKEN})",
    re.IGNORECASE,
)


def _years_from_section_date_ranges(section_text: str) -> float:
    """Sum all date ranges found in the experience section."""
    total_months = 0
    found_any    = False

    for m in DATE_RANGE_RE.finditer(section_text):
        start_str = m.group(1)
        end_str   = m.group(2)

        sy, sm = _parse_month_year(start_str)
        ey, em = _parse_month_year(end_str)

        if sy and ey:
            months = (ey - sy) * 12 + (em - sm)
            if 0 < months < 600:      # sanity: < 50 years per job
                total_months += months
                found_any = True

    return round(total_months / 12, 1) if found_any else 0.0


def _years_from_explicit_statement(section_text: str) -> float:
    """
    Catch explicit claims like '5+ years of experience', '3 years exp'.
    Only inside the experience section or near the summary.
    """
    pattern = re.compile(
        r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)"
        r"[\s\-]*(?:of\s+)?(?:experience|exp|work)?",
        re.IGNORECASE,
    )
    vals = [float(m.group(1)) for m in pattern.finditer(section_text)]
    return max(vals, default=0.0)


def extract_experience(full_text: str) -> float:
    """
    1. Isolate the Work Experience section.
    2. Sum date ranges found only within that section.
    3. Fall back to explicit statement if no ranges found.
    4. If nothing found in section, try full-text as last resort.
    """
    section = _extract_experience_section(full_text)

    by_ranges    = _years_from_section_date_ranges(section)
    by_statement = _years_from_explicit_statement(section)

    result = max(by_ranges, by_statement)

    # Last resort: if section gave 0 try full text (handles no-section-header resumes)
    if result == 0.0 and section != full_text:
        by_ranges_full    = _years_from_section_date_ranges(full_text)
        by_statement_full = _years_from_explicit_statement(full_text)
        result = max(by_ranges_full, by_statement_full)

    return result


# ──────────────────────────────────────────────────────────
# Other Field Extractors
# ──────────────────────────────────────────────────────────

EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE_RE = re.compile(r"[\+\(]?[0-9][0-9\s\-\(\)]{7,}[0-9]")

SKILL_KEYWORDS = [
    "python","java","sql","mysql","postgresql","mongodb","excel","r",
    "tensorflow","pytorch","keras","scikit-learn","pandas","numpy",
    "matplotlib","seaborn","plotly","power bi","tableau","machine learning",
    "deep learning","nlp","computer vision","data analysis","data science",
    "statistics","aws","azure","gcp","docker","kubernetes","git","rest api",
    "flask","django","javascript","react","node.js","html","css","c++","c#",
    "hadoop","spark","kafka","airflow","snowflake","dbt","linux","bash",
    "selenium","opencv","nltk","transformers","hugging face","langchain",
]


def extract_name(text: str) -> str:
    for line in text.splitlines()[:15]:
        line = line.strip()
        words = line.split()
        if (2 <= len(words) <= 4
                and all(w.replace(".", "").replace("-", "").isalpha() for w in words)
                and not any(k in line.lower() for k in [
                    "resume", "curriculum", "vitae", "objective", "summary",
                    "email", "phone", "address", "linkedin", "github",
                    "experience", "education", "skills",
                ])):
            return line
    return "Unknown"


def extract_email(text: str) -> str:
    m = EMAIL_RE.search(text)
    return m.group(0) if m else ""


def extract_phone(text: str) -> str:
    m = PHONE_RE.search(text)
    return m.group(0).strip() if m else ""


def extract_skills(text: str) -> str:
    lower = text.lower()
    return ", ".join(s for s in SKILL_KEYWORDS if s in lower)


# ──────────────────────────────────────────────────────────
# Main Entry Point
# ──────────────────────────────────────────────────────────

def parse_resume(file) -> dict:
    text = extract_text(file)
    return {
        "text":       text,
        "name":       extract_name(text),
        "email":      extract_email(text),
        "phone":      extract_phone(text),
        "experience": extract_experience(text),
        "skills":     extract_skills(text),
    }
