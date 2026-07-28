# Zyxel NWA1123-ACv2 Security Assessment

Security research and configuration analysis of the **Zyxel NWA1123-ACv2**, an End-of-Life wireless access point that remains widely deployed in small business and home-office settings despite no longer receiving firmware security updates.

📄 **[Read the full report](./report/SECURITY_ASSESSMENT.md)**

## TL;DR

- Device: Zyxel NWA1123-ACv2, firmware `<version>`, EOL as of `<date>`
- Key finding: WPA-PSK passphrase is stored **in cleartext** in the device's configuration backup/export file no cracking required if a backup file is ever exposed
- `<second finding one-liner>`
- Scope: personally owned hardware, isolated test network, no third-party systems involved

## Why this exists

EOL network hardware doesn't disappear from real deployments the day vendor support ends — it keeps running, often for years, in places where nobody's tracking its patch status. This repo documents a structured configuration review of one such device, written in the format of a standard attack & penetration report, to (a) flag a concrete, actionable finding for anyone still running this hardware, and (b) serve as a worked example of applied security research methodology.

## Repo structure

```
├── report/
│   └── SECURITY_ASSESSMENT.md   # Full report: findings, evidence, severity, recommendations
├── evidence/                    # Redacted screenshots / config excerpts
├── scripts/                     # Analysis tooling used during the assessment
└── references/                  # CVE references, vendor documentation links
```

## Methodology

Assessment approach is outlined in detail in [§3 of the report](./report/SECURITY_ASSESSMENT.md#3-methodology), broadly aligned with PTES configuration-review phases and OWASP IoT/firmware testing guidance.

## Ethics & scope

This assessment was performed solely against hardware owned by the assessor, on an isolated network, with no third-party systems, users, or live traffic involved. All sensitive values (credentials, network identifiers) have been redacted from this public repository. See [§9 of the report](./report/SECURITY_ASSESSMENT.md#9-scope--ethics-statement) for the full statement.

## License

`<MIT / CC-BY, your call — MIT for scripts, CC-BY for the report is a common split>`
