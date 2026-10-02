"""Synthetic export contract tests; no production media or network required."""
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw
from normalize_slides import normalize, sha256


class NormalizeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "source"
        self.source.mkdir()
        self.output = self.root / "export"

    def slide(self, name="01-hook.png", size=(1122, 1402), color="white"):
        path = self.source / name
        Image.new("RGB", size, color).save(path)
        return path

    def test_1122_by_1402_preserves_edges_and_original(self):
        path = self.slide()
        with Image.open(path) as image:
            draw = ImageDraw.Draw(image)
            draw.rectangle((0, 0, 30, 1401), fill="red")
            draw.rectangle((1091, 0, 1121, 1401), fill="blue")
            draw.rectangle((40, 0, 1080, 30), fill="green")
            draw.rectangle((40, 1371, 1080, 1401), fill="yellow")
            image.save(path)
        original = sha256(path)
        report = normalize(self.source, self.output)
        self.assertEqual(original, sha256(path))
        with Image.open(self.output / path.name) as result:
            self.assertEqual(result.size, (1080, 1350))
            self.assertEqual(result.mode, "RGB")
            self.assertEqual(result.getpixel((3, 600)), (255, 0, 0))
            self.assertEqual(result.getpixel((1076, 600)), (0, 0, 255))
            self.assertEqual(result.getpixel((600, 3)), (0, 128, 0))
            self.assertEqual(result.getpixel((600, 1346)), (255, 255, 0))
        self.assertEqual(report["slides"][0]["source_sha256"], original)
        other = self.root / "second-export"
        second = normalize(self.source, other)
        self.assertEqual(report["slides"][0]["output_sha256"], second["slides"][0]["output_sha256"])

    def test_wide_image_rejected_without_outputs(self):
        self.slide(size=(1920, 1350))
        with self.assertRaisesRegex(ValueError, "repair the design"):
            normalize(self.source, self.output)
        self.assertFalse(self.output.exists())

    def test_no_upscaling(self):
        self.slide(size=(800, 1000))
        with self.assertRaisesRegex(ValueError, "no upscaling"):
            normalize(self.source, self.output)

    def test_duplicate_sources(self):
        path = self.slide()
        (self.source / "02-end.png").write_bytes(path.read_bytes())
        with self.assertRaisesRegex(ValueError, "duplicate source"):
            normalize(self.source, self.output)

    def test_duplicate_numbers(self):
        self.slide()
        self.slide("01-end.png", color="red")
        with self.assertRaisesRegex(ValueError, "duplicate slide number"):
            normalize(self.source, self.output)

    def test_output_collision_and_same_directory(self):
        path = self.slide()
        before = sha256(path)
        with self.assertRaisesRegex(ValueError, "non-overlapping"):
            normalize(self.source, self.source)
        self.output.mkdir()
        sentinel = self.output / "existing.txt"
        sentinel.write_text("keep")
        with self.assertRaisesRegex(ValueError, "never overwritten"):
            normalize(self.source, self.output)
        self.assertEqual(sentinel.read_text(), "keep")
        self.assertEqual(before, sha256(path))

    def test_transparency_flattened_and_numeric_order(self):
        self.slide("10-end.png", (1080, 1350), "red")
        Image.new("RGBA", (1080, 1350), (0, 0, 0, 0)).save(self.source / "2-hook.png")
        report = normalize(self.source, self.output)
        self.assertTrue(report["slides"][0]["source"].endswith("2-hook.png"))
        with Image.open(self.output / "2-hook.png") as image:
            self.assertEqual(image.getpixel((0, 0)), (238, 233, 224))

    def test_jpeg_export(self):
        source = self.slide()
        original = sha256(source)
        report = normalize(self.source, self.output, "jpeg")
        result_path = self.output / "01-hook.jpg"
        with Image.open(result_path) as image:
            self.assertEqual(image.format, "JPEG")
            self.assertEqual(image.size, (1080, 1350))
            self.assertEqual(image.mode, "RGB")
        self.assertEqual(report["slides"][0]["output_bytes"], result_path.stat().st_size)
        self.assertEqual(original, sha256(source))

    def test_exif_orientation_before_dimension_check(self):
        path = self.source / "01-hook.png"
        image = Image.new("RGB", (1350, 1080), "red")
        exif = image.getexif()
        exif[274] = 6
        image.save(path, exif=exif)
        report = normalize(self.source, self.output)
        self.assertEqual(report["slides"][0]["oriented_dimensions"], [1080, 1350])


if __name__ == "__main__":
    unittest.main()
