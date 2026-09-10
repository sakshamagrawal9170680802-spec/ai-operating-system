import psutil

for process in psutil.process_iter(["pid","name","cpu_percent","memory_percent"]):
    print((process))
    print(type(process.info))
    break

print(type(psutil.virtual_memory()))