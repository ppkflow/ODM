from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_srt_parser_preserves_decimal_rtk_altitude_and_reuses_zero_filter():
    text = (ROOT / "opendm" / "video" / "srtparser.py").read_text(encoding="utf-8")

    assert "def float_or_none_if_zero" in text
    assert r"(-?\d+\.?\d*)" in text


def test_video2dataset_preserves_submeter_altitude_precision():
    text = (ROOT / "opendm" / "video" / "video2dataset.py").read_text(encoding="utf-8")

    assert "float_to_rational(altitude)" in text
    assert "float_to_rational(round(altitude))" not in text


def test_submodel_argv_removes_split_image_groups_and_copy_to():
    text = (ROOT / "opendm" / "osfm.py").read_text(encoding="utf-8")

    assert "'split_image_groups'" in text
    assert "'copy_to'" in text
    assert "'copy-to'" not in text


def test_multichannel_tif_uses_rasterio_for_dimensions_and_ai_loading():
    size_text = (ROOT / "opendm" / "get_image_size.py").read_text(encoding="utf-8")
    ai_text = (ROOT / "opendm" / "ai.py").read_text(encoding="utf-8")

    assert "import rasterio as rio" in size_text
    assert 'extension == ".tif"' in size_text
    assert "width, height = f.width, f.height" in size_text

    assert "import rasterio as rio" in ai_text
    assert 'extension == ".tif"' in ai_text
    assert "f.read().transpose(1,2,0)" in ai_text


def test_camera_serial_participates_in_camera_identity():
    text = (ROOT / "opendm" / "photo.py").read_text(encoding="utf-8")

    assert "self.serial_number = 'unknown'" in text
    assert "EXIF LensSerialNumber" in text
    assert "EXIF BodySerialNumber" in text
    assert "@drone-dji:CameraSerialNumber" in text
    assert "@drone-dji:DroneSerialNumber" in text
    assert "self.serial_number.strip()" in text


def test_image_groups_override_split_threshold_to_avoid_recursive_splits():
    text = (ROOT / "stages" / "splitmerge.py").read_text(encoding="utf-8")

    assert "args.split = 999999" in text
    assert "image_groups.txt and split both set" in text
