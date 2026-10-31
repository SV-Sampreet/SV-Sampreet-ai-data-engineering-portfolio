"""Event generator for synthetic transaction data."""
import json
import random
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
import uuid
import logging

logger = logging.getLogger(__name__)


class EventGenerator:
    """Generates synthetic transaction events."""

    def __init__(self, seed: int = None):
        """Initialize event generator.

        Args:
            seed: Random seed for reproducibility
        """
        if seed is not None:
            random.seed(seed)

        self.categories = ["electronics", "clothing", "food", "travel", "entertainment", "health"]
        self.payment_methods = ["credit_card", "debit_card", "paypal", "bank_transfer"]
        self.statuses = ["completed", "pending", "failed"]

    def generate_event(self, timestamp: datetime = None) -> Dict[str, Any]:
        """Generate a single transaction event.

        Args:
            timestamp: Event timestamp (uses current time if None)

        Returns:
            Transaction event dictionary
        """
        if timestamp is None:
            timestamp = datetime.now()

        event = {
            "event_id": str(uuid.uuid4()),
            "timestamp": timestamp.isoformat(),
            "user_id": f"user_{random.randint(1, 100)}",
            "amount": round(random.uniform(10.0, 1000.0), 2),
            "category": random.choice(self.categories),
            "payment_method": random.choice(self.payment_methods),
            "status": random.choices(self.statuses, weights=[0.8, 0.15, 0.05])[0]
        }

        return event

    def generate_events(self, count: int, start_time: datetime = None) -> List[Dict[str, Any]]:
        """Generate multiple transaction events.

        Args:
            count: Number of events to generate
            start_time: Start timestamp for events

        Returns:
            List of transaction events
        """
        if start_time is None:
            start_time = datetime.now()

        events = []
        for i in range(count):
            # Spread events over time
            event_time = start_time + timedelta(seconds=i * 0.1)
            event = self.generate_event(event_time)
            events.append(event)

        logger.info(f"Generated {count} events")
        return events

    def generate_anomalous_event(self, timestamp: datetime = None, multiplier: float = 10.0) -> Dict[str, Any]:
        """Generate an anomalous transaction event (unusually large amount).

        Args:
            timestamp: Event timestamp
            multiplier: Multiplier for normal amount range

        Returns:
            Anomalous transaction event
        """
        if timestamp is None:
            timestamp = datetime.now()

        event = {
            "event_id": str(uuid.uuid4()),
            "timestamp": timestamp.isoformat(),
            "user_id": f"user_{random.randint(1, 100)}",
            "amount": round(random.uniform(10.0, 1000.0) * multiplier, 2),
            "category": random.choice(self.categories),
            "payment_method": random.choice(self.payment_methods),
            "status": "completed"
        }

        return event

    def save_events_to_file(self, events: List[Dict[str, Any]], file_path: str):
        """Save events to a JSONL file (one JSON per line).

        Args:
            events: List of events
            file_path: Output file path
        """
        with open(file_path, 'w') as f:
            for event in events:
                f.write(json.dumps(event) + '\n')

        logger.info(f"Saved {len(events)} events to {file_path}")

    def generate_sample_file(self, file_path: str, count: int = 100):
        """Generate a sample events file.

        Args:
            file_path: Output file path
            count: Number of events to generate
        """
        events = self.generate_events(count)
        self.save_events_to_file(events, file_path)
