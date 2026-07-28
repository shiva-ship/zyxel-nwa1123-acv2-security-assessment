# Security Assessment Report

## Zyxel NWA1123-ACv2 Wireless Access Point — End-of-Life Firmware & Configuration Analysis

| | |
|---|---|
| **Target** | Zyxel NWA1123-ACv2 |
| **Firmware Version** | `<FILL IN — e.g. V5.30(ABYE.x)>` |
| **Assessment Type** | Configuration & firmware security review (white-box, device owned by assessor) |
| **Assessor** | `<Your Name>` |
| **Assessment Date(s)** | `<FILL IN>` |
| **Report Date** | `<FILL IN>` |
| **Classification** | Public (post-redaction) |
| **Report Version** | 1.0 |

---

## Document Control

| Version | Date | Author | Change |
|---|---|---|---|
| 0.1 | `<date>` | `<name>` | Initial draft |
| 1.0 | `<date>` | `<name>` | Published version, redacted for public release |

---

## 1. Executive Summary

This report documents a security assessment of the Zyxel NWA1123-ACv2, a wireless access point that reached End-of-Life (EOL) / End-of-Support status on `<FILL IN — check Zyxel's EOL list>` and is no longer receiving firmware security updates. Despite EOL status, this device (and its product family) remains deployed in small business and home-office environments due to its historical reliability and continued secondhand availability.

The assessment was conducted by the device owner against a unit under their own control, for research and educational purposes. No third-party networks, infrastructure, or devices were accessed or tested.

**Key findings:**

| # | Finding | Severity |
|---|---|---|
| 1 | WPA-PSK stored in cleartext within configuration backup export | `<High/Medium — assign after reading §5.1>` |
| 2 | `<Known CVE finding — fill in once cross-referenced>` | `<TBD>` |
| 3 | `<Additional finding if any>` | `<TBD>` |

The most significant finding is that the device's configuration backup/export function stores the WPA-PSK passphrase in cleartext rather than encrypted or hashed, meaning anyone who obtains a config backup file (via device access, weak backup storage practices, or interception) recovers the live Wi-Fi password directly, with no cracking required.

Because this device is EOL, there is no active vendor security contact to receive a coordinated disclosure, and no patch will be issued. This report is published for community awareness so that current owners of this hardware can take compensating action (see §7, Recommendations).

---

## 2. Scope

### 2.1 In Scope
- Zyxel NWA1123-ACv2 hardware unit owned by the assessor
- Web management interface (local, authenticated)
- Configuration export/backup file format and contents
- Firmware version identification and CVE cross-referencing
- `<add: CLI/Telnet/SSH if tested>`

### 2.2 Out of Scope
- Any device, network, or infrastructure not owned by the assessor
- Any third party's deployment of this hardware
- Physical/hardware attacks (JTAG, UART, flash extraction) — `<remove this line if you did do hardware-level work>`
- Denial-of-service testing

### 2.3 Rules of Engagement
This was a self-authorized assessment of personally owned hardware on an isolated test network. No production network, third-party asset, or live user traffic was involved at any point.

---

## 3. Methodology

This assessment followed a structured approach broadly aligned with configuration-review methodology from frameworks such as OWASP's Firmware/IoT testing guidance and PTES (Penetration Testing Execution Standard) configuration-analysis phases, adapted for a single-device, white-box context:

1. **Reconnaissance** — identify exact model, firmware version, and hardware revision
2. **CVE cross-referencing** — check firmware version against NVD/vendor advisories for known vulnerabilities
3. **Configuration export analysis** — export device backup config, examine file format and storage of sensitive fields
4. **Access control review** — assess management interface authentication (default credentials, session handling, protocol used — HTTP vs HTTPS)
5. **Documentation** — record findings, evidence, severity, and remediation guidance

### 3.1 Tools Used
- `<e.g. Zyxel Web GUI>`
- `<e.g. a text editor / hex editor for config file inspection>`
- `<any scripts you wrote — see /scripts folder>`
- NVD (nvd.nist.gov) for CVE cross-referencing

---

## 4. Device & Environment Details

| Field | Value |
|---|---|
| Model | Zyxel NWA1123-ACv2 |
| Hardware revision | `<FILL IN, check underside label>` |
| Firmware version | `<FILL IN>` |
| EOL / EOS date | `<FILL IN from Zyxel's site>` |
| Management access | `<Web GUI over HTTP/HTTPS, port X>` |
| Test network | Isolated lab segment, no internet-facing exposure |

---

## 5. Findings

Each finding follows: **Description → Evidence → Impact → Severity → Recommendation**, consistent with standard pentest report structure (CVSS-informed severity rather than a formal CVSS vector, since this is a single-host config review rather than a network engagement).

### 5.1 Finding 1: Cleartext Storage of WPA-PSK in Configuration Backup

**Severity:** `<High — recommend assigning this given plaintext credential exposure; confirm your own rationale here>`

**Description:**
The device's configuration export/backup feature (`<Maintenance > Backup/Restore>` or equivalent menu path) produces a file that includes the active WPA-PSK passphrase stored in cleartext, rather than as a hash or in an encrypted container.

**Evidence:**
```
<Insert REDACTED excerpt here — replace actual PSK with a placeholder like Sample1234#
Example format, not your real data:
wpa-psk <REDACTED — 12 chars, alphanumeric+special>
>
```
> ⚠️ Do not include the real PSK value in the public repo. Show the *field/structure* only.

**Impact:**
Any party who obtains a configuration backup file — through device compromise, insecure backup storage (e.g., backups left on a shared drive, emailed, or committed to a repo by mistake), or interception during export — recovers the live network passphrase immediately, with no offline cracking (e.g., hashcat against a captured 4-way handshake) required. This collapses what should be a computationally expensive attack into a trivial file-read.

**Root Cause:**
The backup/restore feature appears designed for operational convenience (full state restore) without treating the config export itself as a sensitive credential store requiring its own protection (e.g., encryption at rest, or masking with a "re-enter to change" pattern common on modern router firmware).

**Recommendation:**
- Immediate (compensating control, since no patch exists): treat all config backups as sensitive material — store encrypted, restrict access, never transmit unencrypted
- Rotate the WPA-PSK if any backup file has ever been stored insecurely or shared
- Long-term: replace EOL hardware with a supported model where backup exports mask or encrypt credential fields

---

### 5.2 Finding 2: `<Known CVE(s) applicable to this firmware — fill in>`

**Severity:** `<TBD>`

**Description:**
`<Cross-reference the exact firmware version against NVD. Search "Zyxel NWA1123-ACv2 CVE" and "Zyxel NWA1123 firmware CVE" — list any that apply to your confirmed firmware version.>`

**Evidence:**
`<CVE ID, NVD link, confirmation your firmware version is in the affected range>`

**Impact:**
`<per the CVE description>`

**Recommendation:**
`<per the CVE's official guidance, or "no vendor patch available due to EOL status — see general recommendations in §7">`

---

### 5.3 Finding 3: `<Management Interface / Transport Security — fill in if applicable>`

`<e.g. if the web GUI is reachable over HTTP without forced HTTPS redirect, or uses a weak default session mechanism, document it here in the same format.>`

---

## 6. Risk Summary

| Finding | Severity | Exploitability | Status |
|---|---|---|---|
| Cleartext PSK in backup | `<High>` | Requires access to backup file | Unpatched (EOL) |
| `<CVE finding>` | `<TBD>` | `<TBD>` | Unpatched (EOL) |

---

## 7. Recommendations

**For current owners of this hardware:**
1. Treat configuration backups as credential material — encrypt at rest, restrict access, never store in plaintext on shared or cloud storage without encryption
2. Rotate the WPA-PSK immediately if any backup has ever left your direct control
3. Where possible, migrate to actively supported hardware, particularly for any deployment handling sensitive traffic
4. If continued use is unavoidable, isolate the device on its own VLAN/segment and disable remote management

**For the broader community:**
This pattern (credentials stored in cleartext within "convenience" export/backup features) is common across consumer and SMB network hardware. When evaluating or auditing similar EOL devices, checking backup/export file contents is a fast, high-value first step.

---

## 8. Disclosure Timeline

| Date | Event |
|---|---|
| `<date>` | Finding identified during personal research |
| `<date>` | Confirmed device is EOL with no active vendor security contact channel |
| `<date>` | Report finalized and published to public GitHub repository for community awareness |

Because Zyxel's EOL policy for this product line means no security patches will be issued and no formal vulnerability-disclosure channel is maintained for this model, this report is published directly rather than held under a private disclosure embargo. This is consistent with common industry practice for EOL hardware research (see e.g. how researchers at Tenable/Rapid7 handle EOL-device findings — publish with clear EOL context rather than withhold indefinitely).

---

## 9. Scope & Ethics Statement

This assessment was performed exclusively against hardware owned by the assessor, on an isolated test network with no third-party systems, users, or traffic involved. No credentials, configuration data, or personally identifiable information from the assessor's live network are included in this public report; all sensitive values have been redacted or replaced with representative placeholders.

---

## 10. References

- NVD — National Vulnerability Database: https://nvd.nist.gov/
- Zyxel Product EOL/EOS list: `<insert link once you check it>`
- PTES (Penetration Testing Execution Standard): http://www.pentest-standard.org/
- OWASP Firmware Security Testing Methodology: https://owasp.org/www-project-iot-security-testing-guide/

---

## Appendix A: Redacted Configuration Excerpt

`<Place sanitized config snippets here — full file should NOT be committed if it contains any real network identifiers>`

## Appendix B: Tools & Scripts

See `/scripts` in this repository for any analysis tooling used during this assessment.
