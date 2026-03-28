# Contributing to Tomcat Monitoring Toolkit

Thank you for your interest in contributing to the Tomcat Monitoring Toolkit! We welcome contributions from the community. This document provides guidelines and instructions for contributing.

## 🤝 Ways to Contribute

- **Report Bugs**: Find and report issues you encounter
- **Suggest Features**: Propose new features or improvements
- **Submit Code**: Fix bugs or implement new features
- **Improve Documentation**: Help us improve README, guides, and comments
- **Share Feedback**: Let us know how we can improve

## 📋 Getting Started

### Prerequisites

- Python 3.10+
- Git
- Docker & docker-compose (optional, for testing)
- Basic understanding of Tomcat and JMX

### Setting Up Your Development Environment

1. **Fork the repository**
   ```bash
   # Click "Fork" button on GitHub
   ```

2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR-USERNAME/Tomcat-Monitoring-Toolkit.git
   cd Tomcat-Monitoring-Toolkit
   ```

3. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or for bug fixes:
   git checkout -b bugfix/your-bug-fix
   ```

4. **Set up virtual environment**
   ```bash
   python3.10 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

5. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install pytest pytest-cov flake8 black  # Development tools
   ```

## 🐛 Reporting Bugs

When reporting a bug, please include:

1. **Description**: Clear description of the bug
2. **Steps to Reproduce**: How to reproduce the issue
3. **Expected Behavior**: What should happen
4. **Actual Behavior**: What actually happens
5. **Environment**: 
   - Python version
   - Tomcat version
   - OS/Platform
   - Docker version (if applicable)
6. **Logs**: Relevant log output
7. **Configuration**: Sanitized config.yaml (remove sensitive data)

### Bug Report Template

```
**Title**: [Brief description]

**Description**: 
[Detailed description of the bug]

**Steps to Reproduce**:
1. [First step]
2. [Second step]
3. [...]

**Expected Behavior**: 
[What should happen]

**Actual Behavior**: 
[What happens instead]

**Environment**:
- Python: 3.10.x
- Tomcat: 9.0.x
- OS: [Linux/macOS/Windows]

**Logs**:
```
[Relevant logs here]
```
```

## ✨ Suggesting Features

We love new ideas! Before submitting a feature request:

1. Check existing issues to see if it's already been suggested
2. Provide clear use case and benefits
3. Consider implementation complexity
4. Examples of how it would be used are helpful

### Feature Request Template

```
**Title**: [Feature name]

**Use Case**: 
[Why is this feature needed?]

**Description**: 
[Detailed description]

**Example Usage**: 
[How would users use this?]

**Benefits**: 
[What problems does it solve?]

**Alternatives Considered**: 
[Other approaches?]
```

## 💻 Submitting Code Changes

### Code Style Guidelines

We follow PEP 8 with some modifications:

1. **Format with Black**:
   ```bash
   black *.py
   ```

2. **Lint with Flake8**:
   ```bash
   flake8 *.py --max-line-length=100
   ```

3. **Type Hints**: Use type hints in function signatures
   ```python
   def function_name(param1: str, param2: int) -> bool:
       """Function description."""
       pass
   ```

4. **Docstrings**: Use Google-style docstrings
   ```python
   def example_function(param1: str) -> None:
       """
       Brief description.
       
       Longer description if needed.
       
       Args:
           param1: Description of param1
           
       Returns:
           Description of return value
           
       Raises:
           ValueError: When something is wrong
       """
       pass
   ```

5. **Comments**: Write clear, meaningful comments
   - Explain *why*, not *what*
   - Keep comments up-to-date with code

### Making Code Changes

1. **Make your changes** in your feature branch
2. **Test locally** using the testing guide (see TESTING.md)
3. **Format your code**:
   ```bash
   black *.py
   flake8 *.py --max-line-length=100
   ```

4. **Run tests**:
   ```bash
   pytest -v --cov
   ```

5. **Commit with clear messages**:
   ```bash
   git commit -m "feat: add new monitoring feature for X"
   # or
   git commit -m "fix: resolve issue with Y"
   # or
   git commit -m "docs: update README with Z"
   ```

   Use conventional commits:
   - `feat:` - New feature
   - `fix:` - Bug fix
   - `docs:` - Documentation changes
   - `refactor:` - Code refactoring
   - `test:` - Test changes
   - `chore:` - Build/dependency changes

6. **Push your branch**:
   ```bash
   git push origin feature/your-feature-name
   ```

### Creating a Pull Request

1. **Go to GitHub** and create a Pull Request
2. **Fill in the PR template**:
   - Link related issues
   - Describe your changes
   - List any breaking changes
   - Add testing notes

3. **PR Title Format**:
   ```
   [feat/fix/docs] Brief description
   ```

4. **PR Description Template**:
   ```
   ## Description
   [Describe your changes]
   
   ## Related Issues
   Fixes #123
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Documentation update
   - [ ] Performance improvement
   
   ## Testing
   [Describe how you tested this]
   
   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Tests pass
   - [ ] Documentation updated
   - [ ] No breaking changes
   ```

## 📝 Testing Guidelines

### Running Tests

```bash
# Run all tests
pytest -v

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_config_manager.py -v

# Run specific test
pytest tests/test_config_manager.py::test_load_config -v
```

### Writing Tests

- Write tests for new features
- Ensure existing tests still pass
- Aim for >80% code coverage
- Use descriptive test names: `test_<function>_<scenario>_<expected_result>`

Example:
```python
def test_health_score_calculation_with_critical_heap_returns_low_score():
    """Test health score calculation when heap is critical."""
    pass
```

## 📚 Documentation

### Updating Documentation

- Update README.md for user-facing changes
- Update TESTING.md for testing changes
- Add docstrings to new functions
- Update examples in `examples/` directory

### Writing Good Documentation

- Be clear and concise
- Use examples
- Include code snippets
- Explain complex concepts
- Keep it up-to-date

## 🔄 Review Process

1. **GitHub Actions**: Automated tests must pass
2. **Code Review**: Maintainers will review your PR
3. **Feedback**: We may request changes
4. **Approval**: Once approved, your PR will be merged
5. **Release**: Your changes will be included in the next release

## 📦 Release Process

We follow semantic versioning: `MAJOR.MINOR.PATCH`

- `MAJOR`: Breaking changes
- `MINOR`: New features
- `PATCH`: Bug fixes

## 🚫 Code of Conduct

- Be respectful and inclusive
- Welcome diverse perspectives
- Provide constructive feedback
- Report inappropriate behavior to maintainers

## ❓ Questions?

- Check existing issues and documentation
- Create a new issue with your question
- Join our community discussions

## 🙏 Thank You!

Your contributions make this project better for everyone. We appreciate your time and effort!

---

**Happy contributing! 🎉**
