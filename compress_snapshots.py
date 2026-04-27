#!/usr/bin/env python3
from PIL import Image
from pathlib import Path
import sys

snapshot_dir = Path(__file__).parent / "snapshots"

def compress_all():
    """Compress all JPG snapshots to WebP format"""
    jpg_files = list(snapshot_dir.glob("snapshot_*.jpg"))
    if not jpg_files:
        print("No snapshots to compress")
        return

    print(f"Found {len(jpg_files)} snapshots to compress")
    for i, jpg_path in enumerate(jpg_files, 1):
        webp_path = jpg_path.with_suffix('.webp')
        if webp_path.exists():
            print(f"[{i}/{len(jpg_files)}] {jpg_path.name} - already compressed, skipping")
            continue

        try:
            img = Image.open(jpg_path)
            img.save(webp_path, 'WEBP', quality=85)
            jpg_size = jpg_path.stat().st_size / 1024
            webp_size = webp_path.stat().st_size / 1024
            ratio = (1 - webp_size / jpg_size) * 100
            print(f"[{i}/{len(jpg_files)}] {jpg_path.name} - {jpg_size:.1f}KB → {webp_size:.1f}KB ({ratio:.0f}% smaller)")
        except Exception as e:
            print(f"[{i}/{len(jpg_files)}] {jpg_path.name} - ERROR: {e}")

if __name__ == '__main__':
    compress_all()
