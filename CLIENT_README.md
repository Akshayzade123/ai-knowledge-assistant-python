# AI Knowledge Assistant - Python Client

A comprehensive Python client library for interacting with the AI Knowledge Assistant API.

## Features

✅ **Full API Coverage** - All endpoints supported  
✅ **Type Hints** - Full type annotations for better IDE support  
✅ **Error Handling** - Custom exceptions for different error types  
✅ **Retry Logic** - Automatic retries for failed requests  
✅ **Session Management** - Efficient connection pooling  
✅ **Easy to Use** - Simple, intuitive API  

## Installation

```bash
# Install required dependencies
pip install requests urllib3
```

## Quick Start

```python
from client import KnowledgeAssistantClient

# Initialize client
client = KnowledgeAssistantClient()

# Login
client.login("username", "password")

# Upload a document
client.upload_document(
    file_path="./document.pdf",
    title="Company Policy",
    department="HR"
)

# Ask a question
answer = client.ask_question("What is the vacation policy?")
print(answer['answer'])

# Logout
client.logout()
```

## Usage Examples

### Authentication

```python
from client import KnowledgeAssistantClient, AuthenticationError

client = KnowledgeAssistantClient()

# Register a new user
try:
    client.register(
        username="john_doe",
        email="john@example.com",
        password="SecurePass123!",
        department="Engineering",
        role="user"
    )
    print("✓ User registered successfully")
except AuthenticationError as e:
    print(f"✗ Registration failed: {e}")

# Login
try:
    response = client.login("john_doe", "SecurePass123!")
    print(f"✓ Logged in. Token expires in {response['expires_in']}s")
except AuthenticationError as e:
    print(f"✗ Login failed: {e}")

# Get current user info
user = client.get_current_user()
print(f"Username: {user['username']}")
print(f"Role: {user['role']}")
print(f"Department: {user['department']}")
```

### Document Management

```python
# Upload a document
doc = client.upload_document(
    file_path="./company_handbook.pdf",
    title="Company Handbook 2024",
    department="HR",
    access_level="department"  # "public", "department", or "restricted"
)
print(f"✓ Uploaded document ID: {doc['document_id']}")

# List all accessible documents
documents = client.get_documents(limit=20)
for doc in documents:
    print(f"- {doc['title']} (ID: {doc['id']})")

# Get specific document details
doc_details = client.get_document(document_id=123)
print(f"Title: {doc_details['title']}")
print(f"Uploaded by: {doc_details['uploaded_by']}")
print(f"Created: {doc_details['created_at']}")

# Delete a document
client.delete_document(document_id=123)
print("✓ Document deleted")
```

### Querying the Knowledge Base

```python
# Ask a question
answer = client.ask_question("What is the remote work policy?")

print(f"Answer: {answer['answer']}")
print(f"Confidence: {answer['confidence']:.2%}")
print(f"Tokens used: {answer['tokens_used']}")

# Display sources
for i, source in enumerate(answer['sources'], 1):
    print(f"\nSource {i}:")
    print(f"  Title: {source['title']}")
    print(f"  Relevance: {source['score']:.2%}")
    print(f"  Excerpt: {source['chunk'][:100]}...")

# Get query history
history = client.get_query_history(limit=10)
for query in history:
    print(f"- {query['question']} ({query['created_at']})")
```

### Error Handling

```python
from client import (
    KnowledgeAssistantClient,
    AuthenticationError,
    APIError,
    KnowledgeAssistantError
)

client = KnowledgeAssistantClient()

try:
    # Attempt operations
    client.login("user", "pass")
    answer = client.ask_question("What is...?")
    
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
    # Handle auth errors (e.g., redirect to login)
    
except APIError as e:
    print(f"API request failed: {e}")
    # Handle API errors (e.g., retry, show error message)
    
except KnowledgeAssistantError as e:
    print(f"General error: {e}")
    # Handle other errors
    
except Exception as e:
    print(f"Unexpected error: {e}")
    # Handle unexpected errors
```

### Advanced Configuration

```python
# Custom configuration
client = KnowledgeAssistantClient(
    base_url="https://api.example.com/api/v1",
    timeout=60,  # Request timeout in seconds
    max_retries=5  # Maximum number of retries
)

# Check API health
health = client.health_check()
print(f"API Status: {health['status']}")

# Client representation
print(client)  # KnowledgeAssistantClient(base_url='...', authenticated)
```

## Running Tests

### Automated Test Suite

```bash
# Run all tests
python test_client.py

# Expected output:
# ======================================================================
#   AI KNOWLEDGE ASSISTANT - PYTHON CLIENT TEST SUITE
# ======================================================================
# 
# ======================================================================
#   AUTHENTICATION TESTS
# ======================================================================
# 
# 1. Checking API health...
#    ✓ API Status: healthy
# 
# 2. Logging in...
#    ✓ Login successful
#    - Token type: bearer
#    - Expires in: 1800 seconds
# 
# ... (more tests)
# 
# ======================================================================
#   TEST SUMMARY
# ======================================================================
# 
#    ✓ PASSED: Authentication
#    ✓ PASSED: Document Operations
#    ✓ PASSED: Query Operations
#    ✓ PASSED: Error Handling
# 
#    Total: 4/4 tests passed
# 
#    🎉 All tests passed!
```

### Interactive Mode

```bash
# Run in interactive mode
python test_client.py --interactive

# Interactive menu:
# ----------------------------------------------------------------------
# What would you like to do?
# 1. Ask a question
# 2. List documents
# 3. View query history
# 4. Upload document
# 5. Exit
# 
# Choice (1-5):
```

## API Reference

### KnowledgeAssistantClient

#### Constructor

```python
KnowledgeAssistantClient(
    base_url: str = "http://localhost:8000/api/v1",
    timeout: int = 30,
    max_retries: int = 3
)
```

#### Authentication Methods

- `register(username, email, password, department, role="user")` - Register new user
- `login(username, password)` - Login and get token
- `get_current_user()` - Get current user info
- `logout()` - Clear authentication token

#### Document Methods

- `upload_document(file_path, title, department, access_level="department")` - Upload document
- `get_documents(skip=0, limit=100)` - List accessible documents
- `get_document(document_id)` - Get document details
- `delete_document(document_id)` - Delete document

#### Query Methods

- `ask_question(question, collection_name="Documents")` - Ask a question
- `get_query_history(limit=10)` - Get query history

#### Utility Methods

- `health_check()` - Check API health

### Exceptions

- `KnowledgeAssistantError` - Base exception
- `AuthenticationError` - Authentication failures
- `APIError` - API request failures

## Best Practices

### 1. Always Use Context Managers (Future Enhancement)

```python
# Future: Context manager support
with KnowledgeAssistantClient() as client:
    client.login("user", "pass")
    answer = client.ask_question("...")
# Automatically logs out
```

### 2. Handle Errors Gracefully

```python
try:
    answer = client.ask_question("...")
except AuthenticationError:
    # Re-authenticate
    client.login(username, password)
    answer = client.ask_question("...")
```

### 3. Use Type Hints

```python
from typing import Dict, List

def process_documents(client: KnowledgeAssistantClient) -> List[Dict]:
    return client.get_documents(limit=50)
```

### 4. Log Important Operations

```python
import logging

logging.basicConfig(level=logging.INFO)
client = KnowledgeAssistantClient()
# Client automatically logs operations
```

### 5. Validate Inputs

```python
from pathlib import Path

def safe_upload(client, file_path: str):
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if path.suffix not in ['.pdf', '.txt', '.docx']:
        raise ValueError(f"Unsupported file type: {path.suffix}")
    
    return client.upload_document(
        file_path=str(path),
        title=path.stem,
        department="General"
    )
```

## Troubleshooting

### Connection Errors

```python
# Check if API is running
try:
    health = client.health_check()
    print(f"API is {health['status']}")
except Exception as e:
    print("API is not accessible. Is it running?")
```

### Authentication Issues

```python
# Verify credentials
try:
    client.login("username", "password")
except AuthenticationError as e:
    print(f"Login failed: {e}")
    print("Please check your username and password")
```

### Timeout Issues

```python
# Increase timeout for slow connections
client = KnowledgeAssistantClient(timeout=120)
```

## Examples

See `test_client.py` for comprehensive examples of all features.

## Contributing

Contributions are welcome! Please ensure:

- Code follows PEP 8 style guide
- All methods have docstrings
- Type hints are used throughout
- Tests pass successfully

## License

MIT License - see LICENSE file for details.
