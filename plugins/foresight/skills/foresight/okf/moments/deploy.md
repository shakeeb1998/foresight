---
type: moment
title: deploy
tags: [tripwire]
resource: deploy
timestamp: 2026-10-08
---

# Moment · deploy

Before deploying or saying merged / deployed / live. Re-check before moving on:

- [FS-12](../patterns/fs-12.md) Deploy pipeline doesn't carry or match what the change needs - For every new route/port/unit/env var, confirm the deploy script installs it and curl the real public path after deploy
- [FS-24](../patterns/fs-24.md) Pushed, merged or deployed state assumed instead of checked - Verify with git ls-remote / gh pr list / gh run list for the exact SHA and confirm origin/<base> contains the commit
- [FS-50](../patterns/fs-50.md) Live-data fix applied without re-detecting and confirming the exact target rows - Print and confirm an identifying fact from the connected DB (row counts, a known location name) before any --apply
- [FS-44](../patterns/fs-44.md) Migration unsafe for code or data already in the shared DB - Set db_default (or nullable + backfill) for new required fields; run sqlmigrate and reject bare ADD COLUMN NOT NULL on shared tables
- [FS-66](../patterns/fs-66.md) Session-scoped cloud or CLI credentials assumed still valid - Run a cheap identity check first (aws sts get-caller-identity, CLI auth status) and ask the user to re-auth up front if it fails
- [FS-61](../patterns/fs-61.md) Startup path echoes production credentials into captured output - Invoke remote commands with a non-login shell (bash --noprofile --norc, no -l/-i) and prefer management commands or script files over manage.py shell
- [FS-71](../patterns/fs-71.md) Store build inputs taken from local state instead of asserted against the release target - Before archiving, query ASC appStoreVersions/builds (and Play tracks) for the highest approved/READY_FOR_SALE version and highest build, and bump the marketing version strictly above any closed train
- [FS-65](../patterns/fs-65.md) Which host, checkout or branch serves an environment assumed - Read the service's systemd unit WorkingDirectory and venv, then check git -C <that dir> rev-parse HEAD and its branch before verifying or restarting
- [FS-73](../patterns/fs-73.md) Native build started without a host preflight (SDK path, UTF-8 locale, disk, gitignored config) - Run a preflight before every native build: ANDROID_HOME/adb set and android/local.properties has sdk.dir, LANG=en_US.UTF-8 and LC_ALL=en_US.UTF-8 exported, df -h shows headroom, and every required gitignored file exists
- [FS-93](../patterns/fs-93.md) Live service config edited without a parse check and a post-restart re-read - Write config through a script file or a drop-in copied to the host, not multi-layer quoted inline commands
- [FS-75](../patterns/fs-75.md) Generated native project or build cache not regenerated after a config, asset or cache change - After any asset/config/plugin change or cache wipe, run expo prebuild --clean for BOTH ios and android (then pod install) before building; never trust incremental xcodebuild for assets
- [FS-88](../patterns/fs-88.md) Mobile OAuth client bound to a signing key or cloud project other than the one real installs use - Record the GCP project id of the webClientId and create every Android/iOS OAuth client in that same project; check it before registering any SHA-1
- [FS-104](../patterns/fs-104.md) Smoke or verification write run against a live production target - Smoke-test writes against a dedicated throwaway target; use read-only probes on live targets
