#!/usr/bin/env python3
import os
import sys
import time
import json
import requests


def read_port_file(port_file: str = "/tmp/arche_registry.port") -> int:
    try:
        with open(port_file, "r") as f:
            return int(f.read().strip())
    except Exception:
        return 5001


def register_instance(base_url: str, name: str, capabilities):
    payload = {
        "instance_id": name,
        "capabilities": {"Cognitive toolS": capabilities},
        "address": f"local:{os.getpid()}"
    }
    r = requests.post(f"{base_url}/register", json=payload, timeout=5)
    r.raise_for_status()
    data = r.json()
    return data.get("instance_id", name)


def get_roadmap(base_url: str):
    r = requests.get(f"{base_url}/orchestrator/roadmap", timeout=5)
    r.raise_for_status()
    return r.json()


def assign_task(base_url: str, task_id: str):
    return requests.post(f"{base_url}/orchestrator/tasks/{task_id}/assign", timeout=5)


def complete_task(base_url: str, task_id: str, result: str, confidence: float = 0.99):
    payload = {
        "result": result,
        "iar": {"confidence": confidence}
    }
    r = requests.post(f"{base_url}/tasks/{task_id}/complete", json=payload, timeout=5)
    r.raise_for_status()
    return r.json()


def main():
    port = int(os.environ.get("ARCHE_PORT", read_port_file()))
    base_url = os.environ.get("ARCHE_BASE_URL", f"http://127.0.0.1:{port}")
    instance_name = os.environ.get("ARCHE_WORKER_NAME", "code-executor-worker")
    capability = os.environ.get("ARCHE_CAPABILITY", "Code executoR")

    print(f"[worker] Connecting to {base_url} as '{instance_name}' with capability '{capability}'")
    try:
        internal_id = register_instance(base_url, instance_name, [capability])
        print(f"[worker] Registered as internal id: {internal_id}")
    except requests.RequestException as e:
        print(f"[worker] Registration failed: {e}")
        sys.exit(1)

    # Poll loop
    while True:
        try:
            tasks = get_roadmap(base_url)
        except requests.RequestException as e:
            print(f"[worker] roadmap error: {e}")
            time.sleep(2)
            continue

        # Prefer tasks already assigned to this instance; otherwise try to assign pending ones
        handled = False
        for t in tasks:
            if t.get("status") == "assigned" and t.get("assigned_to"):
                if t["assigned_to"] == internal_id:
                    print(f"[worker] Executing assigned task {t['task_id']}: {t['description']}")
                    try:
                        res = complete_task(base_url, t["task_id"], result=f"executed:{t['required_capability']}")
                        print(f"[worker] Completed {t['task_id']}: {res}")
                        handled = True
                    except requests.RequestException as e:
                        print(f"[worker] completion error: {e}")
            elif t.get("status") == "pending" and t.get("required_capability") == capability:
                # Try to get it assigned
                try:
                    assign_task(base_url, t["task_id"])
                except requests.RequestException as e:
                    print(f"[worker] assign error: {e}")

        # Sleep briefly
        time.sleep(1.0 if handled else 2.0)


if __name__ == "__main__":
    main()








