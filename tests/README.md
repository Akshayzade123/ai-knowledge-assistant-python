# Test Suite for AI Knowledge Assistant

Comprehensive test suite following SOLID principles and best practices.

## 📁 Structure

```text
tests/
├── conftest.py              # Shared fixtures and configuration
├── pytest.ini               # Pytest configuration
├── unit/                    # Unit tests (isolated, fast)
│   ├── test_auth_service.py
│   ├── test_rag_service.py
│   └── test_embed_service.py
└── integration/             # Integration tests (API, database)
    └── test_auth_routes.py
```

## 🚀 Running Tests

### Run All Tests

```bash
pytest
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Specific test file
pytest tests/unit/test_auth_service.py

# Specific test class
pytest tests/unit/test_auth_service.py::TestAuthService

# Specific test function
pytest tests/unit/test_auth_service.py::TestAuthService::test_register_user_success
```

### Run with Coverage

```bash
# Generate coverage report
pytest --cov=src/app --cov-report=html

# View coverage report
# Open htmlcov/index.html in browser
```

### Run with Verbose Output

```bash
pytest -v
```

### Run Tests in Parallel

```bash
pytest -n auto
```

## 🏷️ Test Markers

Tests are marked with custom markers for selective execution:

- `@pytest.mark.unit` - Fast, isolated unit tests
- `@pytest.mark.integration` - Tests requiring external services
- `@pytest.mark.slow` - Slow-running tests
- `@pytest.mark.requires_db` - Tests requiring database
- `@pytest.mark.requires_weaviate` - Tests requiring Weaviate
- `@pytest.mark.requires_gemini` - Tests requiring Gemini API

### Example Usage

```bash
# Skip slow tests
pytest -m "not slow"

# Run only database tests
pytest -m requires_db

# Run unit tests excluding slow ones
pytest -m "unit and not slow"
```

## 🧪 Test Categories

### Unit Tests

**Purpose**: Test individual components in isolation

**Characteristics**:

- Fast execution (< 1 second per test)
- No external dependencies
- Use mocks and stubs
- Test single responsibility

**Examples**:

- `test_auth_service.py` - Authentication logic
- `test_rag_service.py` - RAG query processing
- `test_embed_service.py` - Document embedding

### Integration Tests

**Purpose**: Test component interactions and API endpoints

**Characteristics**:

- Slower execution
- May use test databases
- Test complete workflows
- Validate API contracts

**Examples**:

- `test_auth_routes.py` - Authentication endpoints
- `test_query_routes.py` - Query and document endpoints

## 📝 Writing Tests

### Test Structure (AAA Pattern)

```python
@pytest.mark.unit
async def test_example(self, service, mock_dependency):
    """Test description."""
    # Arrange - Set up test data and mocks
    mock_dependency.method.return_value = expected_value
    
    # Act - Execute the code under test
    result = await service.method(input_data)
    
    # Assert - Verify the results
    assert result == expected_value
    mock_dependency.method.assert_called_once()
```

### Using Fixtures

```python
@pytest.fixture
def my_service(mock_repository):
    """Create service instance for testing."""
    return MyService(repository=mock_repository)

def test_with_fixture(my_service):
    """Test using the fixture."""
    result = my_service.do_something()
    assert result is not None
```

### Mocking Dependencies

```python
from unittest.mock import AsyncMock, patch

# Mock async methods
mock_repo = AsyncMock()
mock_repo.get_user.return_value = mock_user

# Mock external calls
with patch('app.services.external_api.call') as mock_call:
    mock_call.return_value = expected_response
    result = await service.method()
```

## 🎯 Test Coverage Goals

- **Overall Coverage**: > 80%
- **Critical Paths**: > 95% (auth, RAG, security)
- **Services**: > 90%
- **Routes**: > 85%
- **Adapters**: > 80%

### Check Coverage

```bash
# Generate coverage report
pytest --cov=src/app --cov-report=term-missing

# View detailed HTML report
pytest --cov=src/app --cov-report=html
open htmlcov/index.html
```

## 🔧 Configuration

### pytest.ini

Key configuration options:

- Test discovery patterns
- Coverage settings
- Custom markers
- Async mode

### conftest.py

Shared fixtures:

- Mock repositories
- Mock services
- Test data
- Configuration

## 🐛 Debugging Tests

### Run with Debug Output

```bash
pytest -vv --tb=long
```

### Run Single Test with Print Statements

```bash
pytest -s tests/unit/test_auth_service.py::test_example
```

### Use pytest-pdb for Debugging

```bash
pytest --pdb
```

## 📊 Continuous Integration

Tests run automatically on:

- Pull requests
- Commits to main branch
- Scheduled daily runs

### CI Pipeline

1. Lint code (ruff, black, mypy)
2. Run unit tests
3. Run integration tests
4. Generate coverage report
5. Upload coverage to codecov

## 🔒 Testing Best Practices

### DO ✅

- Write tests before or alongside code (TDD)
- Test one thing per test
- Use descriptive test names
- Mock external dependencies
- Test edge cases and error conditions
- Keep tests fast and independent
- Use fixtures for common setup
- Follow AAA pattern (Arrange, Act, Assert)

### DON'T ❌

- Test implementation details
- Write flaky tests
- Share state between tests
- Make tests depend on execution order
- Skip writing tests for "simple" code
- Ignore failing tests
- Write overly complex tests

## 📚 Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [Testing FastAPI](https://fastapi.tiangolo.com/tutorial/testing/)
- [Python Testing Best Practices](https://docs.python-guide.org/writing/tests/)

## 🤝 Contributing

When adding new features:

1. Write tests first (TDD)
2. Ensure all tests pass
3. Maintain or improve coverage
4. Update this README if needed

## 📞 Support

For questions about tests:

- Check existing test examples
- Review this README
- Ask in team chat
