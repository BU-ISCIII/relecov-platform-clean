# Patho-webcore: Contributing Guidelines

Thank you for considering contributing to the Patho-webcore project! Below, you'll find an outline of how to contribute effectively to our project. Please read through these guidelines before starting.

## Contribution workflow
<!-- Add details about the workflow for contributing, such as creating issues, branching conventions, submitting pull requests, and the review process. -->

## Tests

### Lint tests
<!-- Specify the linting tools used in the project and how contributors should run them (e.g., `flake8`, `black`, etc.). -->

### Code Tests
<!-- Provide instructions on running the project's test suite, including setup steps and commands (e.g., `pytest`). -->

## Version Release
### Check list before releasing a version

- [ ] Ensure all CI/CD tests on the `develop` branch are passing.
- [ ] Address any warnings from automated linters or tools.
    - [ ] Update outdated dependencies and verify compatibility.

- [ ] Resolve any outstanding issues, prioritizing bug fixes and critical updates.
- [ ] Review and finalize the description of the repository for release, ensuring any "under `develop`" labels are removed.
- [ ] Close or move unresolved milestone issues to the next version, as needed.

### Steps to release
1. Update the `develop` branch to reflect the release version:
    - Example: 1.0.0-develop becomes 1.0.0.
    - Use versioning tools to ensure consistent updates across all files and metadata.
2. Validate the release:
    - Run tests and ensure no failures occur.
    - Confirm CHANGELOG.md includes all relevant updates for the release.
    - Add contributors to CHANGELOG.md for improved recognition.
3. Submit a Pull Request (PR):
    - Create a PR from your fork to the `develop` branch with the release changes.
    - After merging, create another PR from source repo `develop` branch to the `main` branch for final review and approval (2 reviews are required).
4. Publish the release:
    - Tag the release version in GitHub (e.g., 1.0.0).
    - Include an optional descriptive title or code name for the release.

### After Release

5. Bump the version number for continued `develop`:
    - Example: 1.0.0 becomes 1.1.0-develop.
    - Update CHANGELOG.md to include a new section for upcoming changes.
