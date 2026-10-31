
from database.db import (
    get_job_history,
    get_container_history,
    get_cpu_history
)

jobs = get_job_history()
containers = get_container_history()
cpu = get_cpu_history()

print("\n===== JENKINS BUILD HISTORY =====")
print("Total records:", len(jobs))

for record in jobs[:5]:
    print(record)

print("\n===== DOCKER CONTAINER HISTORY =====")
print("Total records:", len(containers))

for record in containers[:5]:
    print(record)

print("\n===== DOCKER CPU HISTORY =====")
print("Total records:", len(cpu))

for record in cpu[:5]:
    print(record)
