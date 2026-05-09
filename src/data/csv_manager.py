# src/data/csv_manager.py
import csv
import os
from datetime import datetime

from config.settings import settings_data
from src.utils.logger import logger
from src.utils.text_helpers import truncate_for_csv


class CSVManager:
    def __init__(self):
        # Ensure directories exist
        os.makedirs(os.path.dirname(settings_data.file_name) or ".", exist_ok=True)
        # Increase field size limit to prevent errors
        csv.field_size_limit(1000000)

    def get_applied_job_ids(self) -> set[str]:
        """Returns a set of Job IDs from existing applied jobs history csv file."""
        job_ids = set()
        try:
            with open(settings_data.file_name, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Guard against empty rows or missing headers
                    if 'Job ID' in row and row['Job ID']:
                        job_ids.add(row['Job ID'])
        except FileNotFoundError:
            logger.warning(f"CSV file '{settings_data.file_name}' does not exist yet. Starting fresh.")
        return job_ids

    def get_all_applied_jobs_for_ui(self) -> list[dict]:
        """Used by the Flask web server to display the dashboard."""
        jobs = []
        try:
            with open(settings_data.file_name, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    jobs.append(row)
        except FileNotFoundError:
            logger.error(f"No applications history found at {settings_data.file_name}")
        return jobs

    def log_submitted_job(self, job_data: dict) -> None:
        """Appends a successfully applied job to the CSV."""
        fieldnames = [
            'Job ID', 'Title', 'Company', 'Work Location', 'Work Style',
            'About Job', 'Experience required', 'Skills required', 'HR Name',
            'HR Link', 'Resume', 'Re-posted', 'Date Posted', 'Date Applied',
            'Job Link', 'External Job link', 'Questions Found', 'Connect Request'
        ]

        try:
            file_exists = os.path.isfile(settings_data.file_name)
            with open(settings_data.file_name, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                if not file_exists or file.tell() == 0:
                    writer.writeheader()

                # Clean up the data before writing
                safe_data = {k: truncate_for_csv(v) for k, v in job_data.items() if k in fieldnames}
                writer.writerow(safe_data)
            logger.info(f"Successfully logged applied job: {job_data.get('Job ID')}")
        except Exception as e:
            logger.error(f"Failed to update submitted jobs list! Error: {e}")

    def log_failed_job(self, job_data: dict) -> None:
        """Appends a failed job to the failed CSV."""
        fieldnames = [
            'Job ID', 'Job Link', 'Resume Tried', 'Date listed', 'Date Tried',
            'Assumed Reason', 'Stack Trace', 'External Job link', 'Screenshot Name'
        ]

        try:
            file_exists = os.path.isfile(settings_data.failed_file_name)
            with open(settings_data.failed_file_name, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                if not file_exists or file.tell() == 0:
                    writer.writeheader()

                job_data['Date Tried'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                safe_data = {k: truncate_for_csv(v) for k, v in job_data.items() if k in fieldnames}
                writer.writerow(safe_data)
            logger.info(f"Successfully logged failed job: {job_data.get('Job ID')}")
        except Exception as e:
            logger.error(f"Failed to update failed jobs list! Error: {e}")
