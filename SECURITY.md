# Security Policy

## Scope
This repository contains educational content, synthetic data and detection examples. It does **not** contain production systems or real telemetry.

## Reporting a vulnerability or sensitive-data exposure
If you find (a) a real credential, token or personal data accidentally committed, or (b) content that could cause harm if followed as written, please **do not open a public issue**. Use GitHub's *private vulnerability reporting* ("Security" tab → "Report a vulnerability") on this repository. Include the file path and what you found. I aim to acknowledge reports within 7 days and remove sensitive data promptly.

## Safe-use rules for the labs
- Run cloud labs **only** in a dedicated lab subscription/tenant you own. Never run them against production or an employer's environment.
- Never commit real keys, connection strings, tenant IDs or logs from your workplace. Use `.env` files (git-ignored) for local secrets.
- Detections are examples: tune and validate them in your own environment before use.

## No warranty
Provided "as is" under the MIT License. Not an official Microsoft resource.
