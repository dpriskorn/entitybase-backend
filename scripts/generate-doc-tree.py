#!/usr/bin/env python3
"""
Generate doc-tree.md with links to all README.md files in the project,
excluding deprecated directories.
"""

import os
import sys
from pathlib import Path


def should_exclude(path: Path) -> bool:
    """Check if path should be excluded from doc tree."""
    exclude_patterns = [
        '__pycache__',
        '.git',
        'node_modules',
        'DEPRECATED',
        'deprecated',
    ]
    return any(pattern in str(path) for pattern in exclude_patterns)


def find_readmes(root_dir: Path) -> list[Path]:
    """Find all README.md files."""
    readmes = []
    for path in root_dir.rglob('README.md'):
        if not should_exclude(path):
            readmes.append(path)
    return sorted(readmes)


def generate_markdown(readmes: list[Path], root_dir: Path) -> str:
    """Generate markdown content."""
    lines = ['# Doc Tree\n', 'Links to all README.md files in the project.\n']

    for readme in readmes:
        # Get relative path
        rel_path = readme.relative_to(root_dir)

        # Try to get title from first line
        title = "README"
        try:
            with open(readme, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                if first_line.startswith('# '):
                    title = first_line[2:]
        except Exception:
            pass

        # Add link
        lines.append(f'- [{title}]({rel_path})')

    return '\n'.join(lines)


def main():
    root_dir = Path(__file__).parent.parent
    readmes = find_readmes(root_dir)

    markdown = generate_markdown(readmes, root_dir)

    output_file = root_dir / 'doc-tree.md'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown)

    print(f"Generated {output_file} with {len(readmes)} README links")


if __name__ == '__main__':
    main()