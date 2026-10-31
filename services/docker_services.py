
import docker


def get_docker_containers():

    try:
        client = docker.from_env()

        # Check Docker connection
        client.ping()

        # Get all containers, including stopped containers
        containers = client.containers.list(all=True)

        container_data = []

        for container in containers:

            container.reload()

            state = container.attrs.get("State", {})

            health_info = state.get("Health", {})

            health = health_info.get("Status", "N/A")

            container_data.append({

                "id": container.short_id,

                "name": container.name,

                "image": container.image.tags,

                "status": container.status.upper(),

                "health": health.upper()

            })

        return container_data

    except Exception as e:

        return {"error": str(e)}


# Function to calculate CPU usage of running containers

def get_docker_cpu_usage():

    try:
        client = docker.from_env()

        # Get only running containers
        containers = client.containers.list(
            filters={"status": "running"}
        )

        cpu_data = []

        for container in containers:

            # Get CPU statistics
            stats = container.stats(stream=False)

            cpu_stats = stats["cpu_stats"]

            precpu_stats = stats["precpu_stats"]

            # Calculate CPU usage difference
            cpu_delta = (
                cpu_stats["cpu_usage"]["total_usage"]
                - precpu_stats["cpu_usage"]["total_usage"]
            )

            system_delta = (
                cpu_stats["system_cpu_usage"]
                - precpu_stats["system_cpu_usage"]
            )

            # Get number of CPUs
            online_cpus = cpu_stats.get(
                "online_cpus",
                len(
                    cpu_stats["cpu_usage"].get(
                        "percpu_usage", []
                    )
                )
            )

            # Calculate CPU percentage
            if system_delta > 0 and cpu_delta >= 0:

                cpu_percent = (
                    (cpu_delta / system_delta)
                    * online_cpus
                    * 100
                )

            else:

                cpu_percent = 0

            cpu_data.append({

                "id": container.short_id,

                "name": container.name,

                "cpu_usage": round(cpu_percent, 2)

            })

        return cpu_data

    except Exception as e:

        return {"error": str(e)}
