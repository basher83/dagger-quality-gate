# Security and Dependency Management

## Security Policy (SECURITY.md)

The project has a comprehensive security policy that includes:

- Vulnerability reporting process via GitHub Security Advisories
- Response timelines based on severity (CVSS scores)
- Fix timelines: Critical (7 days), High (30 days), Medium (60 days), Low (90 days)
- Security best practices for users

## Container Security

- **Digest Pinning**: All container images automatically pinned to SHA256 digests by Renovate
- **Vulnerability Scanning**: Recommend scanning images with Trivy or Grype in CI/CD
- **Layer Optimization**: Container layers optimized to reduce attack surface
- **TLS Verification**: Must always be enabled (never `verify=False`)

## Dependency Management

### Renovate Configuration

The project uses Renovate for automated dependency updates with:

- **Container Digest Pinning**: All Docker images automatically pinned to SHA256 digests
- **GitHub Actions Pinning**: Actions pinned to commit SHAs for security
- **Python Dependency Grouping**: Updates grouped to reduce PR noise
- **Vulnerability Alerts**: Security issues labeled and assigned
- **Example Repository Exclusion**: `examples/sample-repo/` ignored (intentional vulnerabilities)
- **Automerge**: Patch updates for development tools (ruff, mypy, pytest, black)

### Dependabot Configuration

Configured to:

- Monitor Python dependencies weekly
- Ignore the example repository
- Monitor GitHub Actions for updates

## Security Tools in Pipeline

- **Bandit**: Python security linter (checks for common security issues)
- **Semgrep**: Language-agnostic SAST (Static Application Security Testing)
- **Safety**: Dependency vulnerability scanner (checks against CVE database)
- **Gitleaks**: Secret detection (prevents credential exposure)

## Future Security Enhancements (per ROADMAP)

- **Grype**: Container vulnerability scanner (planned)
- **Syft**: SBOM generation for supply chain security (planned)

## GitHub Workflow

- CI workflow runs on `workflow_dispatch` (manual trigger)
- All Python security checks enabled by default
- Example workflow for Python-only checks on PRs
