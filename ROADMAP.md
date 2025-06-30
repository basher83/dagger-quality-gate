# Dagger Quality Gate Roadmap

This document tracks the implementation status of quality check pipelines and outlines future development plans.

## 📊 Pipeline Implementation Status

### ✅ Implemented Pipelines (11)

#### Python Quality Checks

- [x] **Ruff** - Fast Python linter with 700+ built-in rules
  - Status: Fully operational
  - Installation: `uv tool install ruff`
  - Config: `.ruff.toml` support
  
- [x] **Black** - Uncompromising Python code formatter
  - Status: Fully operational
  - Installation: `uv pip install --system black`
  - Config: `pyproject.toml` support
  
- [x] **Mypy** - Static type checker for Python
  - Status: Fully operational
  - Installation: `uv pip install --system mypy`
  - Config: `mypy.ini` or `pyproject.toml` support
  
- [x] **Ty** - Experimental Python type checker by Astral
  - Status: Fully operational
  - Installation: `uv tool install ty`
  - Command: `ty check .`
  - Note: Early-stage tool, expect changes

#### Security Scanners

- [x] **Bandit** - Python security linter
  - Status: Fully operational
  - Installation: `uv pip install --system bandit`
  - Config: `.bandit` file support
  
- [x] **Semgrep** - Static analysis for multiple languages
  - Status: Fully operational
  - Container: `semgrep/semgrep:latest`
  - Config: Uses `--config=auto` by default
  
- [x] **Safety** - Python dependency vulnerability scanner
  - Status: Fully operational
  - Installation: `uv pip install --system safety`
  - Database: PyUp.io vulnerability database

#### Infrastructure as Code

- [x] **Terraform Format** - Code formatting check
  - Status: Fully operational
  - Container: `hashicorp/terraform:latest`
  - Command: `terraform fmt -check -recursive`
  
- [x] **TFLint** - Terraform linter
  - Status: Fully operational
  - Container: `ghcr.io/terraform-linters/tflint:latest`
  - Config: `.tflint.hcl` support

#### Documentation & Secrets

- [x] **Markdownlint** - Markdown linter
  - Status: Fully operational
  - Container: `davidanson/markdownlint-cli2:latest`
  - Config: `.markdownlint.yaml` support
  
- [x] **Gitleaks** - Detect secrets in git repos
  - Status: Fully operational
  - Container: `zricethezav/gitleaks:latest`
  - Config: `.gitleaks.toml` support

### 🚧 Planned Pipelines (Phase 1)

#### Shell Scripts

- [ ] **ShellCheck** - Shell script static analysis
  - Priority: High
  - Container: `koalaman/shellcheck:stable`
  - Target: Q1 2025
  
#### YAML

- [ ] **yamllint** - YAML linter
  - Priority: High
  - Container: `python:3.11-slim` with yamllint
  - Target: Q1 2025

#### Containers

- [ ] **Hadolint** - Dockerfile linter
  - Priority: Medium
  - Container: `hadolint/hadolint:latest`
  - Target: Q1 2025

### 🔮 Future Pipelines (Phase 2)

#### JavaScript/TypeScript

- [ ] **ESLint** - JavaScript/TypeScript linter
  - Container: `node:18-alpine`
  - Config: `.eslintrc.js` support
  
- [ ] **Prettier** - Code formatter
  - Container: `node:18-alpine`
  - Config: `.prettierrc` support

#### Go

- [ ] **golangci-lint** - Go linters aggregator
  - Container: `golangci/golangci-lint:latest`
  - Config: `.golangci.yml` support

#### Rust

- [ ] **Clippy** - Rust linter
  - Container: `rust:latest`
  - Integrated with cargo

#### License & Legal

- [ ] **License Finder** - Dependency license analysis
  - Container: Custom build required
  - Database: SPDX license list

#### Supply Chain Security

- [ ] **Syft** - SBOM generation
  - Container: `anchore/syft:latest`
  - Output: SPDX, CycloneDX formats
  
- [ ] **Grype** - Vulnerability scanner
  - Container: `anchore/grype:latest`
  - Database: Multiple vulnerability sources

## 🎯 Development Priorities

### Phase 1 (Q1 2025)

1. Implement ShellCheck for shell script analysis
2. Add yamllint for YAML validation
3. Add Hadolint for Dockerfile best practices
4. Create `pipeline.toml` for declarative configuration
5. Add caching layer for faster subsequent runs

### Phase 2 (Q2 2025)

1. JavaScript/TypeScript ecosystem support
2. Go language support
3. Rust language support
4. License compliance checking
5. SBOM generation and vulnerability scanning

### Phase 3 (Q3 2025)

1. Custom policy engine integration
2. IDE plugin development
3. Web dashboard for results visualization
4. Metrics and trending analysis
5. Integration with external tools (Jira, Slack, etc.)

## 🔧 Infrastructure Improvements

### Near Term

- [ ] Implement container image caching
- [ ] Add progress indicators for long-running checks
- [ ] Support for custom base images
- [ ] Parallel execution optimization

### Long Term

- [ ] Distributed execution support
- [ ] Cloud-native deployment options
- [ ] REST API for remote execution
- [ ] Plugin architecture for custom checks

## 📈 Success Metrics

- **Coverage**: Number of languages/frameworks supported
- **Performance**: Average pipeline execution time
- **Adoption**: Number of projects using the pipeline
- **Quality**: False positive/negative rates
- **Community**: Contributors and plugin ecosystem

## 🤝 Contributing

To add a new pipeline:

1. Review the implementation guide in `docs/development.md`
2. Create a new module in `checks/` directory
3. Update `config.py` and `main.py`
4. Add tests and documentation
5. Submit PR with examples

## 📅 Release Schedule

- **v0.2.0** (Target: Q1 2025) - Shell, YAML, Dockerfile support
- **v0.3.0** (Target: Q2 2025) - Multi-language expansion
- **v0.4.0** (Target: Q3 2025) - Enterprise features
- **v1.0.0** (Target: Q4 2025) - Production-ready with full ecosystem

## 🔗 Related Documents

- [README.md](README.md) - Project overview and quick start
- [docs/development.md](docs/development.md) - Development guide
- [SECURITY.md](SECURITY.md) - Security policy
- [CLAUDE.md](CLAUDE.md) - AI assistant context
