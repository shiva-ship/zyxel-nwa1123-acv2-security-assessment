# CVE Cross-Reference Checklist

Use this to systematically confirm which known CVEs apply to your specific firmware version. Fill in and move confirmed entries into the main report (§5.2).

## Steps

1. Confirm exact firmware version: `<Web GUI > Status, or Maintenance > Firmware Upgrade page>`
2. Search NVD (https://nvd.nist.gov/vuln/search) for:
   - `Zyxel NWA1123-ACv2`
   - `Zyxel NWA1123`
   - `Zyxel AP firmware` (broader, in case the flaw spans the product line)
3. For each candidate CVE:
   - [ ] Does the affected version range include your confirmed firmware version?
   - [ ] Is there a public PoC or advisory with technical detail (not just a CVE stub)?
   - [ ] Does Zyxel's own security advisory page mention this model?
4. Check Zyxel's official advisory index: `<insert URL once checked — security.zyxel.com or similar>`
5. Check Zyxel's EOL/EOS product list to confirm and cite the exact EOL date: `<insert URL>`

## Confirmed CVEs (fill in)

| CVE ID | Affected Versions | Applies to Tested Unit? | Summary |
|---|---|---|---|
| | | | |

## Notes

- If no CVEs are found for this exact model, note that explicitly in the report rather than omitting the section — "no publicly known CVEs at time of writing" is itself useful information.
- Cross-check whether this hardware shares a codebase/chipset with other Zyxel AP models that DO have known CVEs — shared firmware bases sometimes mean shared vulnerabilities even without a model-specific CVE entry.
