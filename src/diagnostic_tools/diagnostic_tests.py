import time
import random
import shutil
import socket


def random_bool_delay(logger=None, environment=None):
    """Simulate a random success/failure with a delay."""

    if logger:
        logger("Simulating a random test...")
    time.sleep(2)
    return random.choice([True, False])


def check_network(logger=None, environment=None):
    """Check if the internet connection is working."""
    time.sleep(1)
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False


def check_disk_space(logger=None, environment=None):
    """Check if there's enough disk space (at least 10%)."""
    time.sleep(1)
    total, used, free = shutil.disk_usage("/")
    percent_free = free / total * 100
    return percent_free > 10


def check_database(logger=None, environment=None):
    """Simulate checking database connection."""
    time.sleep(1)
    return random.choice([True, False])


def check_hardware(logger=None, environment=None):
    """Simulate hardware status check."""
    time.sleep(1)
    return random.choice([True, False])


def validate_configurations(logger=None, environment=None):
    """Simulate configuration validation."""
    time.sleep(1)
    return random.choice([True, False])
