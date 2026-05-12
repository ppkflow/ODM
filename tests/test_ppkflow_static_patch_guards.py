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
