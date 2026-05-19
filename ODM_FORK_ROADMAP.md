# PPKflow ODM Fork Roadmap

Last updated: 2026-05-19.

This document tracks the PPKflow-owned OpenDroneMap fork, what has been ported
into staging, what evidence exists, and what must happen before the fork can be
used as the production default. The fork is a controlled release lane for ODM
patches and build fixes; it is not a place to silently diverge from upstream.

## Current State

Production still uses the public upstream ODM-based PPKflow worker:

- CPU worker: `ghcr.io/ppkflow/photogrammetry-worker:0.1.14-telemetry`
- GPU worker: `ghcr.io/ppkflow/photogrammetry-worker-gpu:0.1.14-telemetry`
- Public ODM base:
  `opendronemap/odm@sha256:4c14b76b9e517a2f7f9b367d2087543c6dd1430f82f71f1f8edcc562c534beac`

The PPKflow ODM fork candidate is staged/internal-canary only:

- Fork repo: `ppkflow/ODM`
- Local checkout: `Source/ODM`
- Current branch: `ppkflow/staging`
- Current staging commit: `79fd24c673685b82c5938244f1f7596f1267e554`
- Current GitHub state: `ppkflow/staging` is pushed and clean.
- Current production fork commit:
  `b9eea2884fa3f9ec57c9ce40701a1a9e7bcdf29e`
- Upstream baseline commit:
  `b9eea2884fa3f9ec57c9ce40701a1a9e7bcdf29e`
- Local checkout status at doc update: clean.

Current candidate images:

| Image | Digest |
| --- | --- |
| `ghcr.io/ppkflow/odm:3.6.0-ppkflow.1` | `sha256:b54fea7bf022db786aeb88c066d674a6895e0b8c7efa701e9a44a347f46f0d7e` |
| `ghcr.io/ppkflow/odm-gpu:3.6.0-ppkflow.1` | `sha256:e47cd7766fb5a0490a144a3a881e040cf684b63dc513cfdbb55b618603a6aeca` |
| `ghcr.io/ppkflow/photogrammetry-worker:0.1.14-telemetry-odm-ppkflow.4` | `sha256:11f0b059756dad492df85631be29e76d225e11af4f12e955ea551c1080ead1d7` |
| `ghcr.io/ppkflow/photogrammetry-worker-gpu:0.1.14-telemetry-odm-ppkflow.4` | `sha256:463fac3edef05a3ec4eb3dac50b23e8cb5e0cfdfe402c8350c6d2374b32ffc1e` |

The benchmark pipeline identity for this candidate is `ppkflow_odm`.

## Branch Model

- `master`: mirrors or tracks upstream ODM.
- `ppkflow/staging`: integrates candidate patches and build changes.
- `ppkflow/production`: contains only promoted commits. It should be
  fast-forwarded only after promotion evidence passes.

Rules:

- Do not promote directly from a dirty local checkout.
- Do not push customer-facing production jobs to `ppkflow/staging`.
- Do not use mutable image tags such as `latest` as promotion evidence.
- Do not mix risky algorithmic patches with low-risk build/metadata patches in
  the same production promotion unless the whole combined patchset has passed
  the full benchmark matrix.

## Staging Patch Queue

These patches have been ported into `ppkflow/staging`.

| Upstream PR / Issue | PPKflow status | Risk | Why it matters |
| --- | --- | --- | --- |
| PR #2021, ExifRead DJI MakerNote empty-value guard | Ported with regression coverage | Low | Prevents DJI metadata parsing failures from aborting jobs before SfM starts. |
| PR #2003, GPU/Kubernetes CUDA path fix | Ported with Dockerfile regression coverage | Low for GPU images | Helps Akash/Kubernetes GPU containers find CUDA/NVIDIA runtime paths. |
| PR #1994, SRT parsing and GPS altitude handling | Ported with static regression guards | Low-medium | Keeps sidecar/video telemetry and altitude handling from degrading georeferencing. |
| PR #1971, nested `image_groups.txt` recursion | Ported with static regression guards | Low | Protects staged/nested worker image package layouts. |
| PR #1980 and issue #1979, multi-channel TIFF image loading | Ported with static regression guards | Low-medium | Prepares future multispectral/stacked TIFF handling while preserving RGB workflows. |
| PR #1948, camera serial number in camera identity | Ported with static regression guards | Medium | Prevents accidental camera-model merging on multi-sensor datasets. |
| PR #1887 and issue #1853, respect `image_groups.txt` over split threshold | Partially ported: split-threshold override only | Low | Ensures explicit image groups are not overridden by automatic split behavior. |

Build and workflow changes on staging:

- Added `.github/workflows/ppkflow-build-images.yml` for GHCR ODM image builds.
- Disabled upstream ODM release workflows in the fork so they only run in
  `OpenDroneMap/ODM`.
- Cleaned Dockerfile warnings around undefined environment variables.
- Added fork-local regression tests:
  - `tests/test_ppkflow_exifread_compat.py`
  - `tests/test_ppkflow_gpu_dockerfile.py`
  - `tests/test_ppkflow_static_patch_guards.py`
- Added `PATCHES_PPKFLOW.md` inside the fork as the source-level patch queue.

## Tracked But Not Production-Ready

These are intentionally not part of a safe default-production promotion yet.

| Upstream PR | Status | Required treatment |
| --- | --- | --- |
| PR #1974, DJI gimbal yaw / OPK orientation handling | Candidate only | Needs DJI Enterprise fixture, PPKflow Brazil accuracy comparison, visual orthophoto check, and spray export validation. |
| PR #2008, topocentric dense reconstruction with final georeferencing | High-risk candidate only | Dedicated canary branch, not normal staging. Requires 20-photo, 174-photo, RTK-already-geotagged, CRS/bounds/GSD/nodata/DSM/DTM/LAZ/spray comparisons, and explicit operator approval. |

Treat these as separate releases. They touch accuracy-sensitive orientation,
georeferencing, or dense reconstruction behavior and should not ride along with
low-risk Docker or metadata fixes.

## Evidence Already Collected

Promotion note:

- `Docs/archive/odm-promotions/2026-05-18-0.1.11-odm-ppkflow.3.md`
- `Docs/archive/odm-promotions/2026-05-18-0.1.10-odm-ppkflow.2.md`

Completed gate evidence from that note:

- Worker image import/preflight passed for CPU and GPU images.
- 20-photo smoke CPU passed:
  `bench-smoke-20-v1-odm-fork-0110p2-smoke20-cpu-17-photo-b4a2fca4`.
- 20-photo smoke GPU passed:
  `bench-smoke-20-v1-odm-fork-0110p2-smoke20-gpu-17-photo-8d255703`.
- 174-photo `mapping_standard` CPU comparison passed:
  - public ODM: `3370.231s`
  - fork ODM: `3278.548s`
  - provider: `akash1aaul837r7en7hpk9wv2svg8u78fdq0t2j2e82z`
- 174-photo `spray_ortho_fast` GPU comparison passed:
  - public ODM: `1398.598s`
  - fork ODM: `1382.387s`
  - provider: `akash12v6dhc8awlwhv438jjyw80eguhgtm735mfv3fx`
- `/map`, `/preview`, `/tiles`, `/download`, and spray export passed on the
  CPU and GPU 174-photo fork runs.
- R2 output adoption and Akash teardown passed.
- Raster metadata QA passed.
- Final comparison rows recorded `pipeline`, worker image/digest, ODM
  image/digest, provider, and DSEQ.

Important caveats:

- This is good staging/internal-canary evidence, not enough to flip every
  customer job.
- Watcher remediation recovered callback dead-letter cases during the gate.
- The intermittent `/complete` HTTP 500 root cause still needs separate
  investigation even though watcher adoption can recover completed outputs.
- The local Docker build still showed a base-image dependency warning where
  `tifffile` requests `numpy>=2.1` while the worker pins `numpy==1.26.4`.

## Production Promotion Checklist

Run this sequence for every ODM fork candidate.

### 1. Freeze Candidate

Record:

- upstream ODM commit;
- fork staging commit;
- patch list;
- branch state;
- local dirty state;
- intended image tags.

Commands:

```bash
cd /Users/meijesibbel/PPKflow
Source/macMini/bin/ppkflow-odm-fork-status --checkout Source/ODM

cd /Users/meijesibbel/PPKflow/Source/ODM
git status --short
git log --oneline --decorate -n 20
git diff --name-status ppkflow/production..ppkflow/staging
```

Pass condition:

- checkout is clean;
- `ppkflow/staging` points to the intended candidate commit;
- patch list matches this roadmap and `Source/ODM/PATCHES_PPKFLOW.md`;
- high-risk candidate patches are not mixed into a normal promotion.

### 2. Run Fork Unit And Static Guards

At minimum:

```bash
cd /Users/meijesibbel/PPKflow/Source/ODM
python -m pytest \
  tests/test_ppkflow_exifread_compat.py \
  tests/test_ppkflow_gpu_dockerfile.py \
  tests/test_ppkflow_static_patch_guards.py
```

For larger patchsets, also run the broader ODM test subset affected by the
changed files.

Pass condition:

- all fork-local tests pass;
- no static guard is weakened to make the test pass;
- changed ODM behavior is covered by a fixture or a documented benchmark gate.

### 3. Build Immutable Images

Build ODM CPU/GPU bases from `ppkflow/staging`, then build PPKflow worker images
on top.

Required outputs:

- `ghcr.io/ppkflow/odm:<odm_tag>`
- `ghcr.io/ppkflow/odm-gpu:<odm_tag>`
- `ghcr.io/ppkflow/photogrammetry-worker:<worker_tag>-odm-ppkflow.<n>`
- `ghcr.io/ppkflow/photogrammetry-worker-gpu:<worker_tag>-odm-ppkflow.<n>`

Security rules:

- Record SHA256 digests immediately.
- Never use unpinned `latest` in benchmark evidence.
- GitHub workflow credentials must be scoped to package build/push only.
- Upstream release workflows must remain guarded so the fork does not try to
  publish upstream releases or require unrelated Azure signing credentials.

### 4. Register Candidate Provenance

Update the candidate values in:

- `Source/macMini/photogrammetry/pipeline_metadata.py`
- `Source/macMini/tests/test_run_photogrammetry_benchmark.py`
- `Source/macMini/tests/test_photogrammetry_benchmarks.py`

Do not change the production default worker image yet. The candidate should be
invoked explicitly as `--pipeline ppkflow_odm`.

Pass condition:

- benchmark launch records contain worker image, worker digest, ODM image, ODM
  digest, `pipeline=ppkflow_odm`, provider, and DSEQ;
- `bin/ppkflow-benchmark-report` groups the candidate separately from
  `production_odm`.

### 5. Run Operator Gates

Use the operator suite and benchmark launcher rather than ad hoc jobs.

Preflight:

```bash
cd /Users/meijesibbel/PPKflow/Source/macMini
source venv/bin/activate

bin/ppkflow-odm-integration-suite preflight --mode docker-worker \
  --worker-image ghcr.io/ppkflow/photogrammetry-worker:<candidate>

bin/ppkflow-odm-integration-suite preflight --mode akash --require-gpu \
  --worker-image ghcr.io/ppkflow/photogrammetry-worker-gpu:<candidate>
```

20-photo smoke:

```bash
python3 tools/run_photogrammetry_benchmark.py \
  --pipeline ppkflow_odm \
  --dataset-id smoke-20-v1 \
  --profile smoke_cpu \
  --product-preset spray_ortho_fast \
  --wait
```

174-photo CPU mapping comparison:

```bash
python3 tools/run_photogrammetry_benchmark.py \
  --pipeline production_odm \
  --dataset-id full-174-v1 \
  --profile standard_cpu \
  --product-preset mapping_standard \
  --wait

python3 tools/run_photogrammetry_benchmark.py \
  --pipeline ppkflow_odm \
  --dataset-id full-174-v1 \
  --profile standard_cpu \
  --product-preset mapping_standard \
  --wait
```

174-photo GPU spray comparison:

```bash
python3 tools/run_photogrammetry_benchmark.py \
  --pipeline production_odm \
  --dataset-id full-174-v1 \
  --profile mid_gpu \
  --product-preset spray_ortho_fast \
  --wait

python3 tools/run_photogrammetry_benchmark.py \
  --pipeline ppkflow_odm \
  --dataset-id full-174-v1 \
  --profile mid_gpu \
  --product-preset spray_ortho_fast \
  --wait
```

Endpoint and artifact checks:

```bash
bin/ppkflow-odm-integration-suite endpoint-check \
  --project-id <fork_project_id>

bin/ppkflow-odm-integration-suite compare \
  --candidate <fork_photogrammetry_result.json> \
  --baseline <production_photogrammetry_result.json>
```

Pass condition:

- required outputs present and non-empty;
- COGs readable;
- CRS, bounds, GSD, nodata, and artifact size deltas are inside tolerance;
- `/map`, `/preview`, `/tiles`, `/download`, and spray export pass;
- R2 uploads/adoption pass;
- Akash leases close;
- no watcher teardown risk remains;
- runtime/cost is not materially worse than production ODM unless explicitly
  accepted for a correctness fix.

### 6. Run Canary Soak

Before making the fork default, run at least:

- two additional internal canary jobs on different providers;
- one GPU canary with non-zero GPU telemetry;
- one direct-R2 input-mode canary when the release touches worker input or
  packaging;
- one multi-flight canary when the release touches grouping, split, image list,
  metadata, or georeferencing paths.

Pass condition:

- repeatable green results, not one lucky run;
- no provider-specific failure pattern;
- no new local disk retention or R2 orphan pattern;
- callback recovery is not masking a systematic `/complete` failure.

### 7. Write Promotion Record

Create or update a dated promotion record under:

- `Docs/archive/odm-promotions/YYYY-MM-DD-<candidate>.md`

It must include:

- branch and commit refs;
- patch list;
- image tags and digests;
- benchmark job IDs;
- provider/DSEQ IDs;
- artifact comparison paths;
- endpoint check paths;
- teardown status;
- open risks;
- explicit promote/no-promote decision.

### 8. Promote

Only after the promotion record says promote:

1. Fast-forward `ppkflow/production` to the approved staging commit.
2. Update production worker image references in the backend configuration or
   deployment environment to the approved worker image digest.
3. Keep `production_odm` benchmark identity until the default actually changes;
   then update docs and pipeline metadata so the baseline is clear.
4. Restart the backend cleanly.
5. Submit one production smoke job.
6. Watch adoption, endpoints, teardown, local GC, and R2 object retention.

Rollback:

- switch the production worker image back to public ODM worker `0.1.14-telemetry`;
- restart the backend;
- pause the fork pipeline in benchmark tooling if needed;
- leave the failed candidate on staging/canary for analysis;
- add the failure to the promotion record.

## Secure Rolling Release Policy

Use a staged rollout even after a green promotion:

1. Operator-only canary: launch with `--pipeline ppkflow_odm`; no automatic
   customer routing.
2. Internal default: use for PPKflow-owned test jobs only.
3. Small customer canary: only jobs that can be rerun and have known-good R2
   inputs.
4. Product-lane default: enable for one lane, such as `spray_ortho_fast`, not
   all photogrammetry.
5. Full default: only after multiple dataset sizes, CPU/GPU profiles,
   multi-flight inputs, direct-R2 inputs, and recovery/GC behavior are green.

Controls:

- Image digests are mandatory for promotion decisions.
- Promotion records are mandatory before changing defaults.
- High-risk georeferencing or dense reconstruction patches require a separate
  branch and a separate promotion record.
- Frontend/Lovable should not receive ODM fork internals; UI still sees normal
  photogrammetry statuses and artifacts.
- Public browser code must never receive `X-API-Key`; claim-token flow remains
  unchanged.
- Rollback must be a config/image-reference change, not a source-code surgery.

## Near-Term Roadmap

1. Keep public ODM worker `0.1.14-telemetry` as production default.
2. Run two more `0.1.14-telemetry-odm-ppkflow.4` canary jobs on different Akash
   providers.
3. Investigate intermittent `/complete` HTTP 500 root cause so watcher recovery
   is a safety net, not the normal completion path.
4. Add a multispectral TIFF fixture before treating PR #1980 as production
   evidence for multispectral jobs.
5. Add a dual-camera or multispectral fixture before relying on PR #1948 for
   multi-sensor production behavior.
6. Keep PR #1974 and PR #2008 out of normal production promotion until they
   have their own canary branches and accuracy reports.
7. Once canaries are repeatably green, promote `ppkflow/production` and update
   production image references by digest.

## Useful References

- Fork patch queue: `Source/ODM/PATCHES_PPKFLOW.md`
- Current pipeline registry:
  `Source/macMini/photogrammetry/pipeline_metadata.py`
- Benchmark launcher:
  `Source/macMini/tools/run_photogrammetry_benchmark.py`
- Operator gate suite:
  `Source/macMini/bin/ppkflow-odm-integration-suite`
- Benchmark report:
  `Source/macMini/bin/ppkflow-benchmark-report`
- Promotion archive:
  `Docs/archive/odm-promotions/`
