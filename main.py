import sys
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


def gather_ping_data(ips, duration, save_interval, csv_filename):
    start_time = time.time()
    ping_results = {ip: {"success": 0, "timeout": 0} for ip in ips}

    # Write header to CSV file
    with open(csv_filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "timestamp",
                "ip",
                "total_requests",
                "successful",
                "timed_out",
                "timeout_percentage",
            ]
        )

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
            writer.writerow(
                [
                    timestamp,
                    ip,
                    total,
                    results["success"],
                    results["timeout"],
                    f"{timeout_percentage:.2f}",
                ]
            )


def analyze_results(ping_results):
    for ip, results in ping_results.items():
        total = results["success"] + results["timeout"]
        timeout_percentage = (results["timeout"] / total) * 100 if total > 0 else 0
        print(f"IP: {ip}")
        print(f"  Total Requests: {total}")
        print(f"  Successful: {results['success']}")
        print(f"  Timed Out: {results['timeout']}")
        print(f"  Timeout Percentage: {timeout_percentage:.2f}%\n")


def main():
    if len(sys.argv) < 4:
        print(
            "[!] Usage: main.py <ip1> <ip2> ... <duration> <save_interval> [csv_filename]"
        )
        sys.exit()

    try:
        ip = sys.argv[1:-2]  # Collect IP's until the last 2 arguments
        duration = int(sys.argv[-2])
        save_interval = int(sys.argv[-1])
        csv_filename = "ping_log.csv"
    except ValueError:
        # If last argument is not an integer, it must be the csv filename
        ip = sys.argv[1:-3]  # Collect IP's until the last 3 arguments
        duration = int(sys.argv[-3])
        save_interval = int(sys.argv[-2])
        csv_filename = sys.argv[-1]

    ping_data = gather_ping_data(ip, duration, save_interval, csv_filename)
    analyze_results(ping_data)


main()
