# Architecture

## Repository data flow
```mermaid
flowchart LR
    GEN[generate_sample_data.py] --> SD[(sample-data)]
    SD --> MIR[tests/detection_logic.py]
    DET[detections/*.kql] --> BLD[build_datatable_queries.py]
    SD --> BLD
    BLD --> LQ[SC-200/lab-queries]
    MIR --> PYT[pytest]
    LQ --> PYT
    PYT --> CI[GitHub Actions CI]
```
Design principles: reproducible (everything generated or tested by script), honest (status labels on every artifact), safe (synthetic data only, secret scanning in tests).

## Target cloud environment (optional lab)
```mermaid
flowchart TB
    subgraph Identity
        ENT[Microsoft Entra ID<br/>sign-in + audit logs]
    end
    subgraph Azure["Azure subscription (lab)"]
        ACT[Azure Activity log]
        RES[Storage / AI / Key Vault]
        POLICY[Azure Policy]
    end
    subgraph Endpoint
        MDE[Defender for Endpoint<br/>DeviceProcessEvents]
    end
    ENT --> LAW[(Log Analytics workspace)]
    ACT --> LAW
    MDE --> LAW
    RES --> LAW
    POLICY -.-> RES
    LAW --> SENT[Microsoft Sentinel<br/>analytics rules, incidents]
    SENT --> DEF[Microsoft Defender portal<br/>unified SecOps]
```
Note: Microsoft has stated the Azure-portal management experience for Sentinel sunsets on 31 March 2027; plan for the Defender portal ([references](references.md)). Defender-portal Advanced Hunting uses `Timestamp`, whereas Log Analytics uses `TimeGenerated`.

## Table-to-detection map
| Table | Detections |
|---|---|
| SigninLogs | 01, 02 |
| AuditLogs | 03 |
| DeviceProcessEvents | 04 |
| AzureActivity | 05, 06 |
