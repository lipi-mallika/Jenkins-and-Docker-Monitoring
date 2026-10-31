
async function loadDashboard() {

    const errorMessage = document.getElementById("errorMessage");

    try {

        const response = await fetch("/api/dashboard");

        if (!response.ok) {
            throw new Error("Unable to retrieve dashboard data");
        }

        const data = await response.json();

        errorMessage.textContent = "";

        // Jenkins summary cards
        document.getElementById("totalJobs").textContent =
            data.total_jobs;

        document.getElementById("successfulJobs").textContent =
            data.successful_jobs;

        document.getElementById("failedJobs").textContent =
            data.failed_jobs;

        document.getElementById("runningJobs").textContent =
            data.running_jobs;

        // Average duration: milliseconds to seconds
        document.getElementById("averageDuration").textContent =
            (data.average_build_duration / 1000).toFixed(2) + " sec";


        // Jenkins jobs table
        const jobsTable = document.getElementById("jobsTable");

        jobsTable.replaceChildren();

        if (data.jobs.length === 0) {

            jobsTable.innerHTML =
                '<tr><td colspan="4">No Jenkins jobs found</td></tr>';

        } else {

            data.jobs.forEach(job => {

                const row = document.createElement("tr");

                [
                    job.name,
                    job.build_number ?? "-",
                    job.status,
                    job.duration ?? 0
                ].forEach(value => {

                    const cell = document.createElement("td");
                    cell.textContent = value;
                    row.appendChild(cell);

                });

                jobsTable.appendChild(row);

            });
        }


        // Jenkins recent builds table
        const recentBuildsTable =
            document.getElementById("recentBuildsTable");

        recentBuildsTable.replaceChildren();

        if (data.recent_builds.length === 0) {

            recentBuildsTable.innerHTML =
                '<tr><td colspan="5">No recent builds found</td></tr>';

        } else {

            data.recent_builds.forEach(build => {

                const row = document.createElement("tr");

                const buildTime = build.timestamp
                    ? new Date(build.timestamp).toLocaleString()
                    : "-";

                [
                    build.job_name,
                    build.build_number ?? "-",
                    build.status,
                    build.duration ?? 0,
                    buildTime
                ].forEach(value => {

                    const cell = document.createElement("td");
                    cell.textContent = value;
                    row.appendChild(cell);

                });

                recentBuildsTable.appendChild(row);

            });
        }


        // Docker summary cards
        document.getElementById("totalContainers").textContent =
            data.total_containers;

        document.getElementById("runningContainers").textContent =
            data.running_containers;

        document.getElementById("stoppedContainers").textContent =
            data.stopped_containers;


        // Docker containers table
        const containersTable =
            document.getElementById("containersTable");

        containersTable.replaceChildren();

        if (data.containers.length === 0) {

            containersTable.innerHTML =
                '<tr><td colspan="5">No containers found</td></tr>';

        } else {

            data.containers.forEach(container => {

                const row = document.createElement("tr");

                [
                    container.name,
                    container.id,
                    (container.image || []).join(", ") || "-",
                    container.status,
                    container.health
                ].forEach(value => {

                    const cell = document.createElement("td");
                    cell.textContent = value;
                    row.appendChild(cell);

                });

                containersTable.appendChild(row);

            });
        }


        // Docker CPU usage table
        const cpuTable = document.getElementById("cpuTable");

        cpuTable.replaceChildren();

        document.getElementById("cpuError").textContent =
            data.docker_cpu_error || "";

        if (data.docker_cpu_usage.length === 0) {

            cpuTable.innerHTML =
                '<tr><td colspan="3">No running containers available for CPU monitoring</td></tr>';

        } else {

            data.docker_cpu_usage.forEach(container => {

                const row = document.createElement("tr");

                [
                    container.name,
                    container.id,
                    container.cpu_usage + "%"
                ].forEach(value => {

                    const cell = document.createElement("td");
                    cell.textContent = value;
                    row.appendChild(cell);

                });

                cpuTable.appendChild(row);

            });
        }


        // Last updated time
        document.getElementById("lastUpdated").textContent =
            "Last updated: " + new Date().toLocaleTimeString();

    }

    catch (error) {

        errorMessage.textContent = error.message;

        console.error(error);

    }

}


// Load dashboard immediately
loadDashboard();


// Refresh dashboard every 10 seconds
setInterval(loadDashboard, 10000);
