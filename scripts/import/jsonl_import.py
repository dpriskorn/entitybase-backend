"""Import entities from JSONL file with parallel processing and resume capability."""

import asyncio
import json
import logging
import time
from pathlib import Path
from typing import Any, Dict
import httpx
from datetime import datetime

# Configuration
DEFAULT_CONCURRENCY = 10
DEFAULT_PROGRESS_INTERVAL = 10
API_BASE_URL = "http://localhost:8000/v1/entitybase"
DB_PATH = "import_state.db"

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 2.0

# Request timeout (seconds) - important for large entities
REQUEST_TIMEOUT = 300.0

# HTTP configuration
MAX_CONNECTIONS = 50
MAX_KEEPALIVE_CONNECTIONS = 20
HTTP_TIMEOUT = httpx.Timeout(REQUEST_TIMEOUT, connect=30.0)
LIMITS = httpx.Limits(
    max_connections=MAX_CONNECTIONS,
    max_keepalive_connections=MAX_KEEPALIVE_CONNECTIONS
)

logger = logging.getLogger(__name__)


class ProgressTracker:
    """Track import progress with rate calculation."""

    def __init__(self, total: int):
        self.total = total
        self.processed = 0
        self.start_time = time.time()
        self.last_update = self.start_time
        self.last_processed = 0

    def update(self, batch_size: int) -> Dict[str, Any]:
        """Update progress after processing a batch."""
        self.processed += batch_size
        now = time.time()
        elapsed = now - self.start_time
        batch_elapsed = now - self.last_update

        rate_per_second = 0.0
        rate_per_minute = 0.0
        rate_per_hour = 0.0

        if elapsed > 0:
            rate_per_second = self.processed / elapsed
            rate_per_minute = rate_per_second * 60
            rate_per_hour = rate_per_second * 3600

            batch_rate = batch_size / batch_elapsed if batch_elapsed > 0 else 0
        else:
            batch_rate = 0

        self.last_update = now
        self.last_processed = self.processed

        eta_seconds = None
        eta_formatted = "N/A"

        if rate_per_second > 0:
            remaining = self.total - self.processed
            eta_seconds = remaining / rate_per_second
            eta_formatted = self._format_eta(eta_seconds)

        return {
            'processed': self.processed,
            'total': self.total,
            'percent': (self.processed / self.total) * 100 if self.total > 0 else 0,
            'rate_per_second': rate_per_second,
            'rate_per_minute': rate_per_minute,
            'rate_per_hour': rate_per_hour,
            'elapsed_seconds': elapsed,
            'eta_seconds': eta_seconds,
            'eta_formatted': eta_formatted
        }

    def _format_eta(self, seconds: float) -> str:
        """Format ETA in human-readable format."""
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            mins = seconds / 60
            return f"{mins:.1f}m"
        else:
            hours = seconds / 3600
            mins = (seconds % 3600) / 60
            return f"{hours:.0f}h {mins:.0f}m"


def format_rate(rate_per_minute: float) -> str:
    """Format rate with appropriate unit."""
    if rate_per_minute < 1:
        rate_per_hour = rate_per_minute * 60
        return f"{rate_per_hour:.2f}/hour"
    elif rate_per_minute >= 60:
        rate_per_second = rate_per_minute / 60
        return f"{rate_per_second:.1f}/sec"
    else:
        return f"{rate_per_minute:.1f}/min"


def format_elapsed(seconds: float) -> str:
    """Format elapsed time as HH:MM:SS."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def print_progress_compact(batch_num: int, progress: Dict[str, Any]):
    """Print compact one-line progress."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    rate = format_rate(progress['rate_per_minute'])
    eta = progress['eta_formatted']
    print(f"[{timestamp}] Batch {batch_num:4d}: "
          f"{progress['processed']:8,} / {progress['total']:8,} "
          f"({progress['percent']:5.1f}%) | {rate} | ETA: {eta}")


def print_progress_detailed(batch_num: int, progress: Dict[str, Any]):
    """Print detailed multi-line progress report."""
    elapsed = format_elapsed(progress['elapsed_seconds'])
    print(f"\n{'='*70}")
    print(f"Progress Report - Batch {batch_num}")
    print(f"{'='*70}")
    print(f"Entities:      {progress['processed']:,} / {progress['total']:,} "
          f"({progress['percent']:.2f}%)")
    print(f"Elapsed:       {elapsed}")
    print(f"Rate:          {progress['rate_per_minute']:.1f} entities/minute "
          f"({progress['rate_per_hour']:,.0f}/hour)")
    print(f"ETA:           {progress['eta_formatted']}")
    print(f"{'='*70}")


async def import_entity(
    session: httpx.AsyncClient,
    entity_id: str,
    entity_data: Dict[str, Any],
    entity_type: str,
    state_manager,
    run_id: int
) -> str:
    """Import a single entity with retry logic.

    Returns:
        'success', 'skip', or 'failed'
    """
    for attempt in range(MAX_RETRIES):
        try:
            response = await session.post(
                f"{API_BASE_URL}/import",
                json=entity_data,
                headers={
                    "X-User-ID": "0",
                    "X-Edit-Summary": "Bulk import"
                },
                timeout=HTTP_TIMEOUT
            )
            response.raise_for_status()

            state_manager.mark_success(entity_id, run_id)
            return 'success'

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 409:
                state_manager.mark_skipped(entity_id, run_id)
                return 'skip'
            elif e.response.status_code == 400:
                error_msg = f"Validation error for {entity_id}: {e.response.text[:200]}"
                logger.error(error_msg)
                state_manager.mark_failed(entity_id, run_id, error_msg)
                return 'failed'
            else:
                if attempt < MAX_RETRIES - 1:
                    logger.warning(f"Retry {attempt + 1}/{MAX_RETRIES} for {entity_id}: {e.response.status_code}")
                    await asyncio.sleep(RETRY_DELAY * (attempt + 1))
                else:
                    error_msg = f"HTTP error for {entity_id}: {e.response.status_code}"
                    logger.error(error_msg)
                    state_manager.mark_failed(entity_id, run_id, error_msg)
                    return 'failed'

        except httpx.TimeoutException:
            if attempt < MAX_RETRIES - 1:
                logger.warning(f"Timeout for {entity_id}, retry {attempt + 1}/{MAX_RETRIES}")
                await asyncio.sleep(RETRY_DELAY * (attempt + 1))
            else:
                error_msg = f"Timeout for {entity_id}"
                logger.error(error_msg)
                state_manager.mark_failed(entity_id, run_id, error_msg)
                return 'failed'

        except Exception as e:
            error_msg = f"Error importing {entity_id}: {e}"
            logger.error(error_msg)
            state_manager.mark_failed(entity_id, run_id, error_msg)
            return 'failed'

    return 'failed'


async def import_from_jsonl(
    jsonl_path: Path,
    concurrency: int = DEFAULT_CONCURRENCY,
    progress_interval: int = DEFAULT_PROGRESS_INTERVAL,
    api_url: str = API_BASE_URL
):
    """Import entities from JSONL file.

    Args:
        jsonl_path: Path to JSONL file
        concurrency: Number of parallel imports (default: 10)
        progress_interval: Show detailed progress every N batches (default: 10)
        api_url: API base URL (default: http://localhost:8000/v1/entitybase)
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    logger.info(f"Starting import from {jsonl_path}")
    logger.info(f"Concurrency: {concurrency}")
    logger.info(f"API URL: {api_url}")

    from scripts.import.state_manager import ImportStateManager

    print("\nParsing JSONL file...")
    entities = []
    with open(jsonl_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            if line.endswith(','):
                line = line[:-1]
            entity = json.loads(line)
            entities.append((line_num, entity))

    print(f"Parsed {len(entities):,} entities from file")

    state_manager = ImportStateManager(DB_PATH)
    run_id = state_manager.create_run(
        jsonl_file=str(jsonl_path),
        total_entities=len(entities),
        concurrency=concurrency,
        api_url=f"{api_url}/import"
    )
    print(f"Created run #{run_id}")

    print("Loading entities into database...")
    state_manager.add_entities(run_id, [e for _, e in entities])

    tracker = ProgressTracker(total=len(entities))
    success_count = 0
    fail_count = 0
    skip_count = 0

    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT, limits=LIMITS) as session:
        batch_num = 0
        while True:
            batch = state_manager.get_next_batch(run_id, limit=concurrency)

            if not batch:
                print("\n" + "="*70)
                print("IMPORT COMPLETE")
                print("="*70)
                break

            batch_num += 1
            progress = tracker.update(len(batch))

            if batch_num % progress_interval == 0 or batch_num == 1:
                print_progress_detailed(batch_num, progress)
            else:
                print_progress_compact(batch_num, progress)

            tasks = [
                import_entity(
                    session,
                    record.entity_id,
                    {},
                    record.entity_type,
                    state_manager,
                    run_id
                )
                for record in batch
            ]
            results = await asyncio.gather(*tasks)

            for result in results:
                if result == 'skip':
                    skip_count += 1
                elif result == 'success':
                    success_count += 1
                else:
                    fail_count += 1

            if batch_num % 10 == 0:
                state_manager.finish_run(run_id, success_count, fail_count, skip_count)

    state_manager.finish_run(run_id, success_count, fail_count, skip_count)

    final_progress = tracker.update(0)
    print(f"\nTotal:        {len(entities):,}")
    print(f"Success:      {success_count:,}")
    print(f"Failed:       {fail_count:,}")
    print(f"Skipped:      {skip_count:,}")
    print(f"Run ID:       {run_id}")
    print(f"View stats:   python scripts/import/cli.py status")
    print(f"Database:      {DB_PATH}")
    print("="*70)


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Import entities from JSONL file')
    parser.add_argument('jsonl_file', type=Path, help='Path to JSONL file')
    parser.add_argument(
        '--concurrency', '-c',
        type=int,
        default=DEFAULT_CONCURRENCY,
        help=f'Number of parallel imports (default: {DEFAULT_CONCURRENCY})'
    )
    parser.add_argument(
        '--progress-interval', '-p',
        type=int,
        default=DEFAULT_PROGRESS_INTERVAL,
        help=f'Show detailed progress every N batches (default: {DEFAULT_PROGRESS_INTERVAL})'
    )
    parser.add_argument(
        '--api-url',
        type=str,
        default=API_BASE_URL,
        help=f'API base URL (default: {API_BASE_URL})'
    )
    parser.add_argument(
        '--db-path',
        type=str,
        default=DB_PATH,
        help=f'Path to SQLite state database (default: {DB_PATH})'
    )

    args = parser.parse_args()

    global DB_PATH
    DB_PATH = args.db_path

    asyncio.run(import_from_jsonl(
        args.jsonl_file,
        concurrency=args.concurrency,
        progress_interval=args.progress_interval,
        api_url=args.api_url
    ))


if __name__ == '__main__':
    main()
