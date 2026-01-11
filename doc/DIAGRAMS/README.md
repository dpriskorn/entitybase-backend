# Architecture Diagrams

This directory contains PlantUML diagrams that are automatically generated from the codebase analysis.

## Prerequisites

To generate PNG images from the PlantUML files, you need PlantUML installed:

```bash
sudo apt-get install plantuml
```

## Generated Files

### PlantUML Sources
- `system_architecture.puml` - System architecture diagram source
- `data_flow.puml` - Data flow diagram source
- `component_relationships.puml` - Component relationships source

### Rendered PNGs (requires PlantUML)
- `png/system_architecture.png` - System architecture diagram
- `png/data_flow.png` - Data flow diagram
- `png/component_relationships.png` - Component relationships diagram

## Viewing Diagrams

### PlantUML Source Files
1. **Edit directly**: Modify `.puml` files in any text editor
2. **Online Preview**: Copy content to [PlantUML Web Server](https://www.plantuml.com/plantuml/uml/)

### PNG Images (if PlantUML installed)
1. **Image Viewer**: Open `.png` files in any image viewer
2. **Documentation**: Embed in docs, presentations, etc.
3. **Web**: Use in web pages and READMEs

### VS Code Integration
Install the "PlantUML" extension for live preview of `.puml` files.

## Automatic Updates

These diagrams are automatically regenerated when running:

```bash
./update-docs.sh
```

The process:
1. **`scripts/generate_architecture_diagrams.py`**: Analyzes codebase to identify components and relationships
2. **`scripts/generate_pngs.py`**: Generates PNG images from PlantUML files (incremental - only when source is newer)

## Incremental PNG Generation

The PNG generation is **incremental** - it only regenerates PNGs when:
- The corresponding `.puml` file has been modified since the PNG was last generated
- The PNG file doesn't exist yet

This makes documentation updates fast when only some diagrams change.

## Adding New Diagrams

To add new diagram types:

1. **Add generation function** in `scripts/generate_architecture_diagrams.py`:
   ```python
   def generate_new_diagram(analysis: Dict) -> str:
       # Generate PlantUML code
       return "@startuml\n...\n@enduml"
   ```

2. **Update save_diagrams()** to call your new function:
   ```python
   new_diagram = generate_new_diagram(analysis)
   with open(diagrams_dir / "new_diagram.puml", "w") as f:
       f.write(new_diagram)
   ```

3. **PNG generation** will automatically handle the new `.puml` file