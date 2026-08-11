# Security Policy

## Reporting a vulnerability

Do **not** publish a suspected vulnerability that could expose DEV.to API credentials or locally collected account data.

Preferred reporting path:

1. Use **Security → Report a vulnerability** for this repository when GitHub private vulnerability reporting is available.
2. Otherwise email **badbanana@proton.me** with the subject `devto-analytics-pro security report`.

Include the affected commit/version, reproduction steps, expected and observed behavior, impact, and any proposed mitigation. Redact API keys and unrelated personal data.

## Security-relevant scope

Reports are especially useful for issues involving:

- exposure of `DEVTO_API_KEY` through logs, files, subprocess arguments, or exports;
- unsafe handling of DEV.to API responses or locally exported data;
- unintended writes outside operator-selected output paths;
- CSV/JSON export behavior that can corrupt or expose data unexpectedly;
- HTTP behavior that bypasses documented authentication or privacy assumptions;
- dependency issues with a meaningful exploit path.

The preferred `dev_env.py` entrypoint exists specifically to keep the API key out of the normal process argument vector. Regressions in that boundary are security-relevant.

## Supported state

Report findings against the current default branch or identify the exact historical commit affected. Changes in DEV.to's external API availability or schema are integration issues unless they create a security impact in this client.

## Disclosure

I aim to acknowledge reproducible reports within seven days. Validation and remediation timing depends on severity and reproducibility; no fixed remediation deadline is promised before triage.

Confirmed fixes should be documented when practical. Reporter credit is welcome unless anonymity is requested.
