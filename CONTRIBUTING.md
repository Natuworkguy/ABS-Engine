# Contributing to ABS Engine

Thank you for your interest in contributing to ABS Engine.

Contributions of all types are welcome, including:

- Bug fixes
- Performance improvements
- Documentation updates
- Refactoring
- Testing improvements
- New features
- Tooling and CI enhancements

Please read this document before submitting changes.

> [!Note]
> All contributions should target the `dev` branch. Changes are reviewed and
> tested there before being merged into `main` for releases.

---

## Development Setup

### 1. Fork and Clone the Repository

```bash
git clone https://github.com/Natuworkguy/ABS-Engine.git
cd ABS-Engine
````

---

### 2. Create a Virtual Environment

#### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

#### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### 3. Install Dependencies

Install both runtime and development dependencies:

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
npm install -g markdownlint-cli2 
```

---

## Code Standards

ABS Engine enforces strong code quality and static analysis standards.

All contributions should prioritize:

- Readability
- Maintainability
- Type safety
- Security
- Consistency
- Modular architecture

---

## Formatting, Linting, and Type Checking

Before opening a pull request, run all checks locally.

## Ruff

```bash
ruff check .
ruff format .
```

## MyPy

```bash
mypy .
```

## Pyright

```bash
pyright
```

## Flake8

```bash
flake8 . --ignore=E501
```

## Bandit

```bash
bandit -r .
```

## MarkdownLint

```bash
markdownlint-cli2 .
```

## Darglint

```bash
darglint .
```

## Interrogate

```bash
interrogate
```

All checks must pass before a pull request will be reviewed.

---

## Type Hinting Requirements

ABS Engine uses static typing throughout the codebase.

Contributors should:

- Add type hints to new code
- Avoid unnecessary use of `Any`
- Minimize unnecessary `type: ignore` comments
- Prefer explicit return types when appropriate

Example:

```python
def load_project(path: Path) -> dict[str, Any]:
    ...
```

---

## Pull Requests

When submitting a pull request:

- Keep changes focused and minimal
- Write clear commit messages
- Ensure CI passes
- Update documentation when necessary
- Add or update tests if applicable

For UI-related changes, screenshots are encouraged.

---

## Commit Message Guidelines

Use concise, descriptive commit messages.

## Examples

```text
Add sprite batching optimization
Fix project loading race condition
Refactor renderer initialization
Improve type annotations in asset manager
```

Avoid vague messages such as:

```text
fix
update
changes
stuff
```

---

## Reporting Bugs

Bug reports should include:

- Operating system
- Python version
- Steps to reproduce
- Expected behavior
- Actual behavior
- Relevant logs or screenshots

Incomplete reports may be difficult to investigate.

---

## Feature Requests

Feature requests should clearly explain:

- The problem being solved
- The proposed solution
- Potential implementation details
- Possible drawbacks or tradeoffs

---

## Branch Naming

Recommended branch naming conventions:

```text
feature/new-renderer
fix/editor-crash
refactor/project-loader
docs/api-updates
```

---

## Security

Do not publicly disclose vulnerabilities or security issues.

Report security-related concerns privately to the maintainers.

---

## Documentation Contributions

Documentation improvements are highly valued.

This includes:

- Fixing inaccuracies
- Improving examples
- Updating setup instructions
- Clarifying APIs
- Improving readability

---

## Contributor Conduct

Be respectful and constructive in discussions, issues, and pull requests.

Professional collaboration helps maintain a productive development environment.

---

## License

By contributing to ABS Engine, you agree that your contributions
will be licensed under the GNU General Public License v3.0 (GPLv3).
