
import os
import requests

from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

# Load Jenkins credentials
load_dotenv()

JENKINS_URL = os.getenv("JENKINS_URL")
JENKINS_USER = os.getenv("JENKINS_USER")
JENKINS_TOKEN = os.getenv("JENKINS_TOKEN")


def connect_jenkins():

    try:
        print("Connecting to Jenkins...")

        url = JENKINS_URL.rstrip("/") + "/api/json"

        params = {
            "tree": "jobs[name,color,lastBuild[number,result,building,timestamp,duration]]"
        }

        response = requests.get(
            url,
            params=params,
            auth=HTTPBasicAuth(
                JENKINS_USER,
                JENKINS_TOKEN
            ),
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        print("\nJenkins Connected Successfully!")
        print("--------------------------------")

        jobs = data.get("jobs", [])

        if not jobs:
            print("No Jenkins jobs found.")

        for job in jobs:

            build = job.get("lastBuild") or {}

            if build.get("building"):
                status = "RUNNING"

            elif build.get("result"):
                status = build["result"]

            else:
                status = "NOT BUILT"

            print("\nJob Name:", job["name"])
            print("Build Number:", build.get("number", "-"))
            print("Status:", status)
            print("Duration:", build.get("duration", 0), "ms")

        print("\nTotal Jenkins Jobs:", len(jobs))

    except requests.exceptions.HTTPError as e:
        print("Jenkins HTTP Error:", e)
        print("Check your username, API token and permissions.")

    except requests.exceptions.ConnectionError:
        print("Cannot connect to Jenkins.")
        print("Check whether Jenkins is running.")

    except requests.exceptions.RequestException as e:
        print("Request Error:", e)

    except Exception as e:
        print("Unexpected Error:", e)


connect_jenkins()
