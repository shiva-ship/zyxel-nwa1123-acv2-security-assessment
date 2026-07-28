# Security Assessment Report

## Zyxel NWA1123-ACv2 Wireless Access Point — End of Life Firmware & Configuration Analysis

| | |
|---|---|
| **Target** | Zyxel NWA1123-ACv2 |
| **Firmware Version** | V5.00(ABEL.3), firmware family code ABEL (confirmed from configuration export headers) |
| **Assessment Type** | Configuration and firmware security review, white box, device owned by assessor |
| **Assessor** | `<Your Name>` |
| **Assessment Date(s)** | `<FILL IN>` |
| **Report Date** | `<FILL IN>` |
| **Classification** | Public, post redaction |
| **Report Version** | 1.0 |

---

## Document Control

| Version | Date | Author | Change |
|---|---|---|---|
| 0.1 | `<date>` | `<name>` | Initial draft |
| 1.0 | `<date>` | `<name>` | Published version, redacted for public release |

---

## 1. Executive Summary

This report documents a security assessment of the Zyxel NWA1123-ACv2, a wireless access point that reached End of RMA and Tech Support status on 2023-01-31 (per Zyxel staff communication on the Zyxel Community forum, since Zyxel's public EOL list does not itemize every legacy model individually) and is no longer receiving firmware security updates. Despite EOL status, this device (and its product family) remains deployed in small business and home office environments due to its historical reliability and continued secondhand availability.

The assessment was conducted by the device owner against a unit under their own control, for research and educational purposes. No third party networks, infrastructure, or devices were accessed or tested.

**Key findings:**

| # | Finding | Severity |
|---|---|---|
| 1 | WPA-PSK stored in cleartext within configuration backup export | High |
| 2 | Hardcoded FTP service credentials (SEC Consult SA-20190829-0), no CVE number assigned by vendor, affecting firmware 5.50 patch 0 and earlier, this device runs 5.00(ABEL.3) and is within the affected range | High |
| 3 | Weak, unrotated WDS pre-shared key (`87654321`, eight numeric characters) | Medium |
| 4 | SNMP v2c enabled, community string based, unauthenticated and unencrypted | Medium |

The most significant finding is that the device's configuration backup and export function stores the WPA-PSK passphrase in cleartext rather than encrypted or hashed, meaning anyone who obtains a config backup file (via device access, weak backup storage practices, or interception) recovers the live Wi-Fi password directly, with no cracking required. This is compounded by Finding 2, a separately disclosed hardcoded FTP credential vulnerability affecting this exact firmware range, which means the configuration file containing that same cleartext PSK can potentially be retrieved from the device itself by an unauthenticated attacker on the local segment, without ever needing management interface access.

Because this device is EOL, there is no active vendor security contact to receive a coordinated disclosure, and no patch will be issued for firmware level issues going forward. This report is published for community awareness so that current owners of this hardware can take compensating action (see Section 7, Recommendations).

---

## 2. Scope

### 2.1 In Scope
- Zyxel NWA1123-ACv2 hardware unit owned by the assessor
- Web management interface (local, authenticated)
- Configuration export and backup file format and contents (`lastgood.conf`, `startup-config.conf`, `autobackup-5_00.conf`, `system-default.conf`, `oldfwid`)
- Firmware version identification and CVE/advisory cross referencing
- `<add: CLI/Telnet/SSH if tested directly against the live device>`

### 2.2 Out of Scope
- Any device, network, or infrastructure not owned by the assessor
- Any third party's deployment of this hardware
- Physical and hardware level attacks (JTAG, UART, flash extraction), not performed as part of this assessment
- Denial of service testing

### 2.3 Rules of Engagement
This was a self authorized assessment of personally owned hardware on an isolated test network. No production network, third party asset, or live user traffic was involved at any point.

---

## 3. Methodology

This assessment followed a structured approach broadly aligned with configuration review methodology from frameworks such as OWASP's Firmware/IoT testing guidance and PTES (Penetration Testing Execution Standard) configuration analysis phases, adapted for a single device, white box context:

1. **Reconnaissance**, identify exact model, firmware version, and hardware revision from configuration export headers
2. **CVE and advisory cross referencing**, check firmware version against NVD and vendor/third party advisories for known vulnerabilities
3. **Configuration export analysis**, review five exported/backup configuration files, examine file format and storage of sensitive fields
4. **Access control review**, assess management interface authentication (default credentials, session handling, protocol used, HTTP versus HTTPS versus SSH versus FTP)
5. **Documentation**, record findings, evidence, severity, and remediation guidance

### 3.1 Tools Used
- Zyxel Web GUI and CLI configuration export
- Plain text inspection of exported `.conf` files (standard Zyxel CLI configuration syntax, CRLF line terminated)
- NVD (nvd.nist.gov) for CVE cross referencing
- SEC Consult public advisory archive for non CVE numbered disclosures
- `<any additional scripts you wrote, see /scripts folder>`

---

## 4. Device & Environment Details

| Field | Value |
|---|---|
| Model | Zyxel NWA1123-ACv2 |
| Hardware revision | Not present in configuration export, obtain from device underside label or Web GUI system information page |
| Firmware version | V5.00(ABEL.3), timestamp on the reviewed configuration files reads `saved at 2017-04-07`, meaning this reflects the firmware at the time the backup was taken, confirm currently installed version separately since it may have been updated since |
| Firmware family code | ABEL (confirmed via `oldfwid` file) |
| EOL / EOS date | End of RMA and Tech Support, 2023-01-31 (Zyxel Community staff communication, no dedicated public EOL page entry found for this specific sub model at time of writing) |
| Management access | HTTP (`ip http server`), HTTPS with default certificate and forced redirect from HTTP (`ip http secure-server cert default`, `ip http secure-server`, `ip http secure-server force-redirect`), SSH (`ip ssh server cert default`, `ip ssh server`), and FTP (`ip ftp server cert default`, `ip ftp server`), all enabled simultaneously in the reviewed configuration |
| Test network | Isolated home lab segment, no internet facing exposure |

---

## 5. Findings

Each finding follows: **Description, Evidence, Impact, Severity, Recommendation**, consistent with standard pentest report structure (CVSS informed severity rather than a formal CVSS vector, since this is a single host configuration review rather than a network engagement).

### 5.1 Finding 1: Cleartext Storage of WPA-PSK in Configuration Backup

**Severity:** High

**Description:**
The device's configuration export and backup feature (`Maintenance > Backup/Restore` in the Web GUI, or CLI configuration dump) produces a file that includes the active WPA-PSK passphrase stored in cleartext, rather than as a hash or in an encrypted container.

**Evidence:**
```
wlan-security-profile QI-Prof
 mode wpa2
 eap external
 idle 300
 wpa-psk <REDACTED, 15 characters, mixed case alphanumeric plus one special character>
 wpa-encrypt auto
 group-key 30000
```
> Do not include the real PSK value in the public repository. Show the field and structure only, as above.

**Impact:**
Any party who obtains a configuration backup file, through device compromise, insecure backup storage (for example backups left on a shared drive, emailed, or committed to a repository by mistake), or interception during export, recovers the live network passphrase immediately, with no offline cracking (for example hashcat against a captured four way handshake) required. This collapses what should be a computationally expensive attack into a trivial file read.

**Root Cause:**
The backup/restore feature appears designed for operational convenience (full state restore) without treating the configuration export itself as a sensitive credential store requiring its own protection, for example encryption at rest, or a mask and re-enter to change pattern common on modern router firmware.

**Recommendation:**
- Immediate (compensating control, since no patch exists), treat all configuration backups as sensitive material, store encrypted, restrict access, never transmit unencrypted
- Rotate the WPA-PSK if any backup file has ever been stored insecurely or shared
- Long term, replace EOL hardware with a supported model where backup exports mask or encrypt credential fields

---

### 5.2 Finding 2: Hardcoded FTP Service Credentials (SEC Consult SA-20190829-0)

**Severity:** High

**Description:**
An FTP daemon with hardcoded, vendor embedded credentials runs on the affected Zyxel NWA, NAP, and WAC wireless access point series, including NWA1123-ACv2 firmware 5.50 patch 0 and earlier. This device's reviewed configuration runs firmware 5.00(ABEL.3), which falls within the affected range, and the reviewed configuration additionally shows the FTP service explicitly enabled (`ip ftp server cert default`, `ip ftp server`). These hardcoded credentials allow an unauthenticated party on the local network segment to log in to the AP's FTP server and retrieve the configuration file, which, per Finding 1, contains the WPA-PSK in cleartext.

**Evidence:**
- Vendor advisory: Zyxel security advisory for hardcoded FTP credential vulnerability of access points
- Third party advisory: SEC Consult Vulnerability Lab, SA-20190829-0, "Hardcoded FTP Credentials in Zyxel NWA/NAP/WAC wireless access point series," disclosed 2019-08-29, no CVE number was assigned by the vendor for this issue
- Affected version range per SEC Consult: Zyxel NWA1123-ACv2 5.50 patch 0 and earlier
- This device's confirmed version: 5.00(ABEL.3), within the affected range
- Local configuration confirms FTP service is active: `ip ftp server cert default` / `ip ftp server`

**Impact:**
An unauthenticated attacker with access to the local network segment (including, per the vendor's own advisory language, an attacker who has joined a different VLAN bridged to the AP) can authenticate to the FTP service using the hardcoded credentials and retrieve the device's configuration file, exposing the WPA-PSK and any other stored secrets in cleartext (see Finding 1). This effectively chains the two findings into a remote, unauthenticated, credential disclosure path that requires no cracking and no management interface access at all.

**Recommendation:**
- Immediate, disable the FTP server on the device (remove `ip ftp server` from the running configuration) unless it is actively required, and if required, restrict access via VLAN segmentation and firewall rules so it is unreachable from client facing wireless segments
- Confirm whether a firmware update exists that removes the hardcoded credential (per vendor advisory, fixed in updated firmware released around 2019-08-29 for supported models); this specific EOL sub model may not have received a fix depending on exact firmware branch, verify against Zyxel's download page for this model
- Rotate the WPA-PSK regardless, since exposure cannot be ruled out for any device that has had FTP enabled on this firmware range

---

### 5.3 Finding 3: Weak, Unrotated WDS Pre-Shared Key

**Severity:** Medium

**Description:**
The default WDS (Wireless Distribution System) profile configures a pre-shared key of `87654321`, an eight character, purely numeric, sequential/patterned value. This applies to the `Zyxel_WDS` SSID used for AP to AP bridging.

**Evidence:**
```
wlan-wds-profile default
 ssid Zyxel_WDS
 psk <REDACTED, 8 numeric characters, sequential pattern>
```

**Impact:**
A short, purely numeric, sequential pre-shared key is trivially brute forceable and is consistent with either a vendor default or a placeholder value that was never rotated after initial setup. If WDS bridging is active, this weak key protects the inter-AP wireless bridge link, compromise of which could allow traffic interception or injection between access points.

**Recommendation:**
- If WDS is not actively in use, disable the profile entirely rather than leaving an active, weakly protected SSID
- If WDS is required, replace the key with a long, high entropy passphrase consistent with the primary WPA-PSK, and rotate on the same schedule

---

### 5.4 Finding 4: SNMP v2c Enabled, Unauthenticated and Unencrypted

**Severity:** Medium

**Description:**
The device has SNMP enabled using protocol version 2c, which relies on plaintext, unauthenticated community strings for read and/or write access, rather than SNMPv3, which supports proper authentication and encryption.

**Evidence:**
```
snmp-server
snmp-server version v2c
```

**Impact:**
SNMP v2c community strings are transmitted in cleartext and, if default or weak community strings are in use, can allow an attacker on the local segment to read (and, depending on configuration, write) device management information without authentication, including potentially sensitive operational data about the AP and connected clients.

**Recommendation:**
- Migrate to SNMPv3 if the management platform in use supports it, to gain authentication and encryption
- If SNMPv2c must be retained, ensure community strings are long, random, and not left at vendor defaults, and restrict SNMP access via ACL or VLAN to management segments only

---

## 6. Risk Summary

| Finding | Severity | Exploitability | Status |
|---|---|---|---|
| Cleartext PSK in backup | High | Requires access to backup file | Unpatched (EOL) |
| Hardcoded FTP credentials (SA-20190829-0) | High | Unauthenticated, local network segment access sufficient | Fix availability for this exact EOL sub model unconfirmed, verify |
| Weak WDS pre-shared key | Medium | Requires proximity to WDS bridge link | Configuration issue, self remediable |
| SNMP v2c, unauthenticated | Medium | Requires local network segment access | Configuration issue, self remediable |

---

## 7. Recommendations

**For current owners of this hardware:**
1. Treat configuration backups as credential material, encrypt at rest, restrict access, never store in plaintext on shared or cloud storage without encryption
2. Rotate the WPA-PSK immediately, given both the direct cleartext storage finding and the separately disclosed FTP credential exposure path
3. Disable the FTP server unless actively required, and segment it away from client wireless traffic if it must remain enabled
4. Replace the default WDS pre-shared key and migrate SNMP to v3 where supported
5. Where possible, migrate to actively supported hardware, particularly for any deployment handling sensitive traffic
6. If continued use is unavoidable, isolate the device on its own VLAN/segment and disable remote management services not actively in use

**For the broader community:**
This pattern, credentials stored in cleartext within convenience export/backup features, compounded by a separately disclosed hardcoded service credential vulnerability on the same product line, is common across consumer and SMB network hardware. When evaluating or auditing similar EOL devices, checking backup/export file contents alongside known vendor and third party advisories for that exact firmware version is a fast, high value first step.

---

## 8. Disclosure Timeline

| Date | Event |
|---|---|
| `<date>` | Finding identified during personal research |
| `<date>` | Confirmed device is EOL with no active vendor security contact channel for new findings |
| `<date>` | Confirmed Finding 2 corresponds to a pre-existing, already publicly disclosed advisory (SEC Consult SA-20190829-0), not a novel issue |
| `<date>` | Report finalized and published to public GitHub repository for community awareness |

Because Zyxel's EOL policy for this product line means no security patches will be issued and no formal vulnerability disclosure channel is maintained for this model, this report is published directly rather than held under a private disclosure embargo, with the exception of Finding 2, which is already public vendor and third party disclosed information being cited, not new information being disclosed here for the first time. This is consistent with common industry practice for EOL hardware research (see for example how researchers at Tenable and Rapid7 handle EOL device findings, publish with clear EOL context rather than withhold indefinitely).

---

## 9. Scope & Ethics Statement

This assessment was performed exclusively against hardware owned by the assessor, on an isolated test network with no third party systems, users, or traffic involved. No credentials, configuration data, or personally identifiable information from the assessor's live network are included in this public report; all sensitive values have been redacted or replaced with representative placeholders.

---

## 10. References

- NVD, National Vulnerability Database: https://nvd.nist.gov/
- Zyxel Product End of Life page: https://www.zyxel.com/global/en/support/end-of-life
- Zyxel security advisory for hardcoded FTP credential vulnerability of access points: https://www.zyxel.com/global/en/support/security-advisories/zyxel-security-advisory-for-hardcoded-ftp-credential-vulnerability-of-access-points
- SEC Consult Vulnerability Lab, SA-20190829-0, Hardcoded FTP Credentials in Zyxel NWA/NAP/WAC wireless access point series: https://sec-consult.com/vulnerability-lab/advisory/hardcoded-ftp-credentials-in-zyxel-wireless-access-point-series/
- PTES (Penetration Testing Execution Standard): http://www.pentest-standard.org/
- OWASP Firmware Security Testing Methodology: https://owasp.org/www-project-iot-security-testing-guide/

---

## Appendix A: Redacted Configuration Excerpt

```
! model: NWA1123-ACv2
! firmware version: 5.00(ABEL.3)
!
hybrid-mode standalone
!
wlan-security-profile QI-Prof
 mode wpa2
 eap external
 idle 300
 wpa-psk <REDACTED>
 wpa-encrypt auto
 group-key 30000
!
wlan-wds-profile default
 ssid Zyxel_WDS
 psk <REDACTED>
!
snmp-server
snmp-server version v2c
!
ip http server
ip http secure-server cert default
ip http secure-server
ip http secure-server force-redirect
ip ssh server cert default
ip ssh server
ip ftp server cert default
ip ftp server
```
> Full configuration files are not committed to the public repository, only the sanitized excerpt above, since even with the PSK redacted they contain the live SSID name, admin account hash, and network topology details.

## Appendix B: Tools & Scripts

See `/scripts` in this repository for any analysis tooling used during this assessment.
