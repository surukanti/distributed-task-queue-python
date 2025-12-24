# GitHub Actions Setup Guide

This project includes comprehensive CI/CD workflows to automate testing, building, and deployment.

## 📋 Workflows Included

### 1. **CI - Tests & Linting** (`ci.yml`)
Runs on every push and pull request to `main` and `develop` branches.

**What it does:**
- ✅ Runs Python tests against Redis service
- ✅ Code linting with flake8
- ✅ Code formatting check with black
- ✅ Import sorting with isort
- ✅ Security scanning with bandit
- ✅ Dependency scanning with safety
- ✅ Coverage reports uploaded to Codecov

**Triggers:** Push to main/develop, Pull requests

### 2. **Docker Build & Push** (`docker.yml`)
Builds and pushes Docker images to Docker Hub and GitHub Container Registry.

**What it does:**
- 🐳 Builds Docker images for gateway, worker, and dashboard
- 📤 Pushes to Docker Hub and GitHub Container Registry
- 🔍 Scans images for vulnerabilities with Trivy
- 📦 Semantic versioning from git tags

**Triggers:** Push to main, tags matching `v*`

**Requires Secrets:**
- `DOCKER_USERNAME` - Docker Hub username
- `DOCKER_PASSWORD` - Docker Hub access token

### 3. **Code Quality & Analysis** (`quality.yml`)
Analyzes code quality, complexity, and dependencies.

**What it does:**
- 📊 Code complexity analysis with Radon
- 🔍 Type checking with mypy
- 🎯 Detailed linting with pylint
- 📝 Docstring coverage check
- 🛡️ Dependency vulnerability checks
- 💎 SonarCloud analysis

**Triggers:** Push to main/develop, Pull requests

**Requires Secrets:**
- `SONAR_TOKEN` - SonarCloud API token

### 4. **Deploy Documentation** (`docs.yml`)
Builds and deploys documentation to GitHub Pages.

**What it does:**
- 📚 Builds documentation with MkDocs
- 🎨 Uses Material theme
- 🌐 Deploys to GitHub Pages
- 📄 Converts markdown files to docs

**Triggers:** Push to main

### 5. **Release & Publish** (`release.yml`)
Creates releases and publishes to PyPI.

**What it does:**
- 🏷️ Creates GitHub Release with changelog
- 📦 Publishes Python package to PyPI
- 📝 Auto-generates release notes

**Triggers:** Git tags matching `v*`

**Requires Secrets:**
- `PYPI_API_TOKEN` - PyPI authentication token

## 🔧 Setup Instructions

### Step 1: Add Secrets to GitHub

Go to your GitHub repository → Settings → Secrets and variables → Actions

Add these secrets:

```bash
# For Docker image publishing (optional but recommended)
DOCKER_USERNAME=your_dockerhub_username
DOCKER_PASSWORD=your_dockerhub_access_token

# For PyPI publishing (optional)
PYPI_API_TOKEN=your_pypi_token

# For SonarCloud analysis (optional)
SONAR_TOKEN=your_sonarcloud_token
```

#### How to get each token:

**Docker Hub Access Token:**
1. Go to https://hub.docker.com/settings/security
2. Click "New Access Token"
3. Copy and save as `DOCKER_PASSWORD`

**PyPI Token:**
1. Go to https://pypi.org/account/
2. Create API token in Account Settings
3. Use token as `PYPI_API_TOKEN`

**SonarCloud Token:**
1. Go to https://sonarcloud.io/account/security
2. Generate token
3. Use as `SONAR_TOKEN`

### Step 2: Update Workflow Files (if needed)

Edit `.github/workflows/*.yml` files to match your needs:

```yaml
# Example: Change branches in ci.yml
on:
  push:
    branches: [ main, staging ]  # Add your branches
  pull_request:
    branches: [ main, staging ]
```

### Step 3: Enable GitHub Pages (for documentation)

1. Go to Settings → Pages
2. Select "Deploy from a branch"
3. Select `gh-pages` branch and `/ (root)` folder
4. Click Save

### Step 4: Install Pre-commit Hooks (Local)

For local development, install pre-commit hooks:

```bash
pip install pre-commit
pre-commit install

# Test it
pre-commit run --all-files
```

This will automatically run checks before committing code locally.

## 🚀 Usage Examples

### Trigger CI Pipeline
```bash
# Any push to main will trigger CI
git push origin main

# Or create a pull request
```

### Create a Release (Triggers Release Workflow)
```bash
# Create a git tag
git tag -a v1.0.0 -m "Release version 1.0.0"

# Push tag to trigger release workflow
git push origin v1.0.0

# This will:
# 1. Create GitHub Release
# 2. Build Docker images
# 3. Publish to PyPI
```

### View Workflow Results

1. Go to your GitHub repo
2. Click "Actions" tab
3. See all workflow runs
4. Click on a run to see detailed logs

### Check Code Coverage

After CI completes:
1. Go to [codecov.io](https://codecov.io)
2. Sign in with GitHub
3. Select your repository
4. View coverage reports and trends

## 📊 Status Badges

Add these badges to your README.md:

```markdown
![CI - Tests & Linting](https://github.com/surukanti/distributed-task-queue-python/workflows/CI%20-%20Tests%20%26%20Linting/badge.svg)
![Docker Build & Push](https://github.com/surukanti/distributed-task-queue-python/workflows/Docker%20Build%20%26%20Push/badge.svg)
![Code Quality & Analysis](https://github.com/surukanti/distributed-task-queue-python/workflows/Code%20Quality%20%26%20Analysis/badge.svg)
[![codecov](https://codecov.io/gh/surukanti/distributed-task-queue-python/branch/main/graph/badge.svg)](https://codecov.io/gh/surukanti/distributed-task-queue-python)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=distributed-task-queue-python&metric=alert_status)](https://sonarcloud.io/dashboard?id=distributed-task-queue-python)
```

## 🔍 Monitoring Workflows

### Check if workflows are running
```bash
# Via GitHub CLI
gh workflow list

# View specific workflow runs
gh run list --workflow=ci.yml
```

### Debug a failed workflow
1. Click on the failed workflow run
2. Click on the failed job
3. View detailed logs
4. Look for error messages

### Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Docker push fails | Check DOCKER_USERNAME and DOCKER_PASSWORD secrets |
| PyPI publish fails | Verify PYPI_API_TOKEN is correct |
| Tests fail in CI but pass locally | Check Python version mismatch (uses 3.11) |
| SonarCloud not reporting | Add SONAR_TOKEN secret |

## 📝 Customization Tips

### Add more tests
```bash
# Run tests locally
pip install pytest pytest-cov
pytest tests/ --cov=src/
```

### Run linting locally
```bash
black src/ tests/
isort src/ tests/
flake8 src/ tests/
```

### Build Docker images locally
```bash
docker build -f Dockerfile.gateway -t task-queue-gateway:latest .
docker build -f Dockerfile.worker -t task-queue-worker:latest .
docker build -f Dockerfile.dashboard -t task-queue-dashboard:latest .
```

## 🎯 Next Steps

1. ✅ Add repository secrets (DOCKER_USERNAME, DOCKER_PASSWORD, etc.)
2. ✅ Create initial commit with workflows
3. ✅ Monitor first CI run
4. ✅ Set up SonarCloud and Codecov (optional but recommended)
5. ✅ Create first release tag (`v1.0.0`)
6. ✅ Monitor Docker image builds
7. ✅ Enable GitHub Pages for documentation

## 📚 Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker GitHub Action](https://github.com/docker/build-push-action)
- [SonarCloud](https://sonarcloud.io)
- [Codecov](https://codecov.io)
- [PyPI Publishing](https://packaging.python.org/tutorials/packaging-projects/)

---

**Questions?** Check the workflow files in `.github/workflows/` for detailed comments.
