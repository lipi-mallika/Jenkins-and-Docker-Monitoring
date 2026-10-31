
import os
import requests

from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

load_dotenv()

JENKINS_URL = os.getenv("JENKINS_URL")
JENKINS_USER = os.getenv("JENKINS_USER")
JENKINS_TOKEN = os.getenv("JENKINS_TOKEN")


def get_jenkins_jobs():

    try:
        url = JENKINS_URL.rstrip("/") + "/api/json"

        params = {
            "tree": "jobs[name,color,lastBuild[number,result,building,timestamp,duration],builds[number,result,building,timestamp,duration]{0,5}]"
        }

        response = requests.get(
            url,
            params=params,
            auth=HTTPBasicAuth(JENKINS_USER, JENKINS_TOKEN),
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        jobs = []

        for job in data.get("jobs", []):

            last_build = job.get("lastBuild") or {}

            if last_build.get("building"):
                status = "RUNNING"

            elif last_build.get("result"):
                status = last_build["result"]

            else:
                status = "NOT_BUILT"

            jobs.append({
                "name": job["name"],
                "build_number": last_build.get("number"),
                "status": status,
                "duration": last_build.get("duration", 0),
                "timestamp": last_build.get("timestamp"),
                "builds": job.get("builds", [])
            })

        return jobs

    except requests.RequestException as e:
        return {"error": str(e)}
