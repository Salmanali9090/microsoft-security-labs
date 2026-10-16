# Lab 02 – Data protection: hardened storage account (Bicep)

**Goal:** deploy (in a lab) a storage account with secure defaults and verify the settings.
**Docs:** [Azure Storage security recommendations](https://learn.microsoft.com/azure/storage/blobs/security-recommendations)

## What the template sets and why
| Setting | Value | Why it matters |
|---|---|---|
| `supportsHttpsTrafficOnly` | `true` | Data in transit is encrypted (no plain HTTP) |
| `minimumTlsVersion` | `TLS1_2` | Rejects older, weaker TLS versions |
| `allowBlobPublicAccess` | `false` | Prevents anonymous (public) blob access |
| `allowSharedKeyAccess` | `false` | Forces Microsoft Entra authorization instead of long-lived account keys |
| `defaultToOAuthAuthentication` | `true` | Portal tools default to Entra auth |
| `publicNetworkAccess` | `Disabled` (parameter) | No internet exposure; use private endpoints or enable deliberately |
| `networkAcls.defaultAction` | `Deny` | Deny by default if public access is enabled |
| Blob soft delete | 7 days | Recover from accidental or malicious deletion |

⚠️ Consequences: with shared-key access off, tools using account keys/SAS signed with keys will fail – use Entra roles (for example *Storage Blob Data Contributor*). With public network access disabled you cannot reach the account from the internet.

## Verification status
- ✅ **Compiled:** `bicep build main.bicep` succeeded with Bicep CLI 0.48.1 on 2026-10-16 (exit 0, no warnings). This checks syntax and type validity only.
- ⚠️ **Not deployed** by the author to a live subscription. Deployment results are unverified.

## Deploy (lab only, ⚠️ untested by the author)
```bash
az group create -n rg-lab-storage -l <region>
az deployment group create -g rg-lab-storage \
  --template-file SC-500/labs/02-data-protection-storage/main.bicep \
  --parameters storageAccountName=<globally-unique-name>
```
## Validate settings
```bash
az storage account show -g rg-lab-storage -n <name> \
  --query "{https:enableHttpsTrafficOnly, tls:minimumTlsVersion, publicBlob:allowBlobPublicAccess, sharedKey:allowSharedKeyAccess}"
```
Expected: `https: true`, `tls: TLS1_2`, `publicBlob: false`, `sharedKey: false`.
Then run Lab 01's policy against this account and confirm it is compliant.

## Clean up
```bash
az group delete -n rg-lab-storage --yes
```
