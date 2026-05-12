from __future__ import annotations

from pathlib import Path


def test_gpu_dockerfile_includes_kubernetes_nvidia_library_paths():
    dockerfile = Path(__file__).resolve().parents[1] / "gpu.Dockerfile"
    text = dockerfile.read_text(encoding="utf-8")

    assert "/usr/local/nvidia/lib64" in text
    assert "/usr/local/nvidia/lib" in text
    assert "/usr/local/nvidia/bin" in text
