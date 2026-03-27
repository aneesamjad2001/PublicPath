import requests
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

API_KEY = os.getenv("USAJOBS_API_KEY")
EMAIL = os.getenv("USAJOBS_EMAIL")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_jobs(keyword="analyst", location="", results_per_page=25):
    url = "https://data.usajobs.gov/api/search"

    headers = {
        "Host": "data.usajobs.gov",
        "User-Agent": EMAIL,
        "Authorization-Key": API_KEY
    }

    params = {
        "Keyword": keyword,
        "LocationName": location,
        "ResultsPerPage": results_per_page
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        return []

    data = response.json()
    jobs = data["SearchResult"]["SearchResultItems"]

    results = []
    for job in jobs:
        j = job["MatchedObjectDescriptor"]
        results.append({
            "title": j["PositionTitle"],
            "agency": j["OrganizationName"],
            "location": j["PositionLocationDisplay"],
            "salary_min": j["PositionRemuneration"][0]["MinimumRange"],
            "salary_max": j["PositionRemuneration"][0]["MaximumRange"],
            "close_date": j["ApplicationCloseDate"],
            "url": j["PositionURI"],
            "source": "usajobs"
        })

    return results


def save_jobs(jobs):
    saved = 0
    skipped = 0

    for job in jobs:
        try:
            supabase.table("jobs").insert(job).execute()
            saved += 1
            print(f"Saved: {job['title']}")
        except Exception as e:
            skipped += 1
            print(f"Skipped (already exists): {job['title']}")

    print(f"\nDone — {saved} saved, {skipped} skipped.")


if __name__ == "__main__":
    keywords = [
        "policy",
        "analyst",
        "attorney",
        "economist",
        "program manager",
        "public health",
        "urban planning",
        "social worker",
        "data scientist",
        "communications"
    ]

    for kw in keywords:
        print(f"\nFetching: {kw}...")
        jobs = fetch_jobs(keyword=kw, location="", results_per_page=25)
        print(f"Found {len(jobs)} jobs. Saving...")
        save_jobs(jobs)

    print("All done! Database is loaded.")