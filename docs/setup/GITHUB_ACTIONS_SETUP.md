# GitHub Actions Setup Guide

## Quick Start

GitHub Actions workflows are now configured! They will automatically:

1. **Test Python application** when you push changes to `nexus.py`
2. **Run CI checks** on every push/PR

## Workflows Created

### 1. `build-python.yml` - Python Testing
**When:** Push/PR to `nexus.py` or `requirements.txt`

Tests Python application:
- Syntax checking
- Import testing
- Multiple Python versions (3.9, 3.10, 3.11)
- Multiple platforms (macOS, Ubuntu)
- PyInstaller executable build (macOS)

### 2. `ci.yml` - Quick CI Checks
**When:** Every push/PR

Fast CI checks:
- Python syntax
- Import verification
- ~2 minutes total

## How to Use

### Automatic Builds

Just push your code:
```bash
git add .
git commit -m "Your changes"
git push origin main
```

Workflows run automatically based on changed files.

## Viewing Results

### Check Workflow Status

1. Go to GitHub → Actions tab
2. See all workflow runs
3. Green checkmark = success
4. Red X = failure (click to see logs)

### Download Artifacts

1. Click on a successful workflow run
2. Scroll to "Artifacts" section
3. Click artifact name to download
4. Extract and run executable

### View Logs

1. Click on workflow run
2. Click on job (e.g., "Test Python Application")
3. Click on step to see logs
4. Expand sections to see details

## Customization

### Add More Platforms

Edit `.github/workflows/build-python.yml`:

```yaml
strategy:
  matrix:
    os: [macos-latest, ubuntu-latest, windows-latest]
    python-version: ['3.9', '3.10', '3.11']
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
git add requirements.txt
git commit -m "Update dependencies"
git push
```

### PyInstaller Build Fails

**Common issues:**
- Missing hidden imports
- Missing data files
- Platform-specific issues

**Fix:** Update PyInstaller command in workflow:
```yaml
- name: Build executable with PyInstaller
  run: |
    pyinstaller --onefile --name nexus \
      --add-data "models:models" \
      --add-data "assets:assets" \
      --hidden-import cv2 \
      --hidden-import mediapipe \
      --hidden-import numpy \
      nexus.py
```

### Artifact Not Found

**Check:**
- Workflow completed successfully
- Artifact wasn't expired (retention: 7 days)
- Path is correct in workflow

**Fix:**
- Re-run workflow
- Increase retention days
- Check artifact path

## Workflow Files

All workflows are in `.github/workflows/`:

- `build-python.yml` - Python testing and builds
- `ci.yml` - Quick CI checks
- `README.md` - Detailed documentation

## Next Steps

1. **Push workflows to GitHub:**
   ```bash
   git add .github/
   git commit -m "Add GitHub Actions workflows"
   git push
   ```

2. **Check Actions tab** to see workflows running

3. **Download artifacts** from successful builds

4. **Customize** workflows for your needs

## Example: Complete Workflow

```bash
# 1. Make changes
vim nexus.py

# 2. Commit and push
git add nexus.py
git commit -m "Update Python code"
git push

# 3. Check GitHub Actions
# Go to GitHub → Actions → See workflow running

# 4. Wait for completion (~10 minutes)

# 5. Download artifact
# Click workflow run → Artifacts → Download nexus-python-macos

# 6. Test executable
chmod +x nexus
./nexus
```

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Python Setup Action](https://github.com/actions/setup-python)
- [PyInstaller Documentation](https://pyinstaller.org/)
