#!/usr/bin/env python3
"""Normalize selected PNG slides without cropping or changing source files.

Requires Pillow: install it in an isolated environment with `python -m pip install
Pillow`. Only deterministic export operations are performed, not creative edits.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

TARGET = (1080, 1350)
BACKGROUND = (238, 233, 224)


def pillow():
    try:
        from PIL import Image, ImageOps
    except ImportError as exc:
        raise ValueError("Pillow is required. In an isolated virtual environment, run: python -m pip install Pillow") from exc
    return Image, ImageOps


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize(input_dir, output_dir, output_format="png"):
    if output_format not in {"png", "jpeg"}:
        raise ValueError("Output format must be png or jpeg.")
    Image, ImageOps = pillow()
    source = Path(input_dir).resolve()
    destination = Path(output_dir).resolve()
    if source == destination or source in destination.parents or destination in source.parents:
        raise ValueError("Input and output must be separate, non-overlapping directories.")
    if not source.is_dir():
        raise ValueError("Input must be a directory of selected, numbered PNG slides.")
    if destination.exists() and (not destination.is_dir() or any(destination.iterdir())):
        raise ValueError("Output directory must be absent or empty; existing outputs are never overwritten.")
    paths = sorted(p for p in source.iterdir() if p.suffix.lower() == ".png")
    if not paths:
        raise ValueError("No PNG slides found.")
    # Validate the entire batch before creating any output.
    prepared, hashes, numbers, names = [], set(), set(), set()
    for path in paths:
        match = re.match(r"^(\d+)(?:[-_.]|$)", path.stem)
        if not match:
            raise ValueError(f"{path.name}: use numbered filenames such as 01-hook.png.")
        number = int(match.group(1))
        output_name = path.with_suffix(".jpg" if output_format == "jpeg" else ".png").name
        if number < 1 or number in numbers or output_name.casefold() in names:
            raise ValueError(f"{path.name}: duplicate slide number or output filename collision.")
        numbers.add(number)
        names.add(output_name.casefold())
        digest = sha256(path)
        if digest in hashes:
            raise ValueError(f"{path.name}: duplicate source image.")
        hashes.add(digest)
        with Image.open(path) as raw:
            if raw.format != "PNG":
                raise ValueError(f"{path.name}: file must actually be PNG.")
            original_size = raw.size
            oriented = ImageOps.exif_transpose(raw)
            width, height = oriented.size
            mismatch = abs((width / height) / (TARGET[0] / TARGET[1]) - 1)
            if mismatch > 0.01:
                raise ValueError(f"{path.name}: aspect mismatch exceeds 1%; repair the design in the image tool before export.")
            if width < TARGET[0] or height < TARGET[1]:
                raise ValueError(f"{path.name}: source is smaller than 1080x1350; regenerate at sufficient resolution (no upscaling).")
            rgba = oriented.convert("RGBA")
            flattened = Image.new("RGBA", rgba.size, BACKGROUND + (255,))
            flattened.alpha_composite(rgba)
            rgb = flattened.convert("RGB")
            fitted = ImageOps.contain(rgb, TARGET, Image.Resampling.LANCZOS)
            result = Image.new("RGB", TARGET, BACKGROUND)
            offset = ((TARGET[0] - fitted.width) // 2, (TARGET[1] - fitted.height) // 2)
            result.paste(fitted, offset)
            prepared.append((number, path, result, {
                "source": str(path), "source_sha256": digest,
                "source_dimensions": list(original_size), "oriented_dimensions": [width, height],
                "output": str(destination / output_name), "output_dimensions": list(TARGET),
                "output_format": output_format, "output_mode": "RGB",
                "content_dimensions": list(fitted.size), "padding_offset": list(offset),
                "action": "exif-orient, flatten to RGB, proportional fit, center pad; no crop or upscale",
            }))
    destination.mkdir(parents=True, exist_ok=True)
    # Recheck after preparation, including any concurrent writer.
    if any(destination.iterdir()):
        raise ValueError("Output directory is no longer empty; refusing overwrite.")
    records = []
    for _, path, result, record in sorted(prepared, key=lambda item: item[0]):
        output = Path(record["output"])
        with output.open("xb") as stream:
            if output_format == "jpeg":
                result.save(stream, format="JPEG", quality=95, subsampling=0, optimize=True)
            else:
                result.save(stream, format="PNG", optimize=True)
        record["output_sha256"] = sha256(output)
        record["output_bytes"] = output.stat().st_size
        records.append(record)
    report = {"output_format": output_format, "target_dimensions": list(TARGET), "background": "#eee9e0", "slides": records}
    with (destination / "normalization-report.json").open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2)
        stream.write("\n")
    return report


def main():
    parser = argparse.ArgumentParser(description="Export numbered PNG slides as exact 1080x1350 RGB PNGs. Preserves sources; fits and pads without crop/stretch. Requires Pillow.")
    parser.add_argument("input_dir", type=Path, help="Directory containing only the selected numbered PNG slides")
    parser.add_argument("output_dir", type=Path, help="Separate absent/empty directory for images and normalization-report.json")
    parser.add_argument("--format", choices=("png", "jpeg"), default="png", help="png for canonical exports (default); jpeg for a separate publisher-compatible folder")
    args = parser.parse_args()
    try:
        report = normalize(args.input_dir, args.output_dir, args.format)
    except (ValueError, OSError) as exc:
        parser.exit(2, f"Error: {exc}\n")
    print(f"Exported {len(report['slides'])} slides to {args.output_dir}; inspect every final image before marking ready.")


if __name__ == "__main__":
    main()
