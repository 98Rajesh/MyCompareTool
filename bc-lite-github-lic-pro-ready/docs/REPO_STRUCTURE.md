# BC-Lite / BC-Lite Pro Repository Strategy

This repository is designed to host **both** the open-source BC-Lite edition and the commercial
BC-Lite Pro edition using **branches and build flags**, rather than separate repos.

## Branch Model

- `main`:
  - Edition: **BC-Lite**
  - License: MIT (see `LICENSE`)
  - Public features only

- `pro`:
  - Edition: **BC-Lite Pro**
  - License: Proprietary (see `LICENSE-PRO` in `pro` branch)
  - Includes Pro-only modules and license enforcement

## Suggested Workflow

- Develop core features on `main` (Lite).
- Merge or cherry-pick selected commits from `main` into `pro`.
- Pro-specific features live in:
  - `app/pro_features/`
  - or guarded by edition checks in code.

## Local Setup Commands (example)

```bash
# create pro branch from main
git checkout main
git checkout -b pro
git push -u origin pro
```

CI and build scripts read the current branch (`github.ref_name`) to decide whether
to build Lite or Pro binaries.
