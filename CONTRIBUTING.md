# Contributing to docsmith

Thank you for your interest in contributing to docsmith!

## Development Setup

### 1. Clone the repository

```bash
git clone https://github.com/izag8216/docsmith.git
cd docsmith
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -e ".[dev]"
```

### 4. Run tests

```bash
pytest
```

### 5. Run with coverage

```bash
pytest --cov=docsmith --cov-report=term-missing --cov-fail-under=80
```

## Code Style

We use `black` for code formatting and `ruff` for linting.

```bash
# Format code
black src/

# Check linting
ruff check src/
```

## Testing

- All new features should include tests
- All tests must pass before merging
- Maintain 80%+ test coverage

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Reporting Bugs

Please report bugs via GitHub Issues with:

- Your environment (OS, Python version)
- docsmith version
- Minimal reproducible example
- Expected vs actual behavior

## Suggesting Features

Open an issue with the label `enhancement` and describe:

- The problem you're trying to solve
- Your proposed solution
- Alternative solutions considered

## License

By contributing, you agree that your contributions will be licensed under the MIT License.