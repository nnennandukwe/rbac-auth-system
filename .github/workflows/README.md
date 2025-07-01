# GitHub Actions Workflows for README Updates

This directory contains several GitHub Actions workflows designed to keep the README.md file up-to-date automatically.

## Available Workflows

### 1. Update README (`update-readme.yml`)
**Purpose**: Comprehensive README updates with multiple triggers and options.

**Triggers**:
- Manual dispatch with update type selection
- Push to main branch (when code changes)
- Pull requests that modify README
- Weekly schedule (Sundays at midnight)

**Features**:
- Generate API documentation from FastAPI routes
- Update dependencies table
- Add/update timestamps
- Generate table of contents
- Check test coverage
- Create pull requests for review

**Usage**:
```bash
# Manual trigger from GitHub UI
# Go to Actions > Update README > Run workflow
# Select update type: general, dependencies, api-docs, features, or all
```

### 2. Sync README with Code (`readme-sync.yml`)
**Purpose**: Automatically sync README when Python code changes.

**Triggers**:
- Push to main/develop branches when Python files change
- Changes to requirements.txt, alembic/, or tests/

**Features**:
- Extract project statistics (models, routes, tests)
- Update API endpoints section
- Auto-commit changes directly to branch

### 3. Manual README Update (`readme-manual-update.yml`)
**Purpose**: Quick manual updates with minimal configuration.

**Triggers**:
- Manual dispatch only

**Options**:
- Custom commit message
- Select sections to update (timestamp, toc, format)
- Direct commits to current branch

**Usage**:
```bash
# From GitHub UI: Actions > Manual README Update > Run workflow
# Enter commit message and sections to update
```

### 4. Generate README from Code (`readme-generator.yml`)
**Purpose**: Generate a completely new README based on code analysis.

**Triggers**:
- Manual dispatch only

**Options**:
- Template selection (standard, detailed, minimal)
- Include/exclude badges
- Creates pull request with generated content

**Features**:
- Analyzes entire codebase
- Extracts features, models, routes
- Generates appropriate sections based on template
- Saves as `README_generated.md` for comparison

## Local Script

A Python script is also available for local README updates:

```bash
# Install dependencies first
pip install pyyaml markdown-toc

# Run with various options
python scripts/update_readme.py --help
python scripts/update_readme.py --all
python scripts/update_readme.py --timestamp --toc
python scripts/update_readme.py --validate --dry-run
```

## Workflow Permissions

All workflows require the following repository permissions:
- `contents: write` - To update files
- `pull-requests: write` - To create PRs

## Best Practices

1. **Use Pull Requests**: The workflows that create PRs allow for review before merging
2. **Test Locally First**: Use the local script with `--dry-run` to preview changes
3. **Regular Updates**: The scheduled workflow keeps documentation fresh
4. **Manual Triggers**: Use for immediate updates after significant changes

## Configuration

### Environment Variables
Workflows respect these repository variables:
- `LOG_LEVEL`: For debugging workflow runs
- `GITHUB_TOKEN`: Automatically provided by GitHub

### Customization
To customize the workflows:
1. Fork the repository
2. Modify the workflow files in `.github/workflows/`
3. Adjust triggers, schedules, or update logic as needed

## Troubleshooting

### Common Issues

1. **Workflow not triggering**
   - Check workflow permissions in repository settings
   - Ensure file paths match trigger conditions
   - Verify branch names in push triggers

2. **Permission denied errors**
   - Check repository Settings > Actions > General
   - Ensure "Read and write permissions" is enabled

3. **Pull request conflicts**
   - Manually resolve conflicts in the PR
   - Or close PR and re-run workflow

### Debugging
Enable debug logging:
```yaml
env:
  ACTIONS_STEP_DEBUG: true
```

## Examples

### Example 1: Update Everything
```yaml
# Manually trigger from GitHub UI
# Select "all" as update_type
```

### Example 2: Update Only API Docs
```yaml
# Manually trigger update-readme.yml
# Select "api-docs" as update_type
```

### Example 3: Generate Fresh README
```yaml
# Trigger readme-generator.yml
# Select "detailed" template with badges
```

## Contributing

To add new README update features:
1. Modify the appropriate workflow file
2. Add new update functions to the Python scripts
3. Test locally before committing
4. Document new features in this README