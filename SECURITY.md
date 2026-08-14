# Security Policy

## Supported Versions

We release security patches and stability fixes for active branches of SpectraAI:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

---

## Reporting a Vulnerability

We take the security and integrity of SpectraAI seriously. If you discover a potential vulnerability, please report it privately following these steps:

1. **Do NOT open a public GitHub issue.**
2. Report the vulnerability directly via **[GitHub Private Security Advisories](https://github.com/dheeraj0677/SpectraAI/security/advisories/new)** (recommended) or email the maintainer directly at **dheerajofficial06@gmail.com** with the subject line `[SECURITY] SpectraAI Vulnerability Report`.
3. Provide as much detail as possible to help us reproduce and resolve the issue quickly:
   - Type of vulnerability (e.g. Remote Code Execution, Path Traversal, Insecure Deserialization, Secret Exposure).
   - Step-by-step instructions or proof-of-concept script.
   - Any affected endpoints, payloads, or configurations.
   - Recommended remediation steps if known.

---

## Response & Disclosure Timeline

- **Initial Acknowledgement:** Within 48 hours of receipt.
- **Triage & Reproduction:** Within 5 business days.
- **Fix & Patch Release:** Coordinated security patch released prior to public disclosure.
- **Credit:** We are glad to credit security researchers in our release notes upon request.

---

## Secret Handling & Contribution Safety Rules

To protect users and maintainers, all contributors must strictly adhere to the following rules:

1. **Zero Secret Commits:** Never commit `.env` files, API keys, tokens, production credentials, or private certificates. Use `.env.example` for variable documentation with placeholder values only.
2. **Deterministic Test Fixtures:** Do not commit proprietary, confidential, or sensitive customer documents. Use synthetic fixtures from `test_data/`.
3. **No Dynamic Code Execution:** User uploads must never be executed dynamically or passed unsanitized into shell or evaluation commands.
4. **Path Traversal Guard:** All uploaded filenames are stripped of parent directory navigation (`Path(filename).name`) and prefixed with SHA-256 content hashes.
