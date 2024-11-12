import subprocess
import time
import platform
import csv
from datetime import datetime

def ping(ip):
    try:
        if platform.system().lower() == "windows":
            command = ["ping", ip, "-n", "1", "-w", "4000"]
        else:
            command = ["ping", ip, "-c", "1", "-W", "2"]
        
        output = subprocess.run(command, capture_output=True, text=True)
        return output.returncode == 0
    except subprocess.TimeoutExpired:
        return False

def gather_ping_data(ips, duration, save_interval=10):
    start_time = time.time()
    ping_results = {ip: {"success": 0, "timeout": 0} for ip in ips}
    csv_filename = "ping_log.csv"

    # Write header to CSV file
    with open(csv_filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["timestamp", "ip", "total_requests", "successful", "timed_out", "timeout_percentage"])
    
    while time.time() - start_time < duration:
        for ip in ips:
            if ping(ip):
                ping_results[ip]["success"] += 1
            else:
                ping_results[ip]["timeout"] += 1
            time.sleep(1)
        
        # Save results every `save_interval` seconds
        if (time.time() - start_time) % save_interval < 1:
            save_results_to_csv(ping_results, csv_filename)

    return ping_results

def save_results_to_csv(ping_results, filename):
    timestamp = datetime.now().isoformat()
    with open(filename, mode="a", newline="") as file:
        writer = csv.writer(file)
        for ip, results in ping_results.items():
            total = results["success"] + results["timeout"]
            timeout_percentage = (results["timeout"] / total) * 100 if total > 0 else 0
            writer.writerow([timestamp, ip, total, results["success"], results["timeout"], f"{timeout_percentage:.2f}"])

def analyze_results(ping_results):
    for ip, results in ping_results.items():
        total = results["success"] + results["timeout"]
        timeout_percentage = (results["timeout"] / total) * 100 if total > 0 else 0
        print(f"IP: {ip}")
        print(f"  Total Requests: {total}")
        print(f"  Successful: {results['success']}")
        print(f"  Timed Out: {results['timeout']}")
        print(f"  Timeout Percentage: {timeout_percentage:.2f}%\n")

# Run the ping test for 1 hour (3600 seconds)
ips_to_test = ["1.1.1.1", "8.8.8.8"]
duration = 3600  # in seconds
save_interval = 10  # save data every 10 seconds

ping_data = gather_ping_data(ips_to_test, duration, save_interval)
analyze_results(ping_data)
