# 📄 PRD: Universal Dagger Quality Gate Pipeline

## 1️⃣ Purpose

Build a reusable Dagger pipeline **written in Python** that:

* Runs standard quality checks across any repo.
* Easy to enable/disable checks per project.
* Runs identically locally and in CI.
* Simple to extend with new linters/scanners.

## 2️⃣ Supported Checks (MVP)

**Included in v1:**

* Markdown Lint → `markdownlint` (Node)
* Python Lint → `ruff`
* Python Type Check → `mypy` + [Ty](https://github.com/astral-sh/ty)
* Python Security scanning → Bandit, semgrep, safety
* Terraform Lint → `terraform fmt -check` and `tflint`
* Secrets Scan → `gitleaks`

**Optional Later:**

* YAML Lint (`yamllint`)
* Dockerfile Lint (`hadolint`)
* Shell Lint (`shellcheck`)
* Unit Tests integration

## 3️⃣ Execution Flow

* Mount repo source.
* For each enabled check:

  * Spin up container with tool.
  * Run tool.
  * Return exit code & logs.
* If any check fails → pipeline fails.

## 4️⃣ Usability Requirements

* **Python Dagger SDK only.**
* Checks configurable via flags/env vars.
* Run all checks by default.
* Clear logs & status output.
* Example CLI & GitHub Actions CI usage.

## 5️⃣ Reusability & Versioning

* Packaged as standalone Git repo `basher83/dagger-quality-gate`
* Version controlled & tagged.
* Usable via submodule or template.
* Clear README & usage instructions.

## 6️⃣ Deliverables

* Dagger pipeline script (`main.py`).
* Example `dagger.yaml` or CLI usage.
* Example GitHub Actions workflow.
* Docs: toggling checks & extending pipeline.
* Test repo for validation.

## 7️⃣ Stretch Goals

* Output SARIF/JSON reports.
* Slack/Discord notifications.
* Cache dependencies for speed.
* Parametric config file (`pipeline.toml`).

## 8️⃣ Timeline

* Draft pipeline: Day 1–2
* Local tests: Day 2–3
* CI example: Day 3–4
* Docs & polish: Day 5

## Risks

* Tool configs vary per repo.
* Large repos may scan slowly.
* Secrets scanning can false positive; use `.gitleaksignore`.
