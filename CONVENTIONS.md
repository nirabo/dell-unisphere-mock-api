## Feature Development and Merging Workflow

1. **Create Feature Branch**
   - Branch from master: `git checkout -b feature/X`
   - X should be a short descriptive name for the feature

2. **Development**
   - Make changes and commit with meaningful messages
   - Ensure all tests pass: `make test`
   - Verify commit hooks: `make lint`

3. **Merge to Pilot**
   - Create pilot branch from master: `git checkout -b pilot`
   - Merge feature branch: `git merge feature/X`
   - Resolve any conflicts
   - Verify:
     - `make test`
     - `make lint`
   - Push pilot branch: `git push origin pilot`

4. **Update Master**
   - Merge pilot into master: `git checkout master && git merge pilot`
   - Verify:
     - `make test`
     - `make lint`

5. **Release**
   - Update CHANGELOG.md with changes
   - Bump version in appropriate files (e.g., pyproject.toml)
   - Create release tag: `git tag vX.Y.Z`
   - Push changes: `git push origin master --tags`

**Important Notes:**
- Never merge directly to master
- All merges must go through pilot branch
- Tests and linting must pass at every stage
- Keep feature branches focused on single features

## Version Update Process

1. **Create Hotfix Branch**
   - Branch from master: `git checkout -b hotfix/X`
   - X should be a short descriptive name for the hotfix

2. **Make Changes**
   - Update necessary files (e.g., pyproject.toml, package icons)
   - Update CHANGELOG.md with changes
   - Ensure all tests pass: `make test`
   - Verify commit hooks: `make lint`

3. **Bump Version**
   - Update version in pyproject.toml following semantic versioning
   - For PyPI package icon updates:
     - Ensure icon file is in project root
     - Update package metadata if needed
     - Verify icon displays correctly in PyPI

4. **Merge to Pilot**
   - Create pilot branch from master: `git checkout -b pilot`
   - Merge hotfix branch: `git merge hotfix/X`
   - Resolve any conflicts
   - Verify:
     - `make test`
     - `make lint`
   - Push pilot branch: `git push origin pilot`

5. **Update Master**
   - Merge pilot into master: `git checkout master && git merge pilot`
   - Verify:
     - `make test`
     - `make lint`

6. **Release**
   - Create release tag: `git tag vX.Y.Z`
   - Push changes: `git push origin master --tags`
   - Verify PyPI package update

**Hotfix Guidelines:**
- Only for critical fixes that can't wait for next release
- Must include version bump
- Must update CHANGELOG.md
- Must verify PyPI package updates

## Hotfix Flow Process

1. **Identify Issue**
   - Confirm the issue requires a hotfix
   - Verify the issue is critical and cannot wait for next release

2. **Create Hotfix Branch**
   - Branch from master: `git checkout -b hotfix/X`
   - X should be a short descriptive name for the hotfix

3. **Implement Fix**
   - Make necessary code changes
   - Update version in pyproject.toml
   - Update CHANGELOG.md with hotfix details
   - Run tests: `make test`
   - Run linting: `make lint`

4. **Merge to Pilot**
   - Create pilot branch from master: `git checkout -b pilot`
   - Merge hotfix branch: `git merge hotfix/X`
   - Resolve any conflicts
   - Verify:
     - `make test`
     - `make lint`
   - Push pilot branch: `git push origin pilot`

5. **Update Master**
   - Merge pilot into master: `git checkout master && git merge pilot`
   - Verify:
     - `make test`
     - `make lint`

6. **Release**
   - Create release tag: `git tag vX.Y.Z`
   - Push changes: `git push origin master --tags`
   - Verify PyPI package update

**Hotfix Best Practices:**
- Keep hotfixes focused on the specific issue
- Include comprehensive tests for the fix
- Document the fix in CHANGELOG.md
- Communicate the hotfix to relevant stakeholders
