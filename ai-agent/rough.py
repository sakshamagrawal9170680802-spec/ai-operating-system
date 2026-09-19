import psutil

for process in psutil.process_iter(["pid","name","cpu_percent","memory_percent"]):
    print((process))
    print(type(process.info))
    break

print(type(psutil.virtual_memory()))




def list_processes():

    processes = []

    for process in psutil.process_iter(
        ["pid", "name", "cpu_percent", "memory_percent"]
    ):
        try:
            info = process.info

            processes.append({
                "pid": info["pid"],
                "name": info["name"],
                "cpu_percent": info["cpu_percent"],
                "memory_percent": info["memory_percent"],
            })

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess
        ):
            continue

    print("TOTAL PROCESSES:", len(processes))

    processes.sort(
        key=lambda x: x["memory_percent"],
        reverse=True
    )

    print("TOP PROCESSES:")
    for process in processes[:10]:
        print(process)

    return processes[:10]


list_processes()