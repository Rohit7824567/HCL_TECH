from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import shutil

root = Path(__file__).resolve().parents[1]
destination = root / "frontend" / "public" / "documents" / "P050_Customer_Purchase_Behaviour_Analysis.zip"
temporary = root / ".tmp" / destination.name
excluded_dirs = {".git", ".venv", "venv", ".tmp", "node_modules", "dist", "outputs", "__pycache__", ".pytest_cache", ".mypy_cache"}
excluded_names = {"customer_analysis.db", "Thumbs.db", ".DS_Store"}

with ZipFile(temporary, "w", ZIP_DEFLATED, compresslevel=8) as archive:
    for path in root.rglob("*"):
        if not path.is_file() or path == temporary or path == destination:
            continue
        relative = path.relative_to(root)
        if any(part in excluded_dirs for part in relative.parts):
            continue
        if relative.parts[:3] == ("frontend", "public", "documents"):
            continue
        if path.name in excluded_names or path.suffix.lower() in {".db", ".sqlite", ".sqlite3", ".pyc"}:
            continue
        if path.suffix.lower() in {".docx", ".pptx"}:
            continue
        if path.name == ".env":
            continue
        archive.write(path, relative.as_posix())

destination.parent.mkdir(parents=True, exist_ok=True)
shutil.move(str(temporary), str(destination))
print(f"Created {destination} ({destination.stat().st_size:,} bytes)")
