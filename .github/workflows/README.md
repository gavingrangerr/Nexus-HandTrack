# GitHub Actions Workflows

This directory contains GitHub Actions workflows for building and testing the Nexus Python application.

## Available Workflows

### 1. `build-python.yml` - Python Build and Test
**Triggers:** Push/PR to `nexus.py` or `requirements.txt`

Tests Python application on multiple platforms and Python versions.

**Features:**
- Syntax checking
- Import testing
- Cross-platform testing (macOS, Ubuntu)
- Multiple Python versions (3.9, 3.10, 3.11)
- PyInstaller executable build (macOS)

**Usage:**
```bash
git push origin main
# Workflow runs automatically when nexus.py changes
```

### 2. `ci.yml` - Continuous Integration
**Triggers:** All pushes and PRs

Quick CI checks:
- Python syntax and imports
- ~2 minutes total

**Use for:** Fast feedback on code changes

## Workflow Selection Guide

| Goal | Workflow | Time |
|------|----------|------|
| Quick CI checks | `ci.yml` | ~2 min |
| Python testing | `build-python.yml` | ~10 min |

## Artifacts

Workflows upload build artifacts:
- **Download:** Go to Actions → Select workflow run → Artifacts
- **Retention:** 7 days
- **Location:** `dist/nexus` (PyInstaller executable)

## Troubleshooting

### Workflow Not Running

**Check:**
- File paths match workflow triggers
- Branch name matches (`main` or `master`)
- Workflow file is in `.github/workflows/`

**Fix:**
```bash
# Ensure workflow files are committed
git add .github/workflows/
git commit -m "Add GitHub Actions workflows"
git push
```

### Build Fails: Missing Dependencies

**Check logs** for missing packages, then update `requirements.txt`:

```bash
pip install opencv-python mediapipe numpy
pip freeze > requirements.txt
```

### Artifact Not Found

**Check:**
- Workflow completed successfully
- Artifacts expire after retention period (7 days)
- Re-run workflow to regenerate

## Local Testing

Test workflows locally using [act](https://github.com/nektos/act):

```bash
# Install act
brew install act

# Test Python workflow
act -W .github/workflows/build-python.yml

# Test with specific event
act push -W .github/workflows/build-python.yml
```

## Customization

### Add More Platforms

Edit workflow files to add:
- Windows builds
- Different Linux distributions
- Different macOS versions

### Add More Python Versions

Edit `build-python.yml`:

```yaml
strategy:
  matrix:
    python-version: ['3.9', '3.10', '3.11', '3.12']
```

### Add Tests

Add test steps after build:

```yaml
- name: Run tests
  run: |
    python -m pytest tests/ || echo "No tests configured"
```

### Cache Dependencies

Speed up builds by caching:

```yaml
- name: Cache pip packages
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
```

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Python Setup Action](https://github.com/actions/setup-python)
- [PyInstaller Documentation](https://pyinstaller.org/)
