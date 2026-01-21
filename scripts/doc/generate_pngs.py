#!/usr/bin/env python3
"""Generate PNG files from PlantUML diagram files (incremental generation)."""

import hashlib
import subprocess
import sys
from pathlib import Path

import yaml


def load_cache(cache_file: Path) -> dict:
    """Load the cache of file hashes."""
    if cache_file.exists():
        with open(cache_file, 'r') as f:
            return yaml.safe_load(f) or {}
    return {}


def save_cache(cache_file: Path, cache: dict):
    """Save the cache of file hashes."""
    with open(cache_file, 'w') as f:
        yaml.dump(cache, f)


def compute_hash(file_path: Path) -> str:
    """Compute MD5 hash of a file."""
    hash_md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def needs_regeneration(puml_file: Path, cache: dict) -> bool:
    """Check if PNG needs to be regenerated based on content hash."""
    current_hash = compute_hash(puml_file)
    cached_hash = cache.get(puml_file.name)
    return current_hash != cached_hash


def generate_png_from_puml(
    puml_file: Path, output_dir: Path, cache: dict, force: bool = False
) -> tuple[bool, str]:
    """Generate PNG from a PlantUML file if needed."""
    png_file = output_dir / f"{puml_file.stem}.png"

    if not force and not needs_regeneration(puml_file, cache):
        return True, f"Skipped {puml_file.name} (PNG is up-to-date)"

    # Use PlantUML command line tool - it creates files based on title
    # We'll rename them afterward to match our expected naming
    cmd = ["plantuml", "-tpng", "-o", str(output_dir), str(puml_file)]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        # PlantUML creates files with title-based names, so we need to find and rename them
        # Look for any .png files in the output directory
        import glob
        import os

        png_files = glob.glob(str(output_dir / "*.png"))

        if png_files:
            # Assume the most recently modified file is the one we just created
            latest_png = max(png_files, key=lambda f: os.path.getmtime(f))
            if os.path.abspath(latest_png) != os.path.abspath(str(png_file)):
                os.rename(latest_png, png_file)

        # Update cache with new hash
        cache[puml_file.name] = compute_hash(puml_file)

        return True, f"Generated {png_file}"
    except subprocess.CalledProcessError as e:
        return False, f"Failed to generate {puml_file}: {e.stderr}"
    except FileNotFoundError:
        return (
            False,
            "PlantUML not installed. Install with: sudo apt-get install plantuml",
        )


def check_plantuml_installed() -> bool:
    """Check if PlantUML is installed."""
    try:
        result = subprocess.run(
            ["plantuml", "-version"], capture_output=True, text=True, check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def main():
    """Generate PNGs for PlantUML files that have been updated."""
    # Use absolute paths to avoid issues with current working directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    diagrams_dir = project_root / "doc" / "DIAGRAMS"
    png_dir = diagrams_dir / "png"
    cache_file = diagrams_dir / ".png_cache.yaml"

    if not diagrams_dir.exists():
        print("Error: Diagrams directory not found")
        sys.exit(1)

    # Check if PlantUML is installed
    if not check_plantuml_installed():
        print("Error: PlantUML not installed.")
        print("Install with: sudo apt-get install plantuml")
        sys.exit(1)

    # Create PNG output directory
    png_dir.mkdir(exist_ok=True)

    # Load cache
    cache = load_cache(cache_file)

    # Find all .puml files in the diagrams directory
    puml_files = list(diagrams_dir.glob("*.puml"))

    if not puml_files:
        print("No PlantUML files found in root diagrams directory")
        sys.exit(1)

    print(f"Checking {len(puml_files)} PlantUML files for updates...")

    error_count = 0
    success_count = 0
    skipped_count = 0

    for puml_file in puml_files:
        success, message = generate_png_from_puml(puml_file, png_dir, cache)
        if success:
            if "Skipped" in message:
                skipped_count += 1
                print(f"○ {message}")
            else:
                success_count += 1
                print(f"✓ {message}")
        else:
            error_count += 1
            print(f"✗ {message}")

    # Save cache
    save_cache(cache_file, cache)

    # Final status and exit code
    if error_count > 0:
        print(f"\nFailed: {error_count} PNG generation(s) failed")
        sys.exit(1)
    else:
        total_processed = success_count + skipped_count
        print(f"\nSuccess: {success_count} generated, {skipped_count} skipped")
        print(f"PNG files saved to: {png_dir}")
        if success_count > 0:
            print(
                "Note: PNGs were regenerated because .puml content changed"
            )
        sys.exit(0)


if __name__ == "__main__":
    main()
