# PPKflow ODM Patch Queue

This fork is used by PPKflow to build and test controlled OpenDroneMap base
images. Upstream OpenDroneMap remains the baseline; patches listed here must
pass PPKflow worker, benchmark, and accuracy gates before moving from
`ppkflow/staging` to `ppkflow/production`.

## Branch Model

- `master`: tracks `OpenDroneMap/ODM` `master`.
- `ppkflow/staging`: integrates candidate patches and benchmark builds.
- `ppkflow/production`: promoted commits only. Fast-forward this branch only
  after the promotion report passes.

## Candidate Patches

### PR #2021: ExifRead DJI MakerNote Empty-Value Guard

- Upstream: https://github.com/OpenDroneMap/ODM/pull/2021
- PPKflow status: ported to `ppkflow/staging` with local regression coverage.
- Risk: low.
- Expected files: `opendm/photo.py`.
- Why PPKflow cares: DJI image metadata parsing failures can abort worker jobs
  before SfM starts. This is especially relevant for DJI Enterprise datasets.
- Required checks:
  - Unit/fixture coverage for an empty DJI MakerNote tag.
  - 20-photo smoke benchmark.
  - 174-photo benchmark.
  - No regression in image count, CRS, bounds, or package adoption.

### PR #2003: GPU/Kubernetes CUDA Path Fix

- Upstream: https://github.com/OpenDroneMap/ODM/pull/2003
- PPKflow status: ported to `ppkflow/staging` with Dockerfile regression coverage.
- Risk: low for GPU images; no expected CPU behavior change.
- Expected files: `gpu.Dockerfile`.
- Why PPKflow cares: Akash GPU providers expose CUDA/NVIDIA binaries through
  container runtime paths that can differ from local Docker. This patch should
  reduce silent GPU non-use or startup failures on Kubernetes-backed providers.
- Required checks:
  - GPU worker preflight logs `nvidia-smi`, CUDA library discovery, and ODM
    CUDA status.
  - GPU smoke worker starts on Akash.
  - GPU telemetry shows at least one non-zero utilization sample during ODM.

### PR #1994: SRT Parsing And GPS Altitude Handling

- Upstream: https://github.com/OpenDroneMap/ODM/pull/1994
- PPKflow status: ported to `ppkflow/staging` with static regression guards.
- Risk: low-medium.
- Expected files: SRT/GPS metadata parsing paths.
- Why PPKflow cares: Some customer uploads include DJI sidecar/video-derived
  telemetry. Incorrect altitude parsing can move the reconstruction or degrade
  georeferencing.
- Required checks:
  - SRT fixture unit test.
  - RTK-already-geotagged path test.
  - CRS, bounds, and GSD comparison against production baseline.

### PR #1971: Nested `image_groups.txt` Recursion

- Upstream: https://github.com/OpenDroneMap/ODM/pull/1971
- PPKflow status: ported to `ppkflow/staging` with static regression guards.
- Risk: low.
- Expected files: image grouping / project layout handling.
- Why PPKflow cares: PPKflow stages image packages before remote execution.
  Recursive or nested image group layouts should not break ODM ingestion.
- Required checks:
  - Fixture with nested image groups.
  - 20-photo smoke benchmark.
  - No change in deliverables for normal flat image package.

### PR #1974: DJI Gimbal Yaw / OPK Orientation Handling

- Upstream: https://github.com/OpenDroneMap/ODM/pull/1974
- Risk: medium.
- Expected files: DJI metadata orientation / OPK paths.
- Why PPKflow cares: Orientation priors can affect SfM speed and stability.
  Bad yaw handling can also hurt spray orthophoto alignment.
- Required checks:
  - DJI Enterprise fixture with known camera orientation metadata.
  - Accuracy comparison on PPKflow Brazil dataset.
  - Visual orthophoto check.
  - Spray boundary export still validates.

### PR #2008: Topocentric Dense Reconstruction With Final Georeferencing

- Upstream: https://github.com/OpenDroneMap/ODM/pull/2008
- Risk: high.
- Expected files: georeferencing, OpenMVS/dense reconstruction, point-cloud
  transformation paths.
- Why PPKflow cares: This might improve reconstruction robustness and numeric
  behavior, but it touches the most sensitive accuracy path.
- Required checks before any production consideration:
  - Dedicated canary branch only.
  - 20-photo smoke benchmark.
  - 174-photo Brazil benchmark.
  - RTK-already-geotagged benchmark.
  - CRS, bounds, GSD, nodata, DSM/DTM, LAZ, and spray export comparisons.
  - Manual visual review of orthophoto alignment.
  - Explicit operator approval in the promotion report.

## Promotion Requirements

Each candidate release must record:

- ODM upstream commit.
- PPKflow fork commit.
- Patch list.
- CPU ODM image tag and digest.
- GPU ODM image tag and digest when applicable.
- PPKflow worker image tags and digests.
- Dataset matrix and product presets.
- Benchmark runtime, cost, resource, GPU, CPU, disk, and stage timing metrics.
- Accuracy comparator output.
- `/map`, `/preview`, `/tiles`, `/download`, and spray export checks.

If a patch fails a gate, leave it on staging or a canary branch. Do not promote
it into `ppkflow/production`.
