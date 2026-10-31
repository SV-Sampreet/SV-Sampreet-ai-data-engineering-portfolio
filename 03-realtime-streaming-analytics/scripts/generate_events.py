"""Script to generate sample transaction events."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.producer.event_generator import EventGenerator

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate sample transaction events")
    parser.add_argument("--count", type=int, default=100, help="Number of events to generate")
    parser.add_argument("--output", type=str, default="data/input/sample_events.jsonl", help="Output file path")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")

    args = parser.parse_args()

    # Create output directory
    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    # Generate events
    generator = EventGenerator(seed=args.seed)
    generator.generate_sample_file(args.output, count=args.count)

    print(f"Generated {args.count} events to {args.output}")
