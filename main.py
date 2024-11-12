import subprocess
import time
import platform

def ping(ip):
    try:
        if platform.system().lower() == "windows":
            command = ["ping", ip, "-n", "1", "-w", "2000"]  # -n for count, -w for timeout in ms
        else:
            command = ["ping", ip, "-c", "1", "-W", "2"]  # -c for count, -W for timeout in seconds
        
        output = subprocess.run(command, capture_output=True, text=True)
        return output.returncode == 0
    except subprocess.TimeoutExpired:
        return False

def gather_ping_data(ips, duration):
    start_time = time.time()
    ping_results = {ip: {"success": 0, "timeout": 0} for ip in ips}
    
    while time.time() - start_time < duration:
        for ip in ips:
            if ping(ip):
                ping_results[ip]["success"] += 1
            else:
                ping_results[ip]["timeout"] += 1
            # Wait 1 second between each ping to avoid excessive requests
            time.sleep(1)
    
    return ping_results

def analyze_results(ping_results):
    for ip, results in ping_results.items():
        total = results["success"] + results["timeout"]
        timeout_percentage = (results["timeout"] / total) * 100 if total > 0 else 0
        print(f"IP: {ip}")
        print(f"  Total Requests: {total}")
        print(f"  Successful: {results['success']}")
        print(f"  Timed Out: {results['timeout']}")
        print(f"  Timeout Percentage: {timeout_percentage:.2f}%\n")

ips_to_test = ["1.1.1.1", "8.8.8.8"]
duration = 300

ping_data = gather_ping_data(ips_to_test, duration)
analyze_results(ping_data)
