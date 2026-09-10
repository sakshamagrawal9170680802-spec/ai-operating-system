import psutil
import time

#for CPU informaions

print(psutil.cpu_count())#it gives total no. of logical CPUs means cores in CPU performing logical functions
print(psutil.cpu_count(logical=False))#it gives total no. of physical CPUs means cores in CPU performing functions other than logical

print(psutil.cpu_percent(interval=1))#it measures the usage of cpu by change taking place in cpu usage percentage over time like here i have given 1sec if you will not give interval than it will quickly print it where in this short interval definetly anser will be zero dut to no change in cpu percent use

print(psutil.cpu_percent(percpu=True))#it gives cpu_percent for each logical_cpu seperately

print(psutil.cpu_times())#it gives statistics of how much time is spent on each type of work in cpu



#for memory information


print(psutil.virtual_memory())#it gives information about RAM how much avialable how much is in use etc in bytes to convert them to GB divide them by 1024**3
print(psutil.swap_memory())#when any information is loadded on RAM sometimes due to overloading some information is moved from RAM to DISK however disk is slow it can reduce performance


#DISK Usage
print(psutil.disk_usage("C:"))#it gives full information about how much is used, how much is free etc
print(psutil.disk_usage("D:"))#it gives full information about how much is used, how much is free etc

print(psutil.disk_partitions())#it gives full information about every folders in which memory is divided in my case it will show C: and D: with all information related to them because only these two are present


#I/O
print(psutil.disk_io_counters())#it shows how much data is being written or read etc
print(psutil.net_io_counters())#it shows how much data is being received or sent etc through network
print(psutil.net_if_addrs())
print(psutil.net_if_stats())#it gives information about your current network connection if you are connected to network through ethernet,wifi etc


#processes
print(psutil.process_iter())#this lets you inspect running processes one of most important function for our ai operating system
for process in psutil.process_iter():
    print(process.pid,process.name())


#to get your current process you are running right now
print(psutil.Process())


#you can also target a particular process if you know its PID value
print(psutil.Process(25968))

#you can perform above functions on a particuler process as well
p=psutil.Process(25968)
print(p.cpu_percent())
print(p.cpu_times())
print(p.memory_info())#here rss shows resident set size that represents memory pages of the process that are currently resident in physical memory,with platform specific details
print(p.status())#it shows what a process is doing and which state is in it like running,sleeping etc
print(p.create_time())#this gives a process creation timestamp

#processes can have parent child relationship with each other like "Operating System->Terminal->Python->Child process"
#to get parent or child of a process
print(p.parent())  
print(p.children())  



# The operating system maintains a process table / process information structures.
# On Linux, a lot of process information is exposed through the /proc filesystem.

    #              Your Python Program
    #                      │
    #                      ↓
    #                  psutil API
    #                      │
    #         ┌────────────┼────────────┐
    #         ↓            ↓            ↓
    #      Windows       Linux        macOS
    #         │            │            │
    #    Windows APIs     /proc      macOS APIs
    #    system APIs      /sys
    #         │            │            │
    #         └────────────┼────────────┘
    #                      ↓
    #                 OS Kernel
    #                      ↓
    #                   Hardware



# all the above functions are not continuosly performed if you want it to continuosly performed use it like this
# while True:
#     print(psutil.cpu_percent())
#     print(psutil.virtual_memory().percent)

#     time.sleep(1)



# as psutil uses windows API aor other API based on the operating system and thus it is possible that psutil ask for an information and is denined for it and in that case it throws error like
#"psutil.AccessDenied"
#or "psutil.NoSuchProcess" if you ask for process with pid that does not exist
#in this case it is better to use try and except error handling approach



#note psutil does not perform only read-only functions
# therefore it is dangerous to use that type of functions
  
#p.terminate() #it terminates that process
#p.kill() #it strongly terminates that process



print(psutil.net_connections())# to inspect your net connections
print(psutil.users())# to know about the user of this operating system


#to know about current hardware conditions
print(psutil.sensors_battery())# to get information about battery




# note libraries such as "os,platform,subprocess" etc are there to perform these functions but psutil is much better in handling these functions in a unified and simple syntax format