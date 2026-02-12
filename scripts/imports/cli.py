"""CLI interface for import state database."""

import argparse
import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = "import_state.db"


def cmd_status(args):
    """Show current import status."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    cursor = conn.execute("""
        SELECT * FROM import_runs
        ORDER BY run_id DESC
        LIMIT 1
    """)
    run = cursor.fetchone()

    if not run:
        print("No import runs found")
        return

    print(f"\n{'='*60}")
    print(f"Import Run #{run['run_id']}")
    print(f"{'='*60}")
    print(f"Started:   {run['start_time']}")
    print(f"Ended:     {run['end_time'] or 'IN PROGRESS'}")
    print(f"File:      {run['jsonl_file']}")
    print(f"API URL:   {run['api_url']}")
    print(f"Concurrency:{run['concurrency']}")
    print(f"\nStatistics:")
    print(f"  Total:    {run['total_entities']}")
    print(f"  Success:  {run['success_count']}")
    print(f"  Failed:   {run['fail_count']}")
    print(f"  Skipped:  {run['skip_count']}")

    cursor = conn.execute("""
        SELECT entity_type, status, COUNT(*) as count
        FROM entities
        WHERE run_id = ?
        GROUP BY entity_type, status
        ORDER BY entity_type, status
    """, (run['run_id'],))

    print(f"\nBreakdown by type:")
    current_type = None
    for row in cursor.fetchall():
        if row['entity_type'] != current_type:
            current_type = row['entity_type']
            print(f"\n  {current_type.upper()}:")
        status_icon = {
            'pending': '⏳',
            'processing': '🔄',
            'success': '✓',
            'failed': '✗',
            'skipped': '○'
        }.get(row['status'], '?')
        print(f"    {status_icon} {row['status']:12} {row['count']:8}")


def cmd_list(args):
    """List entities by status."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    filters = []
    params = []

    if args.status:
        filters.append("status = ?")
        params.append(args.status)

    if args.type:
        filters.append("entity_type = ?")
        params.append(args.type)

    if args.run_id:
        filters.append("run_id = ?")
        params.append(args.run_id)

    where_clause = " AND ".join(filters) if filters else "1=1"

    cursor = conn.execute(f"""
        SELECT entity_id, entity_type, status, line_number,
               last_attempt, error_message
        FROM entities
        WHERE {where_clause}
        ORDER BY line_number
        LIMIT ?
    """, params + [args.limit])

    print(f"\n{'='*80}")
    print(f"Entities matching: {', '.join(filters) if filters else 'all'}")
    print(f"{'='*80}")

    for row in cursor.fetchall():
        status_icon = {
            'pending': '⏳',
            'processing': '🔄',
            'success': '✓',
            'failed': '✗',
            'skipped': '○'
        }.get(row['status'], '?')
        print(f"{status_icon} {row['entity_id']:12} {row['status']:12} Line {row['line_number']:6} {row['last_attempt']}")
        if row['error_message']:
            print(f"   Error: {row['error_message'][:70]}")


def cmd_stats(args):
    """Show overall statistics."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    cursor = conn.execute("""
        SELECT
            COUNT(DISTINCT run_id) as total_runs,
            SUM(total_entities) as total_entities,
            SUM(success_count) as total_success,
            SUM(fail_count) as total_failed,
            SUM(skip_count) as total_skipped,
            MIN(start_time) as first_run,
            MAX(end_time) as last_run
        FROM import_runs
    """)
    stats = cursor.fetchone()

    print(f"\n{'='*60}")
    print("Overall Import Statistics")
    print(f"{'='*60}")
    print(f"Total runs:        {stats['total_runs'] or 0}")
    print(f"Total entities:     {stats['total_entities'] or 0}")
    print(f"Successfully imported:{stats['total_success'] or 0}")
    print(f"Failed:            {stats['total_failed'] or 0}")
    print(f"Skipped:           {stats['total_skipped'] or 0}")
    print(f"First run:        {stats['first_run'] or 'N/A'}")
    print(f"Last run:         {stats['last_run'] or 'IN PROGRESS'}")

    if stats['total_entities']:
        rate = (stats['total_success'] / stats['total_entities']) * 100
        print(f"Success rate:      {rate:.1f}%")


def cmd_reset(args):
    """Reset import state."""
    conn = sqlite3.connect(DB_PATH)

    if args.run_id:
        print(f"Resetting run #{args.run_id}...")
        conn.execute("DELETE FROM entities WHERE run_id = ?", (args.run_id,))
        conn.execute("DELETE FROM import_runs WHERE run_id = ?", (args.run_id,))
    else:
        confirm = input("This will delete ALL import state. Type 'yes' to confirm: ")
        if confirm.lower() != 'yes':
            print("Cancelled")
            return

        print("Resetting all import state...")
        conn.execute("DELETE FROM entities")
        conn.execute("DELETE FROM import_runs")

    conn.commit()
    print("Done")


def cmd_export(args):
    """Export entities to CSV."""
    import csv

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    filters = []
    params = []

    if args.status:
        filters.append("status = ?")
        params.append(args.status)

    where_clause = " AND ".join(filters) if filters else "1=1"

    cursor = conn.execute(f"""
        SELECT * FROM entities
        WHERE {where_clause}
        ORDER BY line_number
    """, params)

    with open(args.file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['entity_id', 'entity_type', 'status', 'line_number',
                      'last_attempt', 'retry_count', 'error_message'])
        for row in cursor.fetchall():
            writer.writerow(row)

    print(f"Exported {cursor.rowcount} entities to {args.file}")


def cmd_runs(args):
    """List all import runs."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    cursor = conn.execute("""
        SELECT run_id, start_time, end_time, jsonl_file,
               total_entities, success_count, fail_count, skip_count
        FROM import_runs
        ORDER BY run_id DESC
        LIMIT ?
    """, (args.limit,))

    print(f"\n{'='*100}")
    print("Import Runs")
    print(f"{'='*100}")
    print(f"{'ID':<6} {'Started':<20} {'Ended':<20} {'File':<30} {'Total':<8} {'✓':<6} {'✗':<6} {'○':<6}")
    print(f"{'-'*100}")

    for row in cursor.fetchall():
        ended = row['end_time'][:19] if row['end_time'] else 'IN PROGRESS'
        print(f"{row['run_id']:<6} {row['start_time'][:19]:<20} {ended:<20} {row['jsonl_file'][:30]:<30} "
              f"{row['total_entities']:<8} {row['success_count']:<6} {row['fail_count']:<6} {row['skip_count']:<6}")


def main():
    parser = argparse.ArgumentParser(description='Manage import state database')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    status_parser = subparsers.add_parser('status', help='Show current import status')

    list_parser = subparsers.add_parser('list', help='List entities')
    list_parser.add_argument('--status', help='Filter by status')
    list_parser.add_argument('--type', help='Filter by entity type')
    list_parser.add_argument('--run-id', type=int, help='Filter by run ID')
    list_parser.add_argument('--limit', type=int, default=100, help='Max results')

    stats_parser = subparsers.add_parser('stats', help='Show overall statistics')

    reset_parser = subparsers.add_parser('reset', help='Reset import state')
    reset_parser.add_argument('--run-id', type=int, help='Reset specific run')

    export_parser = subparsers.add_parser('export', help='Export to CSV')
    export_parser.add_argument('--status', help='Filter by status')
    export_parser.add_argument('--file', required=True, help='Output file path')

    runs_parser = subparsers.add_parser('runs', help='List all import runs')
    runs_parser.add_argument('--limit', type=int, default=10, help='Max runs to show')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    commands = {
        'status': cmd_status,
        'list': cmd_list,
        'stats': cmd_stats,
        'reset': cmd_reset,
        'export': cmd_export,
        'runs': cmd_runs
    }

    commands[args.command](args)


if __name__ == '__main__':
    main()
