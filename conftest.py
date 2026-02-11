"""Root conftest to load environment variables from test.env."""

import os
from pathlib import Path

# Load test.env before any tests run
test_env = Path(__file__).parent / 'test.env'
if test_env.is_file():
    from dotenv import dotenv_values
    values = dotenv_values(test_env)
    for key, value in values.items():
        if value is not None:
            os.environ[key] = value
