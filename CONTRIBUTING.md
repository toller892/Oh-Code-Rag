# Contributing to CodeTree

Thank you for your interest in contributing to CodeTree! 🌲

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/codetree.git
   cd codetree
   ```
3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

## Development Setup

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black src/
ruff check src/
```

## How to Contribute

### Reporting Bugs

- Check existing issues first
- Include reproduction steps
- Include your environment (OS, Python version, etc.)

### Feature Requests

- Open an issue to discuss the feature first
- Explain the use case and benefits

### Pull Requests

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes
3. Add tests if applicable
4. Run tests and linting
5. Commit with clear messages
6. Push and create a PR

## Code Style

- Follow PEP 8
- Use type hints
- Write docstrings for public functions
- Keep functions focused and small

## Areas to Contribute

- 🌍 **Language Support**: Add parsers for new languages (C++, Ruby, PHP, etc.)
- 🧪 **Testing**: Improve test coverage
- 📖 **Documentation**: Improve docs and examples
- 🚀 **Performance**: Optimize indexing for large repos
- 🎨 **CLI**: Improve the command-line experience

## Questions?

Open an issue or start a discussion!
