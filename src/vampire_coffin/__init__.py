"""Nosferatu's Coffin: slide the lid towards the feet and the vampire sits up."""


def main() -> None:
    """Export all STLs (out/stl) and 3MF plates (out/3mf)."""
    import sys
    from pathlib import Path

    from .export import export_all

    sys.exit(1 if any(export_all(Path("out")).values()) else 0)
