#!/bin/bash

# Prune volumes for clean DB state
docker volume prune -f -y >/dev/null 2>&1

# Run tests in isolated environment and capture output
output=$(docker compose -f docker-compose.test.yml up --abort-on-container-exit --remove-orphans 2>&1)
exit_code=$?

# Extract failure count from test-runner logs
echo "Full output:"
echo "$output"
test_logs=$(echo "$output" | sed -n '/test-runner |/,$p' | head -n 50)
if echo "$test_logs" | grep -q "failed"; then
  failed_count=$(echo "$test_logs" | grep -oE '[0-9]+ failed' | grep -oE '[0-9]+' | head -1)
  echo "${failed_count:-0}"
elif [ $exit_code -ne 0 ]; then
  echo "Error: Tests failed to run (exit code $exit_code). Check Docker setup."
  echo "Last 20 lines of output:"
  echo "$output" | tail -20
  exit 1
else
  echo "0"
fi

# Clean up
docker compose -f docker-compose.test.yml down --volumes --remove-orphans >/dev/null 2>&1