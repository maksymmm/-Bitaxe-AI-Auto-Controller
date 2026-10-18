#!/usr/bin/env python3
"""Bitaxe monitoring and profile advisor. DRY RUN by default."""
import logging
import os
import time
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("bitaxe")
HOST = os.getenv("BITAXE_IP", "127.0.0.1")
INTERVAL = max(30, int(os.getenv("CHECK_INTERVAL", "300")))
ALLOW_WRITES = os.getenv("ALLOW_DEVICE_WRITES", "false").lower() == "true"
PROFILES = {
    "emergency": (550, 1000),
    "cool": (575, 1020),
    "eco": (600, 1060),
    "normal": (612, 1080),
    "turbo": (625, 1100),
}
# Example thresholds only; adjust to your device's verified safe limits.
def choose_profile(temp):
    if temp >= 70: return "emergency"
    if temp >= 65: return "cool"
    if temp >= 60: return "eco"
    if temp >= 55: return "normal"
    return "turbo"

def read_status():
    response = requests.get(f"http://{HOST}/api/system/info", timeout=10)
    response.raise_for_status()
    return response.json()

def main():
    if ALLOW_WRITES:
        raise SystemExit("Automatic writes disabled in this community preview: review firmware and hardware limits first.")
    log.info("Monitoring %s in DRY RUN mode", HOST)
    while True:
        try:
            data = read_status()
            temp = data.get("temp")
            if temp is None:
                temp = data.get("temperature")
            if temp is None:
                log.warning("No chip temperature field in AxeOS response; inspect your firmware API.")
            else:
                profile = choose_profile(float(temp))
                log.info("Chip %.1f C; suggested profile %s (not applied); hashrate=%s", float(temp), profile, data.get("hashRate", "n/a"))
        except (requests.RequestException, ValueError, TypeError) as exc:
            log.error("Monitoring error: %s", exc)
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
