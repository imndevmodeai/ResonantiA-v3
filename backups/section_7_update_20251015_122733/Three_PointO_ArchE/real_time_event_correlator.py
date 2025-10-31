"""
=====================================================
Real-Time Event Correlator (real_time_event_correlator.py)
=====================================================

As Above: The Principle of the Watchful Gaze
---------------------------------------------
In any living system, awareness is the constant, silent observation of flow. This module embodies the universal principle of the Watchful Gaze: the ability to perceive a massive, high-velocity stream of raw data and instantly recognize the fleeting patterns of significance. It abstracts the function of an IP camera system into a higher wisdom—it is not about watching a place, but about watching *anything*, discerning the signal from the noise, and detecting the anomalies and correlations that define reality in real-time.

So Below: The Operational Logic
-------------------------------
This module provides the `RealTimeEventCorrelator`, a generic engine for processing streams of event data. It is designed to be highly extensible, allowing custom "Detector" agents to be plugged in to identify specific patterns (e.g., fraud in transactions, intrusions in network logs, specific objects in video frames). It uses an asynchronous architecture to handle high-throughput streams efficiently.
"""

import asyncio
import time
import random
from collections import deque
from typing import Dict, Any, List, Callable, Coroutine

class BaseDetector:
    """Base class for a detector agent that analyzes event streams."""
    def __init__(self, name: str):
        self.name = name

    async def analyze(self, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyzes a single event and returns a list of detected anomalies or patterns.
        
        Returns:
            A list of findings. Each finding is a dictionary. An empty list means nothing was found.
        """
        raise NotImplementedError

class AnomalyDetector(BaseDetector):
    """Detects events that deviate from a statistical norm."""
    def __init__(self, field_to_monitor: str, threshold: float = 3.0):
        super().__init__(name=f"AnomalyDetector({field_to_monitor})")
        self.field = field_to_monitor
        self.threshold_std_dev = threshold
        self.history = deque(maxlen=100) # Store last 100 values
        self.mean = 0.0
        self.std_dev = 0.0

    async def analyze(self, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        value = event.get(self.field)
        if not isinstance(value, (int, float)):
            return []

        findings = []
        if len(self.history) > 20: # Need enough data to be meaningful
            if abs(value - self.mean) > self.threshold_std_dev * self.std_dev:
                findings.append({
                    "pattern_name": "Statistical Anomaly",
                    "detector": self.name,
                    "field": self.field,
                    "value": value,
                    "mean": round(self.mean, 2),
                    "std_dev": round(self.std_dev, 2),
                    "severity": "high"
                })

        # Update stats
        self.history.append(value)
        self.mean = sum(self.history) / len(self.history)
        variance = sum([(x - self.mean) ** 2 for x in self.history]) / len(self.history)
        self.std_dev = variance ** 0.5
        
        return findings

class SequenceDetector(BaseDetector):
    """Detects a specific sequence of events."""
    def __init__(self, sequence: List[Callable[[Dict[str, Any]], bool]], window_seconds: int = 10):
        super().__init__(name="SequenceDetector")
        self.sequence_checkers = sequence
        self.window_seconds = window_seconds
        self.potential_sequence = []

    async def analyze(self, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        current_time = time.time()
        
        # Prune old events from our potential sequence
        self.potential_sequence = [
            e for e in self.potential_sequence if (current_time - e['timestamp']) < self.window_seconds
        ]
        
        next_step_index = len(self.potential_sequence)
        
        if next_step_index < len(self.sequence_checkers):
            # Check if the current event matches the next required step
            if self.sequence_checkers[next_step_index](event):
                self.potential_sequence.append({"event": event, "timestamp": current_time})
                
                # Check if the sequence is now complete
                if len(self.potential_sequence) == len(self.sequence_checkers):
                    finding = {
                        "pattern_name": "Specific Event Sequence Detected",
                        "detector": self.name,
                        "events": [e['event'] for e in self.potential_sequence],
                        "severity": "critical"
                    }
                    self.potential_sequence = [] # Reset for next detection
                    return [finding]
        else:
            # This shouldn't happen, but reset if it does
            self.potential_sequence = []

        return []


class RealTimeEventCorrelator:
    """Orchestrates the analysis of a high-volume event stream."""
    def __init__(self, detectors: List[BaseDetector]):
        self.detectors = detectors
        self.event_queue = asyncio.Queue()
        self.running = False

    async def push_event(self, event: Dict[str, Any]):
        """Asynchronously add an event to the processing queue."""
        await self.event_queue.put(event)

    async def _worker(self):
        """The core worker task that processes events from the queue."""
        while self.running:
            try:
                event = await self.event_queue.get()
                
                # Run all detectors in parallel on the event
                analysis_tasks = [detector.analyze(event) for detector in self.detectors]
                all_findings = await asyncio.gather(*analysis_tasks)
                
                for findings in all_findings:
                    if findings:
                        for finding in findings:
                            # In a real system, this would emit to a logging/alerting system
                            print(f"ALERT: {finding}")

                self.event_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in correlator worker: {e}")

    async def start(self, num_workers: int = 2):
        """Starts the event correlator workers."""
        self.running = True
        self.workers = [asyncio.create_task(self._worker()) for _ in range(num_workers)]
        print(f"RealTimeEventCorrelator started with {num_workers} workers.")

    async def stop(self):
        """Stops the event correlator workers."""
        self.running = False
        for worker in self.workers:
            worker.cancel()
        await asyncio.gather(*self.workers, return_exceptions=True)
        print("RealTimeEventCorrelator stopped.")


async def main():
    # --- Example Usage ---
    # Define detectors based on the "So Below" logic
    
    # 1. Anomaly detection for financial transactions
    fraud_detector = AnomalyDetector(field_to_monitor="amount_usd", threshold=3.5)
    
    # 2. Sequence detection for a specific user behavior (e.g., login -> failed_pw -> pw_reset)
    login_sequence = [
        lambda e: e.get("event_type") == "login_success",
        lambda e: e.get("event_type") == "password_change_failed",
        lambda e: e.get("event_type") == "password_reset_request"
    ]
    hacker_detector = SequenceDetector(sequence=login_sequence, window_seconds=60)
    
    # Initialize the Correlator with our detectors
    correlator = RealTimeEventCorrelator(detectors=[fraud_detector, hacker_detector])
    
    # Start the processing engine
    await correlator.start()

    # --- Simulate a stream of events ---
    print("\n--- Simulating event stream... ---\n")
    async def event_generator():
        for i in range(200):
            # Normal transaction
            await correlator.push_event({"event_type": "transaction", "amount_usd": random.uniform(10, 200)})
            
            # Simulate a hacking attempt sequence
            if i == 50:
                await correlator.push_event({"event_type": "login_success", "user": "test"})
            if i == 52:
                await correlator.push_event({"event_type": "password_change_failed", "user": "test"})
            if i == 53:
                await correlator.push_event({"event_type": "password_reset_request", "user": "test"})
            
            # Simulate a fraudulent transaction
            if i == 150:
                await correlator.push_event({"event_type": "transaction", "amount_usd": 5000.00})

            await asyncio.sleep(0.05)

    generator_task = asyncio.create_task(event_generator())
    await generator_task

    # Allow some time for events to be processed
    await asyncio.sleep(2)

    # Stop the correlator
    await correlator.stop()

if __name__ == "__main__":
    asyncio.run(main())
