
import os
import re
import shutil
import sys
import logging
from datetime import datetime

import requests
from bs4 import BeautifulSoup

LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")

def get_logger(tool_name):
 
    os.makedirs(LOG_DIR, exist_ok=True)

    log_filename = tool_name + "_" + datetime.now().strftime("%Y-%m-%d") + ".log"
    log_path = os.path.join(LOG_DIR, log_filename)

    logger = logging.getLogger(tool_name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-7s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger


# ======================================================================
#  TOOL 1: FILE ORGANIZER  (os, shutil)
# ======================================================================

file_organizer_logger = get_logger("file_organizer")

CATEGORY_MAP = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"],
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt"],
    "Spreadsheets": [".xls", ".xlsx", ".csv"],
    "Presentations": [".ppt", ".pptx"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Audio": [".mp3", ".wav", ".aac", ".flac"],
    "Video": [".mp4", ".mov", ".avi", ".mkv"],
    "Code": [".py", ".js", ".html", ".css", ".java", ".cpp", ".c"]
}

def get_category(file_extension):
    """Return the category name for a given file extension, or 'Other'."""
    file_extension = file_extension.lower()
    for category, extensions in CATEGORY_MAP.items():
        if file_extension in extensions:
            return category
    return "Other"

def get_unique_destination(destination_folder, filename):
    """
    If a file with the same name already exists in the destination,
    append a number to avoid overwriting it (e.g. photo.jpg -> photo (1).jpg).
    """
    base_name, extension = os.path.splitext(filename)
    destination_path = os.path.join(destination_folder, filename)

    counter = 1
    while os.path.exists(destination_path):
        new_filename = base_name + " (" + str(counter) + ")" + extension
        destination_path = os.path.join(destination_folder, new_filename)
        counter += 1

    return destination_path

def organize_folder(source_folder, dry_run=False):
    """
    Organize all files in source_folder into category subfolders.
    If dry_run is True, no files are actually moved - only logged.
    """
    if not os.path.isdir(source_folder):
        file_organizer_logger.error("Source folder does not exist: " + source_folder)
        return {"moved": 0, "skipped": 0, "errors": 0}

    stats = {"moved": 0, "skipped": 0, "errors": 0}

    file_organizer_logger.info("Starting file organization in: " + source_folder)
    if dry_run:
        file_organizer_logger.info("DRY RUN MODE - no files will actually be moved.")

    entries = os.listdir(source_folder)

    for entry in entries:
        full_path = os.path.join(source_folder, entry)

        if os.path.isdir(full_path):
            continue
        if entry.startswith("."):
            continue

        _, extension = os.path.splitext(entry)
        category = get_category(extension)
        category_folder = os.path.join(source_folder, category)

        try:
            if not dry_run:
                os.makedirs(category_folder, exist_ok=True)
                destination_path = get_unique_destination(category_folder, entry)
                shutil.move(full_path, destination_path)

            file_organizer_logger.info("Moved '" + entry + "' -> " + category + "/")
            stats["moved"] += 1

        except Exception as error:
            file_organizer_logger.error("Failed to move '" + entry + "': " + str(error))
            stats["errors"] += 1

    file_organizer_logger.info(
        "Organization complete. Moved: " + str(stats["moved"]) +
        ", Errors: " + str(stats["errors"])
    )

    return stats


def run_file_organizer():
    print("=" * 55)
    print("              FILE ORGANIZER")
    print("=" * 55)
    print("  Sorts files in a folder into type-based subfolders")
    print("  such as Images, Documents, Archives, and more.")
    print("=" * 55)

    folder_path = input("  Enter the full path of the folder to organize: ").strip()

    if not os.path.isdir(folder_path):
        print("  That folder does not exist. Please check the path and try again.")
        return

    dry_run_input = input("  Run in preview mode first? (yes / no): ").strip().lower()
    dry_run = dry_run_input in ("yes", "y")

    stats = organize_folder(folder_path, dry_run=dry_run)

    print("  Summary:")
    print("  Files moved : " + str(stats["moved"]))
    print("  Errors      : " + str(stats["errors"]))

    if dry_run:
        confirm = input("  Apply these changes for real now? (yes / no): ").strip().lower()
        if confirm in ("yes", "y"):
            organize_folder(folder_path, dry_run=False)
        else:
            print("  No files were moved.")

    print("  Done. Check the logs/ folder for a full activity record.")


# ======================================================================
#  TOOL 2: EMAIL EXTRACTOR  (re, file handling)
# ======================================================================

email_extractor_logger = get_logger("email_extractor")

EMAIL_PATTERN = re.compile(
    r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"
)


def extract_emails_from_text(text):
    """Return a sorted list of unique, lowercase email addresses found in the text."""
    found = EMAIL_PATTERN.findall(text)
    unique_emails = sorted(set(email.lower() for email in found))
    return unique_emails


def extract_emails_from_file(input_file_path):
    """Read a text file and extract all email addresses from it."""
    if not os.path.isfile(input_file_path):
        email_extractor_logger.error("Input file does not exist: " + input_file_path)
        return []

    email_extractor_logger.info("Reading file: " + input_file_path)

    with open(input_file_path, "r", encoding="utf-8", errors="ignore") as file:
        content = file.read()

    emails = extract_emails_from_text(content)

    email_extractor_logger.info("Found " + str(len(emails)) + " unique email address(es).")

    return emails

def save_emails_to_file(emails, output_file_path):
    """Write the list of emails to a new text file, one per line."""
    with open(output_file_path, "w", encoding="utf-8") as file:
        for email in emails:
            file.write(email + "\n")

    email_extractor_logger.info("Saved " + str(len(emails)) + " email(s) to: " + output_file_path)


def run_email_extractor():
    print("=" * 55)
    print("              EMAIL EXTRACTOR")
    print("=" * 55)
    print("  Extracts all valid email addresses from a text file")
    print("  and saves the unique results to a new file.")
    print("=" * 55)

    input_path = input("  Enter the path of the .txt file to scan: ").strip()

    emails = extract_emails_from_file(input_path)

    if not emails:
        print("  No email addresses were found, or the file could not be read.")
        return

    print("  Found " + str(len(emails)) + " unique email address(es):")
    print("  " + "-" * 40)
    for email in emails:
        print("  " + email)
    print("  " + "-" * 40)

    output_path = input("  Enter output file name (e.g. extracted_emails.txt): ").strip()

    if not output_path:
        output_path = "extracted_emails.txt"

    save_emails_to_file(emails, output_path)

    print("  Done. Results saved to '" + output_path + "'.")
    print("  Check the logs/ folder for a full activity record.")


# ======================================================================
#  TOOL 3: WEBPAGE TITLE SCRAPER  (requests, BeautifulSoup)
# ======================================================================

web_scraper_logger = get_logger("web_scraper")

REQUEST_TIMEOUT = 10
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Automation Toolkit Web Scraper)"
}


def fetch_page_title(url):
    """
    Fetch the given URL and return its <title> text.
    Returns None if the request fails or no title is found.
    """
    web_scraper_logger.info("Fetching URL: " + url)

    try:
        response = requests.get(url, headers=REQUEST_HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.exceptions.RequestException as error:
        web_scraper_logger.error("Request failed for '" + url + "': " + str(error))
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    if soup.title and soup.title.string:
        title = soup.title.string.strip()
        web_scraper_logger.info("Title found: " + title)
        return title

    web_scraper_logger.warning("No <title> tag found for: " + url)
    return None


def save_title_record(url, title, output_file_path):
    """Append a timestamped record of the scraped title to a results file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    file_exists = os.path.isfile(output_file_path)

    with open(output_file_path, "a", encoding="utf-8") as file:
        if not file_exists:
            file.write("Timestamp".ljust(22) + " | " + "URL".ljust(40) + " | Title\n")
            file.write("-" * 100 + "\n")

        file.write(timestamp.ljust(22) + " | " + url[:40].ljust(40) + " | " + title + "\n")

    web_scraper_logger.info("Record saved to: " + output_file_path)


def run_web_scraper():
    print("=" * 55)
    print("              WEBPAGE TITLE SCRAPER")
    print("=" * 55)
    print("  Fetches a webpage and saves its title to a running")
    print("  history file with a timestamp.")
    print("=" * 55)

    url = input("  Enter the webpage URL: ").strip()

    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    title = fetch_page_title(url)

    if title is None:
        print("  Could not retrieve the title for that URL.")
        print("  Check the logs/ folder for error details.")
        return

    print("  Page title found:")
    print("  \"" + title + "\"")

    output_path = "scraped_titles.txt"
    save_title_record(url, title, output_path)

    print("  Saved to '" + output_path + "'.")
    print("  Check the logs/ folder for a full activity record.")

# ======================================================================
#  MAIN MENU
# ======================================================================

def print_banner():
    print("#" * 55)
    print("#                                                     #")
    print("#              PYTHON AUTOMATION TOOLKIT              #")
    print("#                                                     #")
    print("#" * 55)
    print("  Three small tools that automate repetitive,")
    print("  everyday tasks.")


def print_menu():
    print("  MAIN MENU")
    print("  " + "-" * 40)
    print("  1. Organize files in a folder by type")
    print("  2. Extract email addresses from a text file")
    print("  3. Scrape a webpage's title")
    print("  4. Exit")
    print("  " + "-" * 40)


def main():
    print_banner()

    while True:
        print_menu()
        choice = input("  Select an option (1-4): ").strip()

        if choice == "1":
            run_file_organizer()
        elif choice == "2":
            run_email_extractor()
        elif choice == "3":
            run_web_scraper()
        elif choice == "4":
            print("  Exiting the Automation Toolkit. Goodbye.")
            break
        else:
            print("  Invalid option. Please enter a number from 1 to 4.")


main()
