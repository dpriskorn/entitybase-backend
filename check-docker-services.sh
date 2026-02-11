#!/bin/bash
set -e

# Define color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Track overall status
overall_status=0

# Function to check running service health
check_running_service() {
    local container_name=$1
    local health_status=$(docker inspect --format='{{.State.Health.Status}}' "$container_name" 2>/dev/null || echo "not_found")

    if [ "$health_status" = "healthy" ]; then
        echo "✅ $container_name - healthy"
        return 0
    else
        echo "❌ $container_name - $health_status"
        return 1
    fi
}

# Function to check one-time setup job completion
check_completed_job() {
    local container_name=$1
    local state=$(docker inspect --format='{{.State.Status}}' "$container_name" 2>/dev/null || echo "not_found")
    local exit_code=$(docker inspect --format='{{.State.ExitCode}}' "$container_name" 2>/dev/null || echo "255")

    if [ "$state" = "exited" ] && [ "$exit_code" = "0" ]; then
        echo "✅ $container_name - completed successfully"
        return 0
    else
        echo "❌ $container_name - state: $state, exit code: $exit_code"
        return 1
    fi
}

# Check all services
check_running_service "mysql" || overall_status=1
check_running_service "minio" || overall_status=1
check_running_service "redpanda" || overall_status=1
check_running_service "idworker" || overall_status=1
check_running_service "json-dump-worker" || overall_status=1
check_running_service "ttl-dump-worker" || overall_status=1
check_completed_job "create-tables" || overall_status=1
check_completed_job "create-buckets" || overall_status=1

# Final status
if [ $overall_status -eq 0 ]; then
    echo "✅ All services healthy and ready"
else
    echo "❌ Some services are not healthy. Run ./run-api-local.sh first"
fi

exit $overall_status
