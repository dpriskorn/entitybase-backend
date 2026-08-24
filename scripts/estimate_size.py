#!/usr/bin/env python3
"""Estimate directory size by sampling random subdirectories with du."""

import os
import random
import subprocess
import sys
import tempfile


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <directory> [sample_size=1000]")
        sys.exit(1)

    target_dir = sys.argv[1]
    sample_size = int(sys.argv[2]) if len(sys.argv) > 2 else 1000

    if not os.path.isdir(target_dir):
        print(f"Not a directory: {target_dir}")
        sys.exit(1)

    # List subdirectories (ls reads directory blocks — fast)
    print(f"Listing {target_dir} ...")
    result = subprocess.run(
        ["ls", target_dir], capture_output=True, text=True
    )
    all_dirs = result.stdout.strip().split("\n")
    total_dirs = len(all_dirs)

    if total_dirs == 0 or all_dirs == [""]:
        print("No subdirectories found.")
        sys.exit(0)

    # Sample random directories
    n = min(sample_size, total_dirs)
    sampled = random.sample(all_dirs, n)
    print(f"Sampled {n:,} / {total_dirs:,} dirs")

    # Write null-separated paths for du --files0-from
    with tempfile.NamedTemporaryFile(mode="wb", delete=False) as f:
        tmp_path = f.name
        for name in sampled:
            f.write(os.path.join(target_dir, name).encode() + b"\0")

    try:
        # Single du call on all sampled paths
        print(f"Running du on {n:,} dirs ...")
        du_result = subprocess.run(
            ["du", "-sb", "--files0-from", tmp_path],
            capture_output=True,
            text=True,
        )

        # Parse sizes
        sizes: list[int] = []
        for line in du_result.stdout.strip().split("\n"):
            if line:
                size_str, _ = line.split("\t", 1)
                sizes.append(int(size_str))

        if not sizes:
            print("du returned no output.")
            sys.exit(1)

        # Calculate stats
        total = sum(sizes)
        avg = total / len(sizes)
        estimated_total = avg * total_dirs

        print(f"\nDirectory:      {target_dir}")
        print(f"Sample size:    {len(sizes):,} / {total_dirs:,} dirs")
        print(f"Avg dir size:   {avg:,.0f} bytes ({avg / 1024:.1f} KB)")
        print(f"Estimated:      {estimated_total / 1024 / 1024 / 1024:.1f} GB")

    finally:
        os.unlink(tmp_path)


if __name__ == "__main__":
    main()
