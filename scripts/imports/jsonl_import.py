"""Import entities from JSONL file with parallel processing and resume capability."""

import asyncio
import json
import logging
import logging.handlers
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional
import httpx
from datetime import datetime

# Add parent directory to path for direct script execution
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

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
    logger.debug(f"Starting import for {entity_type} {entity_id}")

    for attempt in range(MAX_RETRIES):
        start_time = time.time()
        try:
            logger.debug(f"Attempt {attempt + 1}/{MAX_RETRIES} for {entity_id}")

            response = await session.post(
                f"{API_BASE_URL}/import",
                json=entity_data,
                headers={
                    "X-User-ID": "0",
                    "X-Edit-Summary": "Bulk import"
                },
                timeout=HTTP_TIMEOUT
            )

            elapsed = time.time() - start_time
            logger.debug(f"Response for {entity_id}: {response.status_code} in {elapsed:.2f}s")

            response.raise_for_status()

            logger.info(f"Successfully imported {entity_type} {entity_id} in {elapsed:.2f}s")
            state_manager.mark_success(entity_id, run_id)
            return 'success'

        except httpx.HTTPStatusError as e:
            elapsed = time.time() - start_time
            error_detail = e.response.text[:500] if e.response.text else "No response body"

            if e.response.status_code == 409:
                logger.info(f"Skipped {entity_id} (already exists)")
                state_manager.mark_skipped(entity_id, run_id)
                return 'skip'
            elif e.response.status_code == 400:
                error_msg = f"Validation error for {entity_id}: {error_detail}"
                logger.error(error_msg)
                state_manager.mark_failed(entity_id, run_id, error_msg)
                return 'failed'
            else:
                if attempt < MAX_RETRIES - 1:
                    retry_delay = RETRY_DELAY * (attempt + 1)
                    logger.warning(
                        f"HTTP {e.response.status_code} for {entity_id} "
                        f"(attempt {attempt + 1}/{MAX_RETRIES}), retrying in {retry_delay}s. "
                        f"Error: {error_detail}"
                    )
                    await asyncio.sleep(retry_delay)
                else:
                    error_msg = f"HTTP error {e.response.status_code} for {entity_id}: {error_detail}"
                    logger.error(error_msg)
                    state_manager.mark_failed(entity_id, run_id, error_msg)
                    return 'failed'

        except httpx.TimeoutException:
            if attempt < MAX_RETRIES - 1:
                retry_delay = RETRY_DELAY * (attempt + 1)
                logger.warning(
                    f"Timeout for {entity_id} (attempt {attempt + 1}/{MAX_RETRIES}), "
                    f"retrying in {retry_delay}s"
                )
                await asyncio.sleep(retry_delay)
            else:
                error_msg = f"Timeout for {entity_id} after {MAX_RETRIES} attempts"
                logger.error(error_msg)
                state_manager.mark_failed(entity_id, run_id, error_msg)
                return 'failed'

        except Exception as e:
            error_msg = f"Unexpected error importing {entity_id}: {type(e).__name__}: {e}"
            logger.error(error_msg)
            state_manager.mark_failed(entity_id, run_id, error_msg)
            return 'failed'

    return 'failed'


async def import_from_jsonl(
    jsonl_path: Path,
    concurrency: int = DEFAULT_CONCURRENCY,
    progress_interval: int = DEFAULT_PROGRESS_INTERVAL,
    api_url: str = API_BASE_URL,
    db_path: str = DB_PATH,
    cleanup: bool = False,
    auto_cleanup: bool = False,
    log_file: Optional[str] = None,
    log_level: str = "INFO"
):
    """Import entities from JSONL file.

    Args:
        jsonl_path: Path to JSONL file
        concurrency: Number of parallel imports (default: 10)
        progress_interval: Show detailed progress every N batches (default: 10)
        api_url: API base URL (default: http://localhost:8000/v1/entitybase)
        db_path: Path to SQLite state database (default: import_state.db)
        cleanup: Prompt to delete database after import completes
        auto_cleanup: Automatically delete database after import completes (no prompt)
        log_file: Path to log file (default: logs/import_YYYY-MM-DD_HH-MM-SS.log)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    run_id_for_log = 0

    class RunIDFilter(logging.Filter):
        def filter(self, record):
            record.run_id = f"Run#{run_id_for_log}" if run_id_for_log > 0 else "Run#?"
            return True

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File handler
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        log_path = logs_dir / f"import_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
        log_file = str(log_path)

    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(run_id)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    file_handler.addFilter(RunIDFilter())
    root_logger.addHandler(file_handler)

    logger.info(f"Starting import from {jsonl_path}")
    logger.info(f"Concurrency: {concurrency}")
    logger.info(f"API URL: {api_url}")
    logger.info(f"Database path: {db_path}")
    logger.info(f"Log file: {log_file}")
    logger.info(f"Log level: {log_level}")
    logger.debug(f"Command line arguments: {sys.argv}")

    logger.info(f"Starting import from {jsonl_path}")
    logger.info(f"Concurrency: {concurrency}")
    logger.info(f"API URL: {api_url}")

    from scripts.imports.state_manager import ImportStateManager

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

    state_manager = ImportStateManager(db_path)
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
    print(f"View stats:   python scripts/imports/cli.py status")
    print(f"Database:      {db_path}")
    print("="*70)

    if cleanup or auto_cleanup:
        db_file = Path(db_path)
        if auto_cleanup:
            if db_file.exists():
                db_file.unlink()
                logger.info(f"Deleted database: {db_path}")
                print(f"\nDatabase deleted: {db_path}")
        else:
            if db_file.exists():
                response = input(f"\nDelete database file '{db_path}'? [y/N]: ").strip().lower()
                if response == 'y' or response == 'yes':
                    db_file.unlink()
                    logger.info(f"Deleted database: {db_path}")
                    print(f"Database deleted: {db_path}")
                else:
                    print(f"Database kept: {db_path}")


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
    parser.add_argument(
        '--cleanup',
        action='store_true',
        help='Prompt to delete database after import completes'
    )
    parser.add_argument(
        '--auto-cleanup',
        action='store_true',
        help='Automatically delete database after import completes (no prompt)'
    )

    args = parser.parse_args()

    asyncio.run(import_from_jsonl(
        args.jsonl_file,
        concurrency=args.concurrency,
        progress_interval=args.progress_interval,
        api_url=args.api_url,
        db_path=args.db_path,
        cleanup=args.cleanup,
        auto_cleanup=args.auto_cleanup
    ))


if __name__ == '__main__':
    main()
