
let jenkinsChart = null;
let dockerChart = null;

// Convert milliseconds into seconds
function convertToSeconds(milliseconds) {
    return (milliseconds / 1000).toFixed(2);
}


// Load Jenkins historical build data
async function loadJenkinsHistory() {

    try {

        const response = await fetch("/api/history/jobs");

        if (!response.ok) {
            throw new Error("Unable to fetch Jenkins history");
        }

        const history = await response.json();

        // Sort builds from oldest to newest
        history.sort((a, b) =>
            (a.build_timestamp || 0) - (b.build_timestamp || 0)
        );

        const labels = history.map(item =>
            item.job_name + " #" + item.build_number
        );

        const durations = history.map(item =>
            Number(convertToSeconds(item.duration || 0))
        );

        const ctx = document.getElementById("jenkinsChart");

        if (jenkinsChart) {
            jenkinsChart.destroy();
        }

        jenkinsChart = new Chart(ctx, {

            type: "line",

            data: {
                labels: labels,

                datasets: [{
                    label: "Build Duration (seconds)",
                    data: durations,
                    borderWidth: 2,
                    tension: 0.3,
                    fill: false
                }]
            },

            options: {
                responsive: true,

                maintainAspectRatio: false,

                plugins: {
                    legend: {
                        display: true
                    }
                },

                scales: {
                    x: {
                        title: {
                            display: true,
                            text: "Jenkins Job and Build"
                        }
                    },

                    y: {
                        beginAtZero: true,

                        title: {
                            display: true,
                            text: "Duration (seconds)"
                        }
                    }
                }
            }

        });

    } catch (error) {

        console.error("Jenkins graph error:", error);

    }

}


// Load Docker historical CPU data
async function loadDockerHistory() {

    try {

        const response = await fetch("/api/history/cpu");

        if (!response.ok) {
            throw new Error("Unable to fetch Docker CPU history");
        }

        const history = await response.json();

        // Sort records from oldest to newest
        history.sort((a, b) =>
            new Date(a.recorded_at) - new Date(b.recorded_at)
        );

        // Collect unique timestamps
        const labels = [
            ...new Set(
                history.map(item =>
                    new Date(item.recorded_at).toLocaleTimeString()
                )
            )
        ];

        // Group CPU readings by container
        const containers = {};

        history.forEach(item => {

            const name = item.container_name;
            const time = new Date(item.recorded_at).toLocaleTimeString();

            if (!containers[name]) {
                containers[name] = {};
            }

            containers[name][time] = item.cpu_usage;

        });

        // Create a separate dataset for each container
        const datasets = Object.keys(containers).map(name => ({

            label: name,

            data: labels.map(time =>
                containers[name][time] ?? null
            ),

            borderWidth: 2,
            tension: 0.3,
            fill: false

        }));

        const ctx = document.getElementById("dockerChart");

        if (dockerChart) {
            dockerChart.destroy();
        }

        dockerChart = new Chart(ctx, {

            type: "line",

            data: {
                labels: labels,
                datasets: datasets
            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                plugins: {
                    legend: {
                        display: true,
                        position: "bottom"
                    }
                },

                scales: {

                    x: {
                        title: {
                            display: true,
                            text: "Monitoring Time"
                        }
                    },

                    y: {
                        beginAtZero: true,

                        title: {
                            display: true,
                            text: "CPU Usage (%)"
                        }
                    }

                }

            }

        });

    } catch (error) {

        console.error("Docker graph error:", error);

    }

}


// Load both graphs
async function loadHistoricalCharts() {

    await loadJenkinsHistory();

    await loadDockerHistory();

}


// Load graphs when page opens
document.addEventListener("DOMContentLoaded", () => {

    loadHistoricalCharts();

    // Refresh historical graphs every 30 seconds
    setInterval(loadHistoricalCharts, 30000);

});
