"""
Pytest configuration and shared fixtures for Mother AI tests.
"""
import pytest
from datetime import datetime, timedelta
from hypothesis import settings

# Configure Hypothesis for property-based testing
settings.register_profile("ci", max_examples=1000, deadline=None)
settings.register_profile("dev", max_examples=100, deadline=None)
settings.register_profile("debug", max_examples=10, verbosity=2, deadline=None)

# Use dev profile by default
settings.load_profile("dev")
