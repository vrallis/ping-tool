#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys
import subprocess
import time
import platform
import csv
from datetime import datetime, timedelta
from collections import deque

# ANSI text colour codes
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
PURPLE = "\033[35m"
RESET = "\033[0m"  # Reset to default colour

def ping(ip, timeout_duration):
    """
    Ping the given IP address & return (reachable, response_time).
    """
    try:
        if platform.system().lower() == "windows":
            command = ["ping", ip, "-n", "1", "-w", str(timeout_duration)]
        else:
            command = ["ping", ip, "-c", "1", "-W", str(timeout_duration // 1000)]

        output = subprocess.run(command, capture_output=True, text=True)
        if output.returncode == 0:
            response_time = extract_response_time(output.stdout)
            return True, response_time
        else:
            return False, None
    except subprocess.TimeoutExpired:
        return False, None

def extract_response_time(output):
    """
    Extract the response time from the ping output.
    """
    try:
        if platform.system().lower() == "windows":
            start = output.find("time=") + 5
            end = output.find("ms", start)
            return int(output[start:end].strip())
        else:
            start = output.find("time=") + 5
            end = output.find(" ms", start)
            return float(output[start:end].strip())
    except (ValueError, IndexError):
        return None

def gather_ping_data(ips, duration, save_interval, timeout_duration, high_ping_threshold):
    """
    Ping a list of IP's over a duration, detect irregularities.
    """
    start_time = time.time()
    ping_results = {ip: {"success": 0, "timeout": 0} for ip in ips}
    irregularities = {ip: {"start": None, "end": None} for ip in ips}
    recent_pings = {ip: deque(maxlen=10) for ip in ips}

    with open("ping_log.csv", mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "timestamp", "ip", "total_requests", "successful", "timed_out",
            "timeout_percentage"
        ])

    while time.time() - start_time < duration:
        for ip in ips:
            reachable, response_time = ping(ip, timeout_duration)

            if reachable:
                ping_results[ip]["success"] += 1
                recent_pings[ip].append(response_time)
            else:
                ping_results[ip]["timeout"] += 1
                recent_pings[ip].append(timeout_duration)

            check_for_irregularities(ip, irregularities, recent_pings[ip], high_ping_threshold)
            display_real_time_results(ping_results)

            time.sleep(1)

        if (time.time() - start_time) % save_interval < 1:
            save_results_to_csv(ping_results)
            save_irregularities_to_csv(irregularities)

    return ping_results

def display_real_time_results(ping_results):
    """
    Display analysis of ping results in real-time.
    """
    sys.stdout.write("\033[H\033[J")  # Clear screen
    for ip, results in ping_results.items():
        total = results["success"] + results["timeout"]
        timeout_percentage = (results["timeout"] / total) * 100 if total > 0 else 0
        sys.stdout.write(f"IP: {RED}{ip}{RESET}\n")
        sys.stdout.write(f"  Total Requests: {YELLOW}{total}{RESET}\n")
        sys.stdout.write(f"  Successful: {YELLOW}{results['success']}{RESET}\n")
        sys.stdout.write(f"  Timed Out: {YELLOW}{results['timeout']}{RESET}\n")
        sys.stdout.write(f"  Timeout Percentage: {YELLOW}{timeout_percentage:.2f}%{RESET}\n\n")
    sys.stdout.flush()

def check_for_irregularities(ip, irregularities, recent_pings, high_ping_threshold):
    """
    Detect and track irregularities based on the average of recent pings.
    """
    if len(recent_pings) == 10:  # Check once we have 10 pings recorded
        avg_ping = sum(recent_pings) / len(recent_pings)
        if avg_ping > high_ping_threshold:
            # Start or extend the irregularity period
            if irregularities[ip]["start"] is None:
                irregularities[ip]["start"] = datetime.now()
            irregularities[ip]["end"] = datetime.now() + timedelta(minutes=5)
        elif irregularities[ip]["end"] and datetime.now() > irregularities[ip]["end"]:
            irregularities[ip]["start"], irregularities[ip]["end"] = None, None

def save_results_to_csv(ping_results):
    """
    Append ping results to a CSV file.
    """
    timestamp = datetime.now().isoformat()
    with open("ping_log.csv", mode="a", newline="") as file:
        writer = csv.writer(file)
        for ip, results in ping_results.items():
            total = results["success"] + results["timeout"]
            timeout_percentage = (results["timeout"] / total) * 100 if total > 0 else 0
            writer.writerow([
                timestamp, ip, total, results["success"], results["timeout"],
                f"{timeout_percentage:.2f}"
            ])

def save_irregularities_to_csv(irregularities):
    """
    Log irregularity periods to a separate CSV file with empty lines between periods.
    """
    timestamp = datetime.now().isoformat()
    with open("irregularities_log.csv", mode="a", newline="") as file:
        writer = csv.writer(file)
        for ip, period in irregularities.items():
            if period["start"] and period["end"]:
                writer.writerow([
                    timestamp, ip, period["start"], period["end"]
                ])
                writer.writerow([])  # Blank line after each period

def main():
    if len(sys.argv) < 5:
        print("[!] Usage: main.py <ip1> <ip2> ... <duration_seconds> <save_interval_seconds> <timeout_duration_ms> <high_ping_threshold_ms>")
        sys.exit()

    try:
        ips = sys.argv[1:-4]
        duration = int(sys.argv[-4])  # seconds
        save_interval = int(sys.argv[-3])  # seconds
        timeout_duration = int(sys.argv[-2])  # ms
        high_ping_threshold = int(sys.argv[-1])  # ms
    except ValueError:
        print("[!] Error: Please ensure all arguments are correctly specified.")
        sys.exit()

    print(f"Starting {PURPLE}ping test{RESET} for {YELLOW}{duration}{RESET} seconds with the following parameters:")
    print(f"  Target IPs: {RED}{', '.join(ips)}{RESET}")
    print(f"  Timeout duration: {YELLOW}{timeout_duration} ms{RESET}")
    print(f"  High ping threshold: {YELLOW}{high_ping_threshold} ms{RESET}")
    print(f"  Save interval: {YELLOW}{save_interval} seconds{RESET}")
    input(f"\n[!] Press {GREEN}Enter{RESET} to start the ping scan...")

    gather_ping_data(ips, duration, save_interval, timeout_duration, high_ping_threshold)
    print(f"\n[!] Ping scan completed {GREEN}successfully{RESET}!")

main()

