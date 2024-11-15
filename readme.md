# Network Overbooking Analyzer

![Contributors](https://img.shields.io/github/contributors/vrallis/ping-tool)
![Last Commit](https://img.shields.io/github/last-commit/vrallis/ping-tool)

This Python tool pings specified IP addresses continuously to help detect potential network overbooking issues caused by your ISP. It logs data on ping success rates, timeouts, and detects irregularity periods where network latency or timeouts might indicate network congestion.

I made this tool to diagnose issues with my own internet connecting and log them so I can provide evidence to my ISP. I hope it can help someone else too!

## Features

- Pings a list of IP addresses at regular intervals
- Logs ping success rates, timeouts, and timeout percentage to `ping_log.csv`
- Detects irregularity periods when:
  - Ping times are consecutively high (last 10 pings above threshold)
  - Ping requests time out
- Logs irregularity periods to `irregularities_log.csv` with a blank line separating each period for readability
- Fully configurable:
  - Set the duration of the test
  - Set the interval between each ping
  - Set the timeout threshold for ping requests and irregularity detection
  - Set the high ping threshold for irregularity detection

## Installation

Ensure Python 3 is installed. Clone this repository and ensure any dependencies are met.

## Usage

Run the script using the following command:

```bash
python3 main.py <ip1> <ip2> ... <duration_seconds> <save_interval_seconds> <timeout_duration_ms> <high_ping_threshold_ms>
```

## Example

### Unix Command Line

Run the script using the following command:

```bash
python3 main.py 1.1.1.1 8.8.8.8 3600 300 4000 150
```

### Windows Command Line

Run the script using the following command:

```cmd
python main.py 1.1.1.1 8.8.8.8 3600 300 4000 150
```

## Contributors

I would like to thank the following contributors for their help with this project:

- [@KafetzisThomas](https://github.com/KafetzisThomas)
