# Licensing Model (BC-Lite vs BC-Lite Pro)

This repository supports:

- **BC-Lite** (open-source, MIT)
- **BC-Lite Pro** (commercial, license-checked)

## Editions

- Lite:
  - Built from `main` branch.
  - Uses `EDITION = "lite"` (default).
  - No license required.

- Pro:
  - Built from `pro` branch.
  - Sets environment variable `BC_LITE_EDITION=pro` during build or in launcher.
  - On startup, calls `licensing.check_license("pro")`.

## License File

Path (by default):

- Linux/macOS: `~/.bc-lite/license.json`
- Windows: `C:\Users\<User>\.bc-lite\license.json`
- Or override with `BC_LITE_CONFIG_DIR` environment variable.

### Example `license.json`

```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "edition": "pro",
  "machine_id": "HOSTNAME-abcdef123456",
  "expires_at": "2026-01-01T00:00:00",
  "signature": "deadbeefcafebabe..."
}
```

The `signature` is an HMAC-SHA256 over the other fields, using a secret key
embedded in `licensing.py` (**you MUST change this for real use** and ideally
move to asymmetric crypto).

## Trial Mode

If no license file exists, the module:

- Creates `~/.bc-lite/trial.json` with a `started_at` timestamp.
- Allows **14 days** of trial (configurable via `TRIAL_DAYS`).
- After expiry, Pro mode will refuse to start and show a license error dialog.

Lite builds ignore the license and always run.

## Machine Lock

`machine_id` is derived from:

- `platform.node()` (hostname)
- `uuid.getnode()` (MAC-ish value)

It is not bulletproof, but sufficient for a basic machine-locked license.

To generate a license for a specific machine, you can:

1. Run a small helper locally (or in a vendor tool) which calls
   `licensing.generate_license_template(...)` with the correct machine ID.
2. Save the returned JSON as `license.json` on the client machine.
