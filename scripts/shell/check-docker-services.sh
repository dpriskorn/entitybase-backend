#!/bin/bash
cd "$(dirname "$0")/../.."
set -e

# Define color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track overall status
overall_status=0
clean_connections=false

# Parse arguments
for arg in "$@"; do
    case $arg in
        --clean-connections)
            clean_connections=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --clean-connections  Kill idle MySQL connections before checking"
            echo "  -h, --help           Show this help message"
            exit 0
            ;;
    esac
done

# Load test environment variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
if [ -f "$PROJECT_ROOT/test.env" ]; then
    source "$PROJECT_ROOT/test.env"
else
    echo -e "${RED}❌ test.env not found at $PROJECT_ROOT/test.env${NC}"
    exit 1
fi

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

# Check MySQL connectivity and connection count
check_mysql_connectivity() {
    # Use docker exec to run mysql inside the container
    if ! docker exec mysql mysql -u"$VITESS_USER" ${VITESS_PASSWORD:+-p"$VITESS_PASSWORD"} -e "SELECT 1" &>/dev/null; then
        echo -e "${RED}❌ mysql - connection failed${NC}"
        return 1
    fi
    echo -e "${GREEN}✅ mysql - accepting connections${NC}"

    # Check connection count
    local conn_info
    conn_info=$(docker exec mysql mysql -u"$VITESS_USER" ${VITESS_PASSWORD:+-p"$VITESS_PASSWORD"} -N -e "SHOW STATUS LIKE 'Threads_connected'" 2>/dev/null)
    local current_connections=$(echo "$conn_info" | awk '{print $2}')

    if [ -n "$current_connections" ]; then
        # E2E tests use pool_size=5 + max_overflow=5 = 10 connections
        local max_test_pool=10
        local warning_threshold=8

        if [ "$current_connections" -ge "$max_test_pool" ]; then
            echo -e "${RED}❌ mysql - $current_connections/$max_test_pool connections (pool exhausted!)${NC}"
            echo -e "${YELLOW}   Run: $0 --clean-connections  or  docker restart mysql${NC}"
            return 1
        elif [ "$current_connections" -ge "$warning_threshold" ]; then
            echo -e "${YELLOW}⚠️  mysql - $current_connections/$max_test_pool connections (high usage)${NC}"
        else
            echo -e "${GREEN}✅ mysql - $current_connections connections active${NC}"
        fi
    fi

    return 0
}

# Clean idle MySQL connections
clean_idle_connections() {
    echo -e "${YELLOW}🧹 Cleaning idle MySQL connections...${NC}"
    
    # Get current connection count before cleanup
    local before_count
    before_count=$(docker exec mysql mysql -u"$VITESS_USER" ${VITESS_PASSWORD:+-p"$VITESS_PASSWORD"} -N -e "SHOW STATUS LIKE 'Threads_connected'" 2>/dev/null | awk '{print $2}')
    echo "   Before: $before_count connections"
    
    # Kill idle connections (Sleep state) that are older than 1 second
    # This targets connections from crashed/leaked test runs
    docker exec mysql mysql -u"$VITESS_USER" ${VITESS_PASSWORD:+-p"$VITESS_PASSWORD"} -N -e "
        SELECT CONCAT('KILL ', id, ';') 
        FROM information_schema.processlist 
        WHERE Command = 'Sleep' 
        AND Time > 1
        AND User = '$VITESS_USER'
    " 2>/dev/null | docker exec -i mysql mysql -u"$VITESS_USER" ${VITESS_PASSWORD:+-p"$VITESS_PASSWORD"} 2>/dev/null || true
    
    # Get connection count after cleanup
    local after_count
    after_count=$(docker exec mysql mysql -u"$VITESS_USER" ${VITESS_PASSWORD:+-p"$VITESS_PASSWORD"} -N -e "SHOW STATUS LIKE 'Threads_connected'" 2>/dev/null | awk '{print $2}')
    
    local cleaned=$((before_count - after_count))
    if [ "$cleaned" -gt 0 ]; then
        echo -e "${GREEN}   Cleaned $cleaned idle connections${NC}"
    fi
    echo -e "${GREEN}   After: $after_count connections${NC}"
}

# Clean connections if requested (do this before other checks)
if [ "$clean_connections" = true ]; then
    clean_idle_connections
fi

# Check all services
check_running_service "mysql" || overall_status=1
check_running_service "minio" || overall_status=1
check_running_service "redpanda" || overall_status=1
check_running_service "idworker" || overall_status=1
check_running_service "json-dump-worker" || overall_status=1
check_running_service "ttl-dump-worker" || overall_status=1
check_completed_job "create-tables" || overall_status=1
check_completed_job "create-buckets" || overall_status=1

check_mysql_connectivity || overall_status=1

# Final status
if [ $overall_status -eq 0 ]; then
    echo "✅ All services healthy and ready"
else
    echo "❌ Some services are not healthy. Run ./run-api-local.sh first"
fi

exit $overall_status
