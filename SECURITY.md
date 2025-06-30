# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

We take the security of the Dagger Quality Gate pipeline seriously. If you discover a security vulnerability, please follow these steps:

1. **DO NOT** create a public GitHub issue for the vulnerability
2. Send details to: [Create a security advisory](https://github.com/basher83/dagger-quality-gate/security/advisories/new)
3. Include as much information as possible:
   - Type of vulnerability
   - Full paths of source file(s) related to the issue
   - Location of the affected source code (tag/branch/commit or direct URL)
   - Steps to reproduce the issue
   - Proof-of-concept or exploit code (if possible)
   - Impact of the issue

## Response Timeline

- We will acknowledge receipt of your vulnerability report within 48 hours
- We will provide a detailed response within 7 days
- We will work on a fix based on severity:
  - **Critical** (CVSS 9.0-10.0): Fix within 7 days
  - **High** (CVSS 7.0-8.9): Fix within 30 days
  - **Medium** (CVSS 4.0-6.9): Fix within 60 days
  - **Low** (CVSS 0.1-3.9): Fix within 90 days
- Maximum disclosure timeline: 90 days from initial report

## Security Best Practices

When using this pipeline:

1. **Container Images**: Pin images by **digest (`sha256:...`)** or immutable tags to prevent supply-chain attacks. This project uses Renovate to automatically pin and update container digests.
2. **Environment Variables**: Never commit sensitive values; use secrets management
3. **Dependencies**: Regularly update the pipeline to get the latest security fixes
4. **Permissions**: Run with minimal required permissions
5. **TLS Verification**: Ensure all outbound requests keep TLS verification enabled (never `verify=False`)

## Known Security Considerations

### Example Repository

The `examples/sample-repo/` directory intentionally contains:

- Vulnerable dependencies (for testing Safety scanner)
- Security anti-patterns (for testing Bandit/Semgrep)
- Exposed secrets (for testing Gitleaks)

**These are for testing purposes only and should never be used in production.**

### Tool-Specific Security

Each security tool has its own configuration options:

- **Bandit**: Configure via `.bandit` file
- **Semgrep**: Uses `--config=auto` by default; customize with `.semgrep.yml`
- **Safety**: Checks against known CVE database
- **Gitleaks**: Configure via `.gitleaks.toml`

## Security Features

This pipeline includes multiple security scanning tools:

- **[Bandit](https://bandit.readthedocs.io)** – Python security linter
- **[Semgrep](https://semgrep.dev)** – Language-agnostic SAST
- **[Safety](https://pyup.io/safety/)** – Dependency vulnerability scanner
- **[Gitleaks](https://gitleaks.io)** – Secret detection

## Disclosure Policy

- Security fixes will be released as patch versions
- Critical vulnerabilities will trigger immediate releases
- We will credit reporters (unless they prefer to remain anonymous)
