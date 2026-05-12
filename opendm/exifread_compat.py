"""Compatibility patches for ExifRead behavior that affects ODM ingestion."""

from __future__ import annotations


def patch_exifread_empty_values() -> bool:
    """Return an empty printable value for empty ExifRead tag values.

    ExifRead 3.x can raise ``IndexError`` while formatting empty DJI MakerNote
    values. That aborts metadata parsing before ODM can decide whether the tag
    matters. This wrapper keeps the original behavior for normal values and
    returns an empty string only for the empty-value crash path.
    """

    import exifread.core.exif_header as exif_header

    current = exif_header.ExifHeader._get_printable_for_field
    if getattr(current, "_ppkflow_empty_values_guard", False):
        return False

    def safe_get_printable(self, *args, **kwargs):
        try:
            return current(self, *args, **kwargs)
        except IndexError:
            return ""

    safe_get_printable._ppkflow_empty_values_guard = True
    safe_get_printable._ppkflow_original = current
    exif_header.ExifHeader._get_printable_for_field = safe_get_printable
    return True
