# C4 — <system> (Mermaid, 4 levels)

## L1 Context
```mermaid
flowchart TB
  FI[Financial Institution / KYC] -->|submits identity inputs| SHIELD[SHIELD-ID Detection API]
  SHIELD -->|trust score + token| FI
```
## L2 Container · L3 Component · L4 Code
<containers: API · Layer1 · Layer2 · eval harness · data pipeline>
> Lives in `.context/ARCHITECTURE.md`. Instantiate from modelo_documentacao/, extend with ML sections.
