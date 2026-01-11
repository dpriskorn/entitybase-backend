#!/usr/bin/env python3
"""Update STATISTICS.md with coverage information."""

import xml.etree.ElementTree as ET
import re
from pathlib import Path


def parse_coverage_xml(xml_file: str) -> dict:
    """Parse coverage XML file and return coverage statistics."""
    tree = ET.parse(xml_file)
    root = tree.getroot()

    total_lines = int(root.attrib['lines-valid'])
    covered_lines = int(root.attrib['lines-covered'])
    coverage_percentage = float(root.attrib['line-rate']) * 100

    return {
        'total_lines': total_lines,
        'covered_lines': covered_lines,
        'coverage_percentage': coverage_percentage,
        'line_rate': float(root.attrib['line-rate'])
    }


def update_statistics_md(stats_file: str, coverage_data: dict) -> None:
    """Update STATISTICS.md with coverage information."""
    content = Path(stats_file).read_text()

    # Create coverage section
    coverage_section = f"""# Test Coverage
```
Coverage: {coverage_data['coverage_percentage']:.1f}%
Lines covered: {coverage_data['covered_lines']:,}
Total lines: {coverage_data['total_lines']:,}
```

"""

    # Check if coverage section already exists
    if "# Test Coverage" in content:
        # Replace existing section
        pattern = r'# Test Coverage\n```.*?\n```\n\n'
        content = re.sub(pattern, coverage_section, content, flags=re.DOTALL)
    else:
        # Add after Overall section
        pattern = r'(# Overall\n```.*?```\n\n)'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            insert_pos = match.end()
            content = content[:insert_pos] + coverage_section + content[insert_pos:]
        else:
            # Fallback: add at the beginning
            content = coverage_section + content

    Path(stats_file).write_text(content)
    print(f"Updated {stats_file} with coverage statistics")


def main():
    """Main function to update statistics."""
    coverage_xml = "coverage.xml"
    stats_md = "STATISTICS.md"

    if not Path(coverage_xml).exists():
        print(f"Coverage file {coverage_xml} not found. Run tests with coverage first.")
        return

    coverage_data = parse_coverage_xml(coverage_xml)
    update_statistics_md(stats_md, coverage_data)

    print(f"Updated coverage statistics: {coverage_data['coverage_percentage']:.1f}%")
if __name__ == "__main__":
    main()