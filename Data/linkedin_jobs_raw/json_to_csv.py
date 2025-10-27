import os
import json
import csv

INPUT_DIR = r"C:\Users\Admin\Desktop\resume-recommender\linkedin_jobs_raw"      # folder where all JSONs are stored
OUTPUT_FILE = "all_jobs.csv"

# Columns you want in CSV
FIELDS = ["job_position", "job_link", "company_name", "job_location"]

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=FIELDS)
    writer.writeheader()

    # Loop through all JSON files in folder
    for filename in os.listdir(INPUT_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(INPUT_DIR, filename)

            with open(filepath, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    print(f"Skipping {filename}, invalid JSON")
                    continue

                # Each file may have list of jobs or single job
                if isinstance(data, list):
                    jobs = data
                elif isinstance(data, dict):
                    jobs = data.get("jobs", [data])
                else:
                    jobs = []

                # Write rows
                for job in jobs:
                    row = {field: job.get(field, "") for field in FIELDS}
                    writer.writerow(row)

print(f"✅ CSV created: {OUTPUT_FILE}")
