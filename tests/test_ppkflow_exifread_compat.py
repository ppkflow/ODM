from __future__ import annotations


def test_empty_exifread_values_are_printed_as_empty_string(monkeypatch):
    import exifread.core.exif_header as exif_header

    from opendm.exifread_compat import patch_exifread_empty_values

    def raises_index_error(self, *args, **kwargs):
        raise IndexError("list index out of range")

    monkeypatch.setattr(exif_header.ExifHeader, "_get_printable_for_field", raises_index_error)

    patch_exifread_empty_values()

    assert exif_header.ExifHeader._get_printable_for_field(object()) == ""
