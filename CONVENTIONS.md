# **Coding Conventions and Workflow Guidelines**

## **Branch Naming Conventions**

Adopting clear and consistent branch naming conventions enhances collaboration and code management.

- **Use Prefixes to Indicate Purpose:**
  - `feature/`: For new features.
  - `bugfix/`: For bug fixes.
  - `hotfix/`: For critical fixes that need immediate attention.
  - `release/`: For preparing a release.

- **Use Descriptive Names:**
  - Keep branch names concise yet descriptive, using hyphens to separate words.
  - Example: `feature/user-authentication`.

- **Include Issue or Ticket Numbers** (if applicable):
  - Incorporate relevant issue or ticket numbers to link branches to specific tasks.
  - Example: `bugfix/1234-fix-login-error`.

---

## **Feature Development and Merging Workflow**

### 1. **Create a Feature Branch**
- Branch from `main`:
  ```bash
  git checkout -b feature/<short-descriptive-name>
  ```

### 2. **Development**
- Implement changes with regular commits, ensuring commit messages are clear and meaningful.
- Run tests to ensure code quality:
  ```bash
  make test
  ```
- Verify code formatting and linting:
  ```bash
  make lint
  ```
- Update `CHANGELOG.md` and version files (`pyproject.toml`) as part of the development process:
  ```bash
  nano CHANGELOG.md  # Document planned changes
  nano pyproject.toml  # Bump version
  ```

### 3. **Merge to Integration Branch**
- Create an integration branch (e.g., `develop`) if it doesn't exist:
  ```bash
  git checkout -b develop
  ```
- Merge the feature branch into the integration branch:
  ```bash
  git merge feature/<short-descriptive-name>
  ```
- Resolve any merge conflicts.
- Verify integration by running tests and linting:
  ```bash
  make test
  make lint
  ```
- Push the integration branch to the remote repository:
  ```bash
  git push origin develop
  ```

### 4. **Update Main Branch**
- Merge the integration branch into `main`:
  ```bash
  git checkout main
  git merge develop
  ```
- Ensure all tests and linting pass:
  ```bash
  make test
  make lint
  ```

### 5. **Release**
- Create a release tag:
  ```bash
  git tag vX.Y.Z
  ```
- Push changes and tags to the remote repository:
  ```bash
  git push origin main --tags
  ```

---

## **Hotfix Workflow**

### 1. **Create a Hotfix Branch**
- Branch from `main`:
  ```bash
  git checkout -b hotfix/<short-descriptive-name>
  ```

### 2. **Implement the Fix**
- Make necessary code changes to address the issue.
- Update `CHANGELOG.md` with details of the fix.
- Update the version in `pyproject.toml` (increment the patch version for hotfixes).
- Run tests and linting:
  ```bash
  make test
  make lint
  ```
- Commit the changes:
  ```bash
  git add CHANGELOG.md pyproject.toml
  git commit -m "hotfix: <description>"
  ```

### 3. **Merge to Integration Branch**
- Merge the hotfix branch into the integration branch:
  ```bash
  git checkout develop
  git merge hotfix/<short-descriptive-name>
  ```
- Resolve any conflicts and verify integration:
  ```bash
  make test
  make lint
  ```
- Push the integration branch:
  ```bash
  git push origin develop
  ```

### 4. **Update Main Branch**
- Merge the integration branch into `main`:
  ```bash
  git checkout main
  git merge develop
  ```
- Ensure all tests and linting pass:
  ```bash
  make test
  make lint
  ```

### 5. **Release**
- Create a release tag:
  ```bash
  git tag vX.Y.Z
  ```
- Push changes and tags:
  ```bash
  git push origin main --tags
  ```

---

## **Streamlined Version Update Process**

### 1. **Include `CHANGELOG.md` and Version Updates During Development**
- Update `CHANGELOG.md` and version files (`pyproject.toml`) during feature or hotfix development to avoid redundant steps later.

### 2. **Commit and Verify Updates**
- Commit changes as part of the development workflow:
  ```bash
  git add CHANGELOG.md pyproject.toml
  git commit -m "chore: update CHANGELOG and bump version to vX.Y.Z"
  ```
- Verify using tests and linting.

### 3. **Push and Merge**
- Merge the branch into `develop` for integration testing.
- Ensure the integration branch is clean and verified before merging into `main`.

### 4. **Release Directly from `Main`**
- Once verified, release changes from `main` without additional updates to `CHANGELOG.md` or version files.

---

## **GitHub Workflow and Release Process**

### Branch Strategy
1. Feature Development
   - Create feature branches from `integration` branch
   - Branch naming: `feature/feature-name`
   - Commit messages must follow [Conventional Commits](https://www.conventionalcommits.org/)

2. Pull Request Process
   - Create PR from feature branch to `integration`
   - PR title must follow Conventional Commits format
   - PR must pass all automated checks:
     - All tests must pass
     - Code must pass linting
     - Version consistency must be verified
   - PR must be approved by at least one reviewer
   - After approval and passing checks, PR can be merged to `integration`

3. Release Process
   - Create PR from `integration` to `main` when ready to release
   - PR must pass all automated checks and be approved
   - Upon merging to `main`:
     - GitHub Actions will automatically create a new release
     - Release will be tagged with version from `pyproject.toml`
     - Release notes will be generated from `CHANGELOG.md`

### Version Management

---

### **General Best Practices**
- Avoid direct commits to `main`.
- Ensure all tests and linting pass at every stage.
- Use CI/CD pipelines to automate verification steps and releases.
- Keep branches focused on a single feature, bugfix, or hotfix to simplify reviews and integration.
