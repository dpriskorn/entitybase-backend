#!/usr/bin/env python3
"""Generate PlantUML architecture diagrams from codebase analysis."""

import ast
from pathlib import Path
from typing import Any, Dict


def analyze_codebase() -> Dict[str, Any]:
    """Analyze the codebase structure and relationships."""
    src_dir = Path("src")

    analysis = {
        "packages": {},
        "services": [],
        "repositories": [],
        "handlers": [],
        "models": [],
        "workers": [],
        "imports": {},
        "relationships": [],
    }

    # Scan all Python files
    for py_file in src_dir.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue

        try:
            with open(py_file, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content, filename=str(py_file))

            # Get relative path for categorization
            rel_path = py_file.relative_to(src_dir)
            package_path = str(rel_path.parent)

            # Analyze file content
            file_info = analyze_file(py_file, tree, content, package_path)
            update_analysis(analysis, file_info, package_path)

        except Exception as e:
            print(f"Warning: Could not analyze {py_file}: {e}")

    return analysis


def analyze_file(
    py_file: Path, tree: ast.AST, content: str, package_path: str
) -> Dict[str, Any]:
    """Analyze a single Python file."""
    file_info = {
        "path": py_file,
        "classes": [],
        "imports": set(),
        "functions": [],
        "category": categorize_file(package_path, py_file.name),
    }

    # Extract imports
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                file_info["imports"].add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                file_info["imports"].add(node.module.split(".")[0])

    # Extract classes and their methods
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_info = {
                "name": node.name,
                "methods": [],
                "bases": [
                    base.id if isinstance(base, ast.Name) else str(base)
                    for base in node.bases
                ],
            }

            # Get methods
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and not item.name.startswith("_"):
                    class_info["methods"].append(item.name)

            file_info["classes"].append(class_info)

    return file_info


def categorize_file(package_path: str, filename: str) -> str:
    """Categorize a file based on its path and name."""
    if "rest_api" in package_path:
        if "services" in package_path:
            return "service"
        elif "handlers" in package_path or "routes" in package_path:
            return "handler"
        elif "response" in package_path:
            return "model"
        else:
            return "api"
    elif "infrastructure" in package_path:
        if "vitess" in package_path:
            if "repository" in filename:
                return "repository"
            else:
                return "infrastructure"
        else:
            return "infrastructure"
    elif "workers" in package_path:
        return "worker"
    elif "config" in package_path:
        return "config"
    else:
        return "other"


def update_analysis(analysis: Dict, file_info: Dict, package_path: str):
    """Update the analysis dictionary with file information."""
    category = file_info["category"]

    # Add to packages
    if package_path not in analysis["packages"]:
        analysis["packages"][package_path] = {"files": [], "classes": []}

    analysis["packages"][package_path]["files"].append(
        str(file_info["path"].relative_to(Path("src")))
    )
    analysis["packages"][package_path]["classes"].extend(
        [cls["name"] for cls in file_info["classes"]]
    )

    # Add to specific categories
    for cls in file_info["classes"]:
        if category == "service":
            analysis["services"].append(cls["name"])
        elif category == "repository":
            analysis["repositories"].append(cls["name"])
        elif category == "handler":
            analysis["handlers"].append(cls["name"])
        elif category == "model":
            analysis["models"].append(cls["name"])
        elif category == "worker":
            analysis["workers"].append(cls["name"])

    # Track imports for relationship analysis
    module_name = file_info["path"].stem
    analysis["imports"][module_name] = file_info["imports"]


def generate_system_architecture_diagram(analysis: Dict) -> str:
    """Generate PlantUML system architecture diagram."""
    lines = [
        "@startuml System Architecture",
        "",
        "title Wikibase Backend - System Architecture",
        "",
    ]

    # Define packages
    packages = {
        "API Layer": {
            "components": analysis["handlers"] + ["FastAPI Server", "Request Routing"],
            "color": "LightBlue",
        },
        "Service Layer": {"components": analysis["services"], "color": "LightGreen"},
        "Worker Layer": {"components": analysis["workers"], "color": "LightYellow"},
        "Infrastructure Layer": {
            "components": analysis["repositories"] + ["Vitess Client", "S3 Client"],
            "color": "LightGray",
        },
        "Data Models": {
            "components": analysis["models"][:10],  # Limit to first 10
            "color": "LightCyan",
        },
    }

    # Create package definitions
    for pkg_name, pkg_info in packages.items():
        if pkg_info["components"]:
            lines.append(
                f'package "{pkg_name}" as {pkg_name.replace(" ", "")} #{pkg_info["color"]} {{'
            )

            for component in pkg_info["components"][:5]:  # Limit components (detailed in separate diagram)
                component_name = (
                    component.replace("Service", "")
                    .replace("Handler", "")
                    .replace("Repository", "")
                    .strip()
                )
                # Skip empty component names
                if not component_name:
                    continue
                # Use quoted component names to handle special characters safely
                safe_id = (
                    component.replace(" ", "_")
                    .replace("-", "_")
                    .replace("(", "")
                    .replace(")", "")
                    .replace("[", "")
                    .replace("]", "")
                )
                if not safe_id:
                    safe_id = f"Component_{len(lines)}"  # Fallback ID
                lines.append(f'    "{component_name}" as {safe_id}')

            if len(pkg_info["components"]) > 8:
                lines.append(
                    f"    ... ({len(pkg_info['components'])} total components)"
                )

            lines.append("}")
            lines.append("")

    # Add relationships
    lines.extend(
        [
            "",
            "' Relationships",
            "API -> Service : business logic",
            "Service -> Infrastructure : data access",
            "Worker -> Infrastructure : background processing",
            "API -> DataModels : serialization",
            "",
            "@enduml",
        ]
    )

    return "\n".join(lines)


def generate_data_flow_diagram(analysis: Dict) -> str:
    """Generate PlantUML data flow diagram."""
    lines = ["@startuml Data Flow", "", "title Wikibase Backend - Data Flow", ""]

    # Define actors and components
    components = [
        'actor \"Client\" as Client',
        'rectangle \"FastAPI\" as API',
        'rectangle \"Request Handler\" as Handler',
        'rectangle \"Service Layer\" as Service',
        'rectangle \"Vitess Client\" as VitessClient',
        'database \"Vitess DB\" as Vitess',
        'rectangle \"S3 Client\" as S3Client',
        'storage \"S3 Terms\" as S3Terms',
        'storage \"S3 Statements\" as S3Statements',
        'storage \"S3 References\" as S3References',
        'storage \"S3 Qualifiers\" as S3Qualifiers',
        'storage \"S3 Revisions\" as S3Revisions',
        'storage \"S3 Dumps\" as S3Dumps',
        'rectangle \"Workers\" as Workers',
        'database \"Kafka\" as Kafka',
    ]

    lines.extend(components)
    lines.append("")

    # Data flow arrows
    flows = [
        "' Main request flow",
        "Client -> API : HTTP Request",
        "API -> Handler : Route Request",
        "Handler -> Service : Business Logic",
        "Service -> VitessClient : Database Query",
        "VitessClient -> Vitess : SQL Query",
        "",
        "' Background processing",
        "Handler -> Kafka : Change Events",
        "Workers -> Vitess : Background Tasks",
        "",
        "' Storage operations",
        "Service -> S3Client : Metadata Operations",
        "S3Client -> S3Terms : Labels/Descriptions/Aliases",
        "Service -> S3Client : Statement Operations",
        "S3Client -> S3Statements : Statement Deduplication",
        "Service -> S3Client : Reference Operations",
        "S3Client -> S3References : Reference Deduplication",
        "Service -> S3Client : Qualifier Operations",
        "S3Client -> S3Qualifiers : Qualifier Deduplication",
        "Service -> S3Client : Revision Operations",
        "S3Client -> S3Revisions : Revision Data",
        "Workers -> S3Client : Dump Operations",
        "S3Client -> S3Dumps : Entity Exports",
        "",
        "' Response flow",
        "S3Terms --> S3Client : Metadata",
        "S3Statements --> S3Client : Statements",
        "S3References --> S3Client : References",
        "S3Qualifiers --> S3Client : Qualifiers",
        "S3Revisions --> S3Client : Revisions",
        "S3Dumps --> S3Client : Dump Data",
        "S3Client --> Service : Retrieved Data",
        "Vitess --> VitessClient : Results",
        "VitessClient --> Service : Response Data",
        "Service --> Handler : Processed Data",
        "Handler --> API : JSON Response",
        "API --> Client : HTTP Response",
    ]

    lines.extend(flows)
    lines.append("")
    lines.append("@enduml")

    return "\n".join(lines)


def generate_detailed_api_diagram(analysis: Dict) -> str:
    """Generate PlantUML detailed API diagram showing all handlers/routes."""
    lines = [
        "@startuml Detailed API Components",
        "",
        "title Wikibase Backend - Detailed API Components",
        "",
    ]

    # Get all API components (handlers)
    api_components = sorted(analysis.get("handlers", []))
    if api_components:
        lines.append('package "API Handlers" as APIHandlers #LightBlue {')
        for component in api_components:
            component_name = component.replace("Handler", "").replace("Service", "").strip()
            if not component_name:
                continue
            safe_id = component.replace(" ", "_").replace("-", "_").replace("(", "").replace(")", "").replace("[", "").replace("]", "")
            if not safe_id:
                safe_id = f"Component_{len(lines)}"
            lines.append(f'    "{component_name}" as {safe_id}')
        lines.append("}")
    else:
        lines.append("note: No API components found")

    lines.append("")
    lines.append("@enduml")

    return "\n".join(lines)


def generate_component_relationship_diagram(analysis: Dict) -> str:
    """Generate PlantUML component relationship diagram."""
    lines = [
        "@startuml Component Relationships",
        "",
        "title Wikibase Backend - Component Relationships",
        "",
    ]

    # Define main components
    components = [
        "[FastAPI] as API",
        "[Handlers] as Handlers",
        "[Services] as Services",
        "[Workers] as Workers",
        "[Repositories] as Repos",
        "[Models] as Models",
        'database "Vitess" as Vitess',
        'storage "S3 Terms" as S3Terms',
        'storage \"S3 Statements\" as S3Statements',
        'storage \"S3 References\" as S3References',
        'storage \"S3 Qualifiers\" as S3Qualifiers',
        'storage \"S3 Revisions\" as S3Revisions',
        'storage "S3 Dumps" as S3Dumps',
        'queue "Kafka" as Kafka',
        "[Config] as Config",
    ]

    lines.extend(components)
    lines.append("")

    # Define interfaces
    interfaces = [
        '() "HTTP API" as HTTP',
        '() "Database Interface" as DBI',
        '() "Storage Interface" as SI',
        '() "Kafka Message Queue" as MQ',
    ]

    lines.extend(interfaces)
    lines.append("")

    # Relationships
    relationships = [
        "' Architecture layers",
        "API --> Handlers : routes",
        "Handlers --> Services : logic",
        "Services --> Repos : data",
        "Workers --> Repos : processing",
        "Services --> Models : serialization",
        "",
        "' External interfaces",
        "API -- HTTP",
        "Repos -- DBI",
        "Services -- SI",
        "Handlers -- MQ",
        "",
        "' External systems",
        "DBI --> Vitess : mysql",
        "SI --> S3Terms : terms metadata",
        "SI --> S3Statements : statement content",
        "SI --> S3References : reference content",
        "SI --> S3Qualifiers : qualifier content",
        "SI --> S3Revisions : revision data",
        "Workers --> S3Dumps : entity dumps",
        "MQ --> Kafka : events",
        "Config --> API : configuration",
        "Config --> Workers : configuration",
    ]

    lines.extend(relationships)
    lines.append("")
    lines.append("@enduml")

    return "\n".join(lines)


def save_diagrams():
    """Generate and save all diagrams."""
    print("Analyzing codebase...")
    analysis = analyze_codebase()

    print("Generating diagrams...")

    # Create diagrams directory
    diagrams_dir = Path("doc/DIAGRAMS")
    diagrams_dir.mkdir(parents=True, exist_ok=True)

    # Generate system architecture diagram
    system_diagram = generate_system_architecture_diagram(analysis)
    with open(diagrams_dir / "system_architecture.puml", "w") as f:
        f.write(system_diagram)

    # Generate data flow diagram
    data_flow_diagram = generate_data_flow_diagram(analysis)
    with open(diagrams_dir / "data_flow.puml", "w") as f:
        f.write(data_flow_diagram)

    # Generate component relationship diagram
    component_diagram = generate_component_relationship_diagram(analysis)
    with open(diagrams_dir / "component_relationships.puml", "w") as f:
        f.write(component_diagram)

    # Generate detailed API diagram
    detailed_api_diagram = generate_detailed_api_diagram(analysis)
    with open(diagrams_dir / "detailed_api_components.puml", "w") as f:
        f.write(detailed_api_diagram)

    print(f"Diagrams generated in {diagrams_dir}/")


if __name__ == "__main__":
    save_diagrams()
