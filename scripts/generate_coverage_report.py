#!/usr/bin/env python3
import sys
import xml.etree.ElementTree as ET

if len(sys.argv) != 2:
    print("Usage: python generate_coverage_report.py <threshold>")
    sys.exit(1)

threshold_pct = int(sys.argv[1])
threshold = threshold_pct / 100.0

# Parse coverage.xml
tree = ET.parse("coverage.xml")
root = tree.getroot()

# Get coverage percentage
coverage = float(root.attrib["line-rate"]) * 100

# Generate badge URL
color = (
    "red"
    if coverage < 50
    else "orange"
    if coverage < 75
    else "yellow"
    if coverage < 90
    else "green"
)
badge_url = f"https://img.shields.io/badge/coverage-{coverage:.1f}%25-{color}"

print(f"Coverage: {coverage:.1f}%")
print(f"Badge URL: {badge_url}")

# Generate missing coverage report
missing_files = []
for class_elem in root.findall(".//class"):
    filename = class_elem.attrib.get("filename", "Unknown")
    line_rate = float(class_elem.attrib.get("line-rate", 0))
    if line_rate < threshold:
        missing_files.append((filename, line_rate * 100))

filename = "coverage_below_threshold.txt"
with open(filename, "w") as f:
    f.write(f"Files with coverage below {threshold_pct}%:\n")
    if missing_files:
        for file_name, pct in sorted(missing_files, key=lambda x: x[1]):
            f.write(f"{file_name}: {pct:.1f}%\n")
    else:
        f.write("None\n")

print(f"Missing coverage report saved to {filename}")
