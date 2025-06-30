# CI/CD Integration Guide

This guide shows how to integrate the Dagger Quality Gate pipeline into various CI/CD systems.

## GitHub Actions

### Basic Setup

Create `.github/workflows/quality-gate.yml`:

```yaml
name: Quality Gate

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  quality-gate:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install uv
      uses: astral-sh/setup-uv@v3
    
    - name: Install dependencies
      run: uv sync
    
    - name: Run Quality Gate
      run: uv run python main.py
```

### Advanced Configuration

```yaml
jobs:
  quality-gate:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install uv
      uses: astral-sh/setup-uv@v3
    
    - name: Cache uv dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/uv
        key: ${{ runner.os }}-uv-${{ hashFiles('uv.lock') }}
    
    - name: Install dependencies
      run: uv sync
    
    - name: Run Quality Gate
      run: uv run python main.py
      env:
        VERBOSE: 'true'
        FAIL_FAST: 'false'
```

### PR-Specific Checks

```yaml
quality-gate-pr:
  runs-on: ubuntu-latest
  if: github.event_name == 'pull_request'
  
  steps:
  - uses: actions/checkout@v4
  
  - name: Install uv
    uses: astral-sh/setup-uv@v3
  
  - name: Run Python Checks Only
    run: |
      uv sync
      uv run python main.py
    env:
      ENABLE_MARKDOWN: 'false'
      ENABLE_TERRAFORM: 'false'
      ENABLE_GITLEAKS: 'false'
```

## GitLab CI

### Basic Setup

Create `.gitlab-ci.yml`:

```yaml
stages:
  - quality

quality-gate:
  stage: quality
  image: python:3.11
  before_script:
    - curl -LsSf https://astral.sh/uv/install.sh | sh
    - export PATH="$HOME/.cargo/bin:$PATH"
    - uv sync
  script:
    - uv run python main.py
  only:
    - branches
```

### With Caching

```yaml
variables:
  UV_CACHE_DIR: "$CI_PROJECT_DIR/.cache/uv"

quality-gate:
  stage: quality
  image: python:3.11
  cache:
    key: "$CI_COMMIT_REF_SLUG"
    paths:
      - .cache/uv
      - .venv
  before_script:
    - curl -LsSf https://astral.sh/uv/install.sh | sh
    - export PATH="$HOME/.cargo/bin:$PATH"
    - uv sync
  script:
    - uv run python main.py
```

## Jenkins

### Declarative Pipeline

```groovy
pipeline {
    agent {
        docker {
            image 'python:3.11'
        }
    }
    
    stages {
        stage('Setup') {
            steps {
                sh '''
                    curl -LsSf https://astral.sh/uv/install.sh | sh
                    export PATH="$HOME/.cargo/bin:$PATH"
                    uv sync
                '''
            }
        }
        
        stage('Quality Gate') {
            steps {
                sh 'uv run python main.py'
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
    }
}
```

### With Environment Configuration

```groovy
pipeline {
    agent any
    
    environment {
        ENABLE_SAFETY = 'false'
        VERBOSE = 'true'
    }
    
    stages {
        stage('Quality Gate') {
            steps {
                sh '''
                    curl -LsSf https://astral.sh/uv/install.sh | sh
                    $HOME/.cargo/bin/uv sync
                    $HOME/.cargo/bin/uv run python main.py
                '''
            }
        }
    }
}
```

## CircleCI

Create `.circleci/config.yml`:

```yaml
version: 2.1

jobs:
  quality-gate:
    docker:
      - image: cimg/python:3.11
    steps:
      - checkout
      - run:
          name: Install uv
          command: |
            curl -LsSf https://astral.sh/uv/install.sh | sh
            echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> $BASH_ENV
      - restore_cache:
          keys:
            - v1-dependencies-{{ checksum "uv.lock" }}
      - run:
          name: Install dependencies
          command: uv sync
      - save_cache:
          paths:
            - ~/.cache/uv
          key: v1-dependencies-{{ checksum "uv.lock" }}
      - run:
          name: Run Quality Gate
          command: uv run python main.py

workflows:
  version: 2
  quality:
    jobs:
      - quality-gate
```

## Azure DevOps

Create `azure-pipelines.yml`:

```yaml
trigger:
- main
- develop

pool:
  vmImage: 'ubuntu-latest'

steps:
- task: UsePythonVersion@0
  inputs:
    versionSpec: '3.11'
  displayName: 'Use Python 3.11'

- script: |
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
    uv sync
  displayName: 'Install dependencies'

- script: |
    source $HOME/.cargo/env
    uv run python main.py
  displayName: 'Run Quality Gate'
  env:
    VERBOSE: true
```

## Best Practices

### 1. Fail Fast in CI

```yaml
env:
  FAIL_FAST: 'true'  # Stop on first failure
```

### 2. Different Checks for PRs vs Main

```yaml
# For PRs - faster feedback
env:
  ENABLE_SAFETY: 'false'  # Skip dependency scanning
  PARALLEL: 'true'        # Run in parallel

# For main branch - comprehensive
env:
  VERBOSE: 'true'         # Detailed output
  FAIL_FAST: 'false'      # Run all checks
```

### 3. Cache Dependencies

Always cache uv dependencies for faster builds:
- GitHub Actions: Use `actions/cache@v3`
- GitLab: Use cache with `UV_CACHE_DIR`
- CircleCI: Use `restore_cache` and `save_cache`

### 4. Matrix Testing

Test against multiple Python versions:

```yaml
strategy:
  matrix:
    python-version: ['3.10', '3.11', '3.12']
```

### 5. Conditional Checks

Run different checks based on file changes:

```yaml
- name: Check Python files changed
  id: python-changes
  run: |
    if git diff --name-only origin/main..HEAD | grep -q '\.py$'; then
      echo "python_changed=true" >> $GITHUB_OUTPUT
    fi

- name: Run Python checks
  if: steps.python-changes.outputs.python_changed == 'true'
  run: uv run python main.py
  env:
    ENABLE_MARKDOWN: 'false'
    ENABLE_TERRAFORM: 'false'
```

## Troubleshooting CI Issues

See the [Troubleshooting Guide](troubleshooting.md) for common CI-specific issues and solutions.