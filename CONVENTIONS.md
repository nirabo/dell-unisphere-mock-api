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
