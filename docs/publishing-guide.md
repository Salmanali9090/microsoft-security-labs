# Publishing guide (do these steps yourself – no tool has access to your GitHub)

## 1. Prepare locally
```bash
unzip microsoft-security-labs.zip && cd microsoft-security-labs
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
pytest -q                                           # all tests must pass
```
Read the whole repo once. Replace `<your-username>` in the README clone URL.

## 2. Create the GitHub repository
1. GitHub → **New repository** → name `microsoft-security-labs` → **Public** → do **not** add README/licence (they already exist).
2. Description: *Original, synthetic-data labs for Microsoft security: SC-900, SC-200, SC-500, KQL detections.*
3. Topics: `microsoft-sentinel`, `kql`, `soc`, `microsoft-security`, `cybersecurity`, `azure`, `detection-engineering`.

## 3. Push
```bash
git init -b main
git add .
git commit -m "Initial release: SC-900/SC-200/SC-500 labs, KQL detections, tests"
git remote add origin https://github.com/<your-username>/microsoft-security-labs.git
git push -u origin main
```
Authenticate with GitHub's browser login or a personal access token. **Never paste tokens into chats, files or commits.**

## 4. After pushing
- **Settings → Security → Private vulnerability reporting → Enable** (SECURITY.md refers to it).
- Confirm the **Actions** tab shows a green CI run; add the badge if you like.
- Check that Mermaid diagrams render on GitHub; fix any that do not.
- Create a release `v0.1.0` and write truthful notes.

## 5. Raise the verification level (most valuable next step)
Run the six queries in a lab Log Analytics/Sentinel workspace, save screenshots in `docs/evidence/`, update each detection's `Status` and [verification-matrix.md](verification-matrix.md). Only then may you say a query "ran in a live workspace".

## 6. Evidence for an MVP nomination
Record: repository URL, commit history dates, stars/forks/issues (real numbers), any external contributions with PR links and status, and event or article links. Do not claim merged contributions until the status is verified.
