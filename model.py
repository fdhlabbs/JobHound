# model.py
import csv
import uuid
from pathlib import Path
import json
import os

from app_paths import DATA_DIR

#----------------------------------------------------------------------
# Directory and file paths
HUNT_CSV = DATA_DIR / "hunt.csv"
COMPANY_CSV = DATA_DIR / "company.csv"
REMINDER_CSV = DATA_DIR / "reminder.csv"
PROGRESS_CSV = DATA_DIR / "progress.csv"
PERSONAL_FILE = DATA_DIR / "personalDetails.json"

#----------------------------------------------------------------------
# load_hunt
HUNT_FIELDS = [
    "id",
    "jobTitle",
    "jobDescription",
    "jobSource",
    "salaryBaseMin",
    "salaryBaseMax",
    "salaryIndustryAvg",
    "salaryExpecting",
    "currency",
    "otRateRatio",
    "workArrangement",
    "hasHealthInsurance",
    "companyId",
]


def load_hunt():
    if not HUNT_CSV.exists():
        return []

    with HUNT_CSV.open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f)

        width = len(HUNT_FIELDS)
        rows = []

        for row in reader:
            # add missing columns
            if len(row) < width:
                row = row + [""] * (width - len(row))

            # trim excess columns
            elif len(row) > width:
                row = row[:width]

            rows.append(row)

    return rows

#----------------------------------------------------------------------
# load_company
COMPANY_FIELDS = [
    "id",
    "name",
    "industry",
    "description",
    "isMnc",
    "address",
    "website",
    "reputation",
    "phone",
    "email",
]


def load_company():
    if not COMPANY_CSV.exists():
        return []

    with COMPANY_CSV.open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f)

        width = len(COMPANY_FIELDS)
        rows = []

        for row in reader:
            # add missing columns
            if len(row) < width:
                row = row + [""] * (width - len(row))

            # trim excess columns
            elif len(row) > width:
                row = row[:width]

            rows.append(row)

    return rows

#----------------------------------------------------------------------
# load_reminder
REMINDER_FIELDS = [
    "id",
    "huntId",
    "dateTime",
    "status",
    "description",
]


def load_reminder():
    if not REMINDER_CSV.exists():
        return []

    with REMINDER_CSV.open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f)

        width = len(REMINDER_FIELDS)
        rows = []

        for row in reader:
            # add missing columns
            if len(row) < width:
                row = row + [""] * (width - len(row))

            # trim excess columns
            elif len(row) > width:
                row = row[:width]

            rows.append(row)

    return rows

#----------------------------------------------------------------------
# load_progress
PROGRESS_FIELDS = [
    "id",
    "huntId",
    "dateTime",
    "status",
    "description",
]


def load_progress():
    if not PROGRESS_CSV.exists():
        return []

    with PROGRESS_CSV.open(newline="", encoding="utf-8") as f:
        reader = csv.reader(f)

        width = len(PROGRESS_FIELDS)
        rows = []

        for row in reader:
            # add missing columns
            if len(row) < width:
                row = row + [""] * (width - len(row))

            # trim excess columns
            elif len(row) > width:
                row = row[:width]

            rows.append(row)

    return rows

#----------------------------------------------------------------------
# new_id
def new_id() -> str:
    """Generate a new unique ID (UUID4 hex string)."""
    return uuid.uuid4().hex

#----------------------------------------------------------------------
# save_hunt
def save_hunt(rows):
    """
    Overwrite hunt.csv with the given rows (list-of-lists).
    - Does NOT write a header row; CSV is data-only.
    - Normalizes each row length to match HUNT_FIELDS width.
    """
    DATA_DIR.mkdir(exist_ok=True)

    width = len(HUNT_FIELDS)

    with HUNT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        for row in rows:
            if len(row) < width:
                row = row + [""] * (width - len(row))
            elif len(row) > width:
                row = row[:width]

            writer.writerow(row)

#----------------------------------------------------------------------
# save_company
def save_company(rows):
    """
    Overwrite company.csv with the given rows (list-of-lists).
    - Does NOT write a header row; CSV is data-only.
    - Normalizes each row length to match COMPANY_FIELDS width.
    """
    DATA_DIR.mkdir(exist_ok=True)

    width = len(COMPANY_FIELDS)

    with COMPANY_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        for row in rows:
            if len(row) < width:
                row = row + [""] * (width - len(row))
            elif len(row) > width:
                row = row[:width]

            writer.writerow(row)

#----------------------------------------------------------------------
# save_reminder
def save_reminder(rows):
    """
    Overwrite reminder.csv with the given rows (list-of-lists).
    - Does NOT write a header row; CSV is data-only.
    - Normalizes each row length to match REMINDER_FIELDS width.
    """
    DATA_DIR.mkdir(exist_ok=True)

    width = len(REMINDER_FIELDS)

    with REMINDER_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        for row in rows:
            if len(row) < width:
                row = row + [""] * (width - len(row))
            elif len(row) > width:
                row = row[:width]

            writer.writerow(row)

#----------------------------------------------------------------------
# save_progress
def save_progress(rows):
    """
    Overwrite progress.csv with the given rows (list-of-lists).
    - Does NOT write a header row; CSV is data-only.
    - Normalizes each row length to match PROGRESS_FIELDS width.
    """
    DATA_DIR.mkdir(exist_ok=True)

    width = len(PROGRESS_FIELDS)

    with PROGRESS_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        for row in rows:
            if len(row) < width:
                row = row + [""] * (width - len(row))
            elif len(row) > width:
                row = row[:width]

            writer.writerow(row)

#----------------------------------------------------------------------
# personal details JSON
def _default_personal_details():
    return {
        "name": "",
        "email": "",
        "linkedinId": "",
        "githubAcc": "",
        "phone": "",
        "address": "",
        "about": "",
        "education": [
            {"education": "", "almamater": "", "description": ""}
        ],
        "work": [
            {"position": "", "company": "", "description": ""}
        ],
        "skills": [
            {"skill": "", "description": ""}
        ],
    }


def load_personal_details():
    if not os.path.exists(PERSONAL_FILE):
        return _default_personal_details()

    try:
        with open(PERSONAL_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return _default_personal_details()

    base = _default_personal_details()
    base.update({k: data.get(k, base[k]) for k in base})

    if not isinstance(base["education"], list):
        base["education"] = _default_personal_details()["education"]
    if not isinstance(base["work"], list):
        base["work"] = _default_personal_details()["work"]
    if not isinstance(base["skills"], list):
        base["skills"] = _default_personal_details()["skills"]

    return base


def save_personal_details(data: dict):
    os.makedirs(os.path.dirname(PERSONAL_FILE), exist_ok=True)
    with open(PERSONAL_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
