import numpy as np
import sys
import types

sys.modules.setdefault("pdal", types.SimpleNamespace(Pipeline=None))
sys.modules.setdefault("opendm.log", types.SimpleNamespace())
from opendm.dem.ground_rectification import rectify
from opendm.dem.ground_rectification.point_cloud import BoundingBox3D, PointCloud


class _FakePartition:
    def __init__(self, point_cloud):
        self.point_cloud = point_cloud
        self.bounds = BoundingBox3D(0, 0.2, 0, 0.2, -1, 1)


class _FakePlan:
    def __init__(self, partition):
        self.partition = partition

    def execute(self, **kwargs):
        return [self.partition]


def _ground_cloud():
    return PointCloud.with_dimensions(
        np.array([0.0, 1.0, 0.0, 1.0]),
        np.array([0.0, 0.0, 1.0, 1.0]),
        np.array([0.0, 0.0, 0.0, 0.0]),
        np.array([2, 2, 2, 2], dtype=np.uint8),
        np.array([100, 100, 100, 100], dtype=np.uint8),
        np.array([100, 100, 100, 100], dtype=np.uint8),
        np.array([100, 100, 100, 100], dtype=np.uint8),
    )


def test_extend_cloud_appends_only_grid_points_that_received_predictions(monkeypatch):
    point_cloud = _ground_cloud()
    grid_xy = np.array([[0.1, 0.1], [0.9, 0.9]])

    def grid_with_in_bounds_placeholder_values(xy):
        count = xy.shape[0]
        return PointCloud.with_dimensions(
            xy[:, 0],
            xy[:, 1],
            np.zeros(count),
            np.zeros(count, dtype=np.uint8),
            np.zeros(count, dtype=np.uint8),
            np.zeros(count, dtype=np.uint8),
            np.zeros(count, dtype=np.uint8),
        )

    monkeypatch.setattr(rectify, "calculate_convex_hull_bounds", lambda xy: object())
    monkeypatch.setattr(rectify, "build_grid", lambda bounds, ground_cloud, distance: grid_xy)
    monkeypatch.setattr(rectify, "select_partition_plan", lambda plan, ground_cloud: _FakePlan(_FakePartition(ground_cloud)))
    monkeypatch.setattr(rectify.PointCloud, "with_xy", staticmethod(grid_with_in_bounds_placeholder_values))

    extended = rectify.extend_cloud(point_cloud, "one", distance=1, min_points=1, min_area=1)

    assert extended.len() == 5
    assert [tuple(xy) for xy in extended.xy[-1:]] == [(0.1, 0.1)]


def test_rectify_main_invokes_run_rectification(monkeypatch, tmp_path):
    calls = {}
    monkeypatch.setattr(rectify, "run_rectification", lambda **kwargs: calls.update(kwargs))

    rc = rectify.main([
        str(tmp_path / "input.laz"),
        str(tmp_path / "output.laz"),
        "--extend_plan",
        "one",
    ])

    assert rc == 0
    assert calls["input"] == str(tmp_path / "input.laz")
    assert calls["output"] == str(tmp_path / "output.laz")
    assert calls["extend_plan"] == "one"
