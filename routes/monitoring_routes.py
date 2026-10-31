
from flask import Blueprint, jsonify

from services.jenkins_services import get_jenkins_jobs

from services.docker_services import (
    get_docker_containers,
    get_docker_cpu_usage
)

from database.db import (
    save_monitoring_data,
    get_job_history,
    get_container_history,
    get_cpu_history
)

monitoring = Blueprint("monitoring", __name__)


@monitoring.route("/api/jenkins")
def jenkins_status():
    jobs = get_jenkins_jobs()

    if isinstance(jobs, dict):
        return jsonify(jobs), 503

    return jsonify(jobs)


@monitoring.route("/api/containers")
def container_status():
    containers = get_docker_containers()

    if isinstance(containers, dict):
        return jsonify(containers), 503

    return jsonify(containers)


@monitoring.route("/api/dashboard")
def dashboard_data():

    jobs = get_jenkins_jobs()
    containers = get_docker_containers()
    cpu_data = get_docker_cpu_usage()

    if isinstance(jobs, dict):
        return jsonify({
            "error": "Jenkins connection failed",
            "details": jobs["error"]
        }), 503

    if isinstance(containers, dict):
        return jsonify({
            "error": "Docker connection failed",
            "details": containers["error"]
        }), 503

    durations = []
    recent_builds = []

    for job in jobs:
        for build in job.get("builds", []):

            if (
                build.get("duration", 0) > 0
                and not build.get("building")
            ):
                durations.append(build["duration"])

            recent_builds.append({
                "job_name": job["name"],
                "build_number": build.get("number"),
                "status": (
                    "RUNNING" if build.get("building")
                    else build.get("result") or "NOT_BUILT"
                ),
                "duration": build.get("duration", 0),
                "timestamp": build.get("timestamp")
            })

    average_duration = (
        sum(durations) / len(durations)
        if durations else 0
    )

    recent_builds.sort(
        key=lambda b: b["timestamp"] or 0,
        reverse=True
    )

    recent_builds = recent_builds[:5]

    if isinstance(cpu_data, dict):
        cpu_error = cpu_data["error"]
        cpu_data = []
    else:
        cpu_error = None

    # Save monitoring information into SQLite
    save_monitoring_data(jobs, containers, cpu_data)

    return jsonify({
        "total_jobs": len(jobs),

        "successful_jobs": sum(
            j["status"] == "SUCCESS" for j in jobs
        ),

        "failed_jobs": sum(
            j["status"] == "FAILURE" for j in jobs
        ),

        "running_jobs": sum(
            j["status"] == "RUNNING" for j in jobs
        ),

        "total_containers": len(containers),

        "running_containers": sum(
            c["status"] == "RUNNING" for c in containers
        ),

        "stopped_containers": sum(
            c["status"] == "EXITED" for c in containers
        ),

        "average_build_duration": round(
            average_duration, 2
        ),

        "recent_builds": recent_builds,
        "docker_cpu_usage": cpu_data,
        "docker_cpu_error": cpu_error,
        "jobs": jobs,
        "containers": containers
    })


# Jenkins build history
@monitoring.route("/api/history/jobs")
def job_history():
    return jsonify(get_job_history())


# Docker container status history
@monitoring.route("/api/history/containers")
def container_history():
    return jsonify(get_container_history())


# Docker CPU history
@monitoring.route("/api/history/cpu")
def cpu_history():
    return jsonify(get_cpu_history())
