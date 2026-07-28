#!/usr/bin/env python3
"""
analyze_config_export.py

Scans a Zyxel NWA1123-ACv2 configuration backup export for sensitive fields
stored in cleartext (e.g. wpa-psk, admin passwords, RADIUS secrets).

Usage:
    python3 analyze_config_export.py <path_to_config_export>

This script only READS the provided file locally. It does not transmit,
upload, or exfiltrate any data. Run only against configuration exports
from hardware you own.
"""

import argparse
import re
import sys
from pathlib import Path

# Field patterns known/suspected to appear in Zyxel config exports.
# Extend this list as you confirm the actual export format on your unit.
SENSITIVE_PATTERNS = {
    "wpa_psk": re.compile(r"wpa-psk\s+(\S+)", re.IGNORECASE),
    "admin_password": re.compile(r"password\s+(\S+)", re.IGNORECASE),
    "radius_secret": re.compile(r"radius-secret\s+(\S+)", re.IGNORECASE),
}


def scan_file(path: Path) -> dict:
    findings = {}
    text = path.read_text(errors="ignore")

    for label, pattern in SENSITIVE_PATTERNS.items():
        matches = pattern.findall(text)
        if matches:
            findings[label] = len(matches)

    return findings


def redact_preview(path: Path, label: str, pattern: re.Pattern, context_chars: int = 20):
    """Print a redacted preview showing the field exists without revealing the value."""
    text = path.read_text(errors="ignore")
    for m in pattern.finditer(text):
        start = max(0, m.start() - context_chars)
        end = min(len(text), m.end() + context_chars)
        snippet = text[start:end]
        redacted = pattern.sub(lambda mm: mm.group(0).split()[0] + " [REDACTED]", snippet)
        print(f"  ...{redacted}...")


def main():
    parser = argparse.ArgumentParser(description="Scan a config export for cleartext sensitive fields.")
    parser.add_argument("config_path", type=Path, help="Path to the exported config file")
    args = parser.parse_args()

    if not args.config_path.exists():
        print(f"File not found: {args.config_path}", file=sys.stderr)
        sys.exit(1)

    findings = scan_file(args.config_path)

    if not findings:
        print("No known sensitive field patterns matched. "
              "Consider extending SENSITIVE_PATTERNS to match this export's actual format.")
        return

    print(f"Sensitive fields found in {args.config_path.name}:\n")
    for label, count in findings.items():
        print(f"[{label}] — {count} match(es) found in cleartext")
        redact_preview(args.config_path, label, SENSITIVE_PATTERNS[label])
        print()

    print("Note: presence of these fields in plaintext within a config export "
          "is itself the finding — see report/SECURITY_ASSESSMENT.md §5.1")


if __name__ == "__main__":
    main()
