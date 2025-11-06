# AI Knowledge Assistant for Enterprises

A production-ready **Retrieval-Augmented Generation (RAG)** system using **Docker AI EmbeddingGemma** for local embeddings and **Gemini 2.0** for generation, integrated with **PostgreSQL** and **Weaviate** to provide internal document Q&A with semantic memory and user access control.

Built with exemplary **SOLID principles**, clean architecture, and enterprise-grade features.

## 🌟 Features

- **🤖 RAG-Powered Q&A**: Local embeddings with Docker AI + Gemini 2.0 for accurate, context-aware answers
- **🔐 Access Control**: Role-based permissions (Admin, User, Viewer) with department-level isolation
- **📚 Document Management**: Support for PDF, DOCX, TXT, and Markdown files
- **🔍 Vector Search**: Weaviate-powered semantic search with configurable similarity thresholds
- **📊 Query Logging**: Complete audit trail of user queries and responses
- **🚀 FastAPI Backend**: High-performance async API with automatic OpenAPI documentation
- **🐳 Docker Ready**: Complete containerization with docker-compose + Docker AI integration
- **✨ SOLID Architecture**: Exemplary implementation of all five SOLID principles
- **🆓 Local Embeddings**: Free, private embeddings using Docker AI's EmbeddingGemma (300M params)

## 🏗️ Architecture & SOLID Principles

This project demonstrates **production-ready software engineering** with rigorous application of SOLID principles:

### **S - Single Responsibility Principle**

Each class has one reason to change:

- `RAGService`: Only handles RAG query processing
- `AuthService`: Only handles authentication/authorization
- `EmbedService`: Only handles document ingestion and embedding
- Each repository manages one entity type

### **O - Open/Closed Principle**

Open for extension, closed for modification:

- New LLM providers can be added by implementing `IEmbeddingProvider` or `IGenerationProvider`
- New vector stores can be added by implementing `IVectorStore`
- New document types can be supported by extending `EmbedService._load_document()`

### **L - Liskov Substitution Principle**

Abstractions are substitutable:

- Any `IVectorStore` implementation (Weaviate, Pinecone, etc.) can replace another
- Any `IGenerationProvider` (Gemini, OpenAI, etc.) can be swapped without breaking services

### **I - Interface Segregation Principle**

Focused, minimal interfaces:

- `IEmbeddingProvider` and `IGenerationProvider` are separate (not one bloated LLM interface)
- `IUserRepository`, `IDocumentRepository`, `IQueryLogRepository` are segregated by concern

### **D - Dependency Inversion Principle**

High-level modules depend on abstractions:

- `RAGService` depends on `IVectorStore`, not `WeaviateAdapter`
- `AuthService` depends on `IUserRepository`, not `PostgresAdapter`
- All dependencies injected via `dependencies.py`

## 📁 Project Structure

```text
ai-knowledge-assistant/
│
├── src/
│   └── app/
│       ├── main.py                      # FastAPI application
│       │
│       ├── interfaces/                  # Abstract interfaces (SOLID-D)
│       │   ├── vector_store.py          # IVectorStore interface
│       │   ├── database.py              # Repository interfaces
│       │   ├── llm.py                   # LLM provider interfaces
│       │   └── auth.py                  # Authentication interface
│       │
│       ├── adapters/                    # Infrastructure implementations
│       │   ├── weaviate_adapter.py      # Weaviate vector store
│       │   ├── postgres_adapter.py      # PostgreSQL repositories
│       │   └── gemini_adapter.py        # Google Gemini LLM
│       │
│       ├── services/                    # Business logic (SOLID-S)
│       │   ├── rag_service.py           # RAG query processing
│       │   ├── embed_service.py         # Document ingestion
│       │   └── auth_service.py          # Authentication/authorization
│       │
│       ├── routes/                      # API endpoints
│       │   ├── query_router.py          # Query & document endpoints
│       │   └── auth_router.py           # Authentication endpoints
│       │
│       ├── models/                      # Pydantic schemas
│       │   └── schemas.py               # Request/response models
│       │
│       └── core/                        # Configuration & utilities
│           ├── config.py                # Settings management
│           ├── dependencies.py          # Dependency injection
│           └── logging_config.py        # Logging setup
│
├── asgi.py                              # ASGI entry point (run with: python asgi.py)
├── docker-compose.yml                   # Multi-container setup
├── Dockerfile                           # Application container
├── pyproject.toml                       # uv/pip configuration
├── requirements.txt                     # Python dependencies (legacy)
└── .env.example                         # Environment template
```

### **Why This Structure?**

1. **Separation of Concerns**: Interfaces, adapters, services, and routes are clearly separated
2. **Testability**: Each layer can be tested independently with mocks
3. **Maintainability**: Changes to infrastructure don't affect business logic
4. **Scalability**: Easy to add new features without modifying existing code
5. **SOLID Compliance**: Architecture enforces all five SOLID principles naturally

### **Key Files Explained**

- **`asgi.py`**: Application entry point - run with `uv run asgi.py`
- **`src/app/main.py`**: FastAPI app configuration and route registration
- **`src/app/interfaces/`**: Abstract base classes defining contracts (Dependency Inversion)
- **`src/app/adapters/`**: Concrete implementations of external services
- **`src/app/services/`**: Business logic layer (orchestrates adapters)
- **`src/app/routes/`**: HTTP endpoints and request/response handling
- **`src/app/core/dependencies.py`**: Dependency injection container
- **`pyproject.toml`**: Modern Python project configuration with uv support

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Google Gemini API Key ([Get one here](https://makersuite.google.com/app/apikey))

### Installation & Setup

```bash
# Clone the repository
git clone https://github.com/sabry-awad97/ai-knowledge-assistant.git
cd ai-knowledge-assistant

# Copy environment template
cp .env.example .env

# Edit .env and add your Gemini API key
# GEMINI_API_KEY=your-api-key-here
```

### Run with Docker Compose

```bash
# Start all services (PostgreSQL, Weaviate, API)
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build

# View logs
docker-compose logs -f api

# Stop services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

**The API will be available at `http://localhost:8000`**

### Docker Commands Reference

```bash
# Rebuild only the API service
docker-compose build api

# Restart a specific service
docker-compose restart api

# View logs for all services
docker-compose logs -f

# Check service status
docker-compose ps

# Execute commands in the API container
docker-compose exec api bash
```

## 📖 API Documentation

Once running, visit:

- **Swagger UI**: <http://localhost:8000/api/v1/docs>
- **ReDoc**: <http://localhost:8000/api/v1/redoc>
- **Health Check**: <http://localhost:8000/health>

## 💼 Use Cases

### **1. Enterprise Knowledge Management**

Build an intelligent company knowledge base where employees can:

- Upload company policies, procedures, and handbooks
- Ask natural language questions about HR policies, benefits, vacation rules
- Get instant answers with source citations
- Department-specific access control for sensitive documents

**Example**: *"What is our remote work policy?"* → System retrieves relevant sections from HR handbook

### **2. Technical Documentation Assistant**

Create a smart documentation system for engineering teams:

- Upload API documentation, architecture diagrams, technical specs
- Query complex technical information instantly
- Onboard new developers faster with conversational docs
- Version control through document updates

**Example**: *"How do I authenticate with the payment API?"* → Returns authentication flow with code examples

### **3. Customer Support Knowledge Base**

Power your support team with instant answers:

- Upload product manuals, FAQs, troubleshooting guides
- Support agents get quick answers to customer questions
- Reduce response time and improve accuracy
- Track common questions through query history

**Example**: *"How do I reset my password?"* → Step-by-step instructions from support docs

### **4. Legal & Compliance Assistant**

Manage legal documents and compliance requirements:

- Upload contracts, regulations, compliance documents
- Quick reference for legal teams
- Ensure compliance with instant policy lookups
- Restricted access for sensitive legal materials

**Example**: *"What are the GDPR data retention requirements?"* → Relevant compliance sections

### **5. Research & Academic Assistant**

Organize and query research materials:

- Upload research papers, journals, study materials
- Ask questions across multiple papers
- Literature review assistance
- Citation tracking with source references

**Example**: *"What are the main findings about climate change in these papers?"* → Synthesized summary

### **6. Sales & Marketing Intelligence**

Centralize sales and marketing materials:

- Upload product catalogs, case studies, competitive analysis
- Sales teams get instant product information
- Marketing teams access brand guidelines
- Competitive intelligence queries

**Example**: *"What are our key differentiators vs Competitor X?"* → Competitive advantages

### **7. Training & Onboarding Platform**

Accelerate employee training:

- Upload training materials, SOPs, best practices
- New employees ask questions during onboarding
- Self-service learning platform
- Track learning progress through query history

**Example**: *"How do I submit an expense report?"* → Process explanation with links

### **8. Healthcare Documentation**

Medical knowledge management (non-diagnostic):

- Upload medical protocols, treatment guidelines
- Quick reference for healthcare professionals
- Research medical procedures and best practices
- HIPAA-compliant access controls

**Example**: *"What is the standard protocol for post-surgery care?"* → Clinical guidelines

## 🔑 API Usage Examples

### 1. Register a User

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepassword123",
    "department": "Engineering"
  }'
```

### 2. Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "securepassword123"
  }'
```

Response:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### 3. Upload a Document

```bash
curl -X POST "http://localhost:8000/api/v1/query/documents/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@document.pdf" \
  -F "title=Company Handbook" \
  -F "department=Engineering" \
  -F "access_level=department"
```

### 4. Ask a Question

```bash
curl -X POST "http://localhost:8000/api/v1/query/ask" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is our vacation policy?",
    "collection_name": "Documents"
  }'
```

Response:

```json
{
  "answer": "According to the company handbook, employees receive 20 days of paid vacation per year...",
  "sources": [
    {
      "title": "Company Handbook",
      "score": 0.92,
      "chunk_index": 5,
      "excerpt": "Vacation Policy: All full-time employees..."
    }
  ],
  "confidence": 0.89,
  "tokens_used": 245
}
```

### 5. View Query History

```bash
curl -X GET "http://localhost:8000/api/v1/query/history?limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🎨 Frontend Integration

### **React/Next.js Example**

```typescript
// lib/api.ts
const API_BASE = 'http://localhost:8000/api/v1';

export class KnowledgeAssistantAPI {
  private token: string | null = null;

  async login(username: string, password: string) {
    const response = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    const data = await response.json();
    this.token = data.access_token;
    localStorage.setItem('token', data.access_token);
    return data;
  }

  async uploadDocument(file: File, title: string, department: string) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', title);
    formData.append('department', department);
    formData.append('access_level', 'department');

    const response = await fetch(`${API_BASE}/query/upload`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${this.token}` },
      body: formData,
    });
    return response.json();
  }

  async askQuestion(question: string) {
    const response = await fetch(`${API_BASE}/query/ask`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        question,
        collection_name: 'Documents',
      }),
    });
    return response.json();
  }

  async getDocuments() {
    const response = await fetch(`${API_BASE}/query/documents`, {
      headers: { 'Authorization': `Bearer ${this.token}` },
    });
    return response.json();
  }

  async getQueryHistory(limit = 10) {
    const response = await fetch(`${API_BASE}/query/history?limit=${limit}`, {
      headers: { 'Authorization': `Bearer ${this.token}` },
    });
    return response.json();
  }
}

// components/ChatInterface.tsx
'use client';

import { useState } from 'react';
import { KnowledgeAssistantAPI } from '@/lib/api';

export default function ChatInterface() {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState(null);
  const [loading, setLoading] = useState(false);
  const api = new KnowledgeAssistantAPI();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await api.askQuestion(question);
      setAnswer(response);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <form onSubmit={handleSubmit} className="mb-6">
        <div className="flex gap-2">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question..."
            className="flex-1 px-4 py-2 border rounded-lg"
          />
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg"
          >
            {loading ? 'Thinking...' : 'Ask'}
          </button>
        </div>
      </form>

      {answer && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-bold text-lg mb-2">Answer:</h3>
          <p className="mb-4">{answer.answer}</p>
          
          <div className="border-t pt-4">
            <h4 className="font-semibold mb-2">Sources:</h4>
            {answer.sources.map((source, idx) => (
              <div key={idx} className="bg-gray-50 p-3 rounded mb-2">
                <p className="text-sm font-medium">{source.title}</p>
                <p className="text-xs text-gray-600">{source.chunk}</p>
                <span className="text-xs text-blue-600">
                  Relevance: {(source.score * 100).toFixed(0)}%
                </span>
              </div>
            ))}
          </div>
          
          <div className="text-sm text-gray-500 mt-4">
            Confidence: {(answer.confidence * 100).toFixed(0)}% | 
            Tokens: {answer.tokens_used}
          </div>
        </div>
      )}
    </div>
  );
}
```

### **Vue.js Example**

```vue
<!-- components/KnowledgeChat.vue -->
<template>
  <div class="knowledge-chat">
    <form @submit.prevent="askQuestion">
      <input
        v-model="question"
        placeholder="Ask a question..."
        class="question-input"
      />
      <button type="submit" :disabled="loading">
        {{ loading ? 'Thinking...' : 'Ask' }}
      </button>
    </form>

    <div v-if="answer" class="answer-card">
      <h3>Answer:</h3>
      <p>{{ answer.answer }}</p>
      
      <div class="sources">
        <h4>Sources:</h4>
        <div
          v-for="(source, idx) in answer.sources"
          :key="idx"
          class="source-item"
        >
          <strong>{{ source.title }}</strong>
          <p>{{ source.chunk }}</p>
          <span>Relevance: {{ (source.score * 100).toFixed(0) }}%</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const question = ref('');
const answer = ref(null);
const loading = ref(false);
const token = localStorage.getItem('token');

const askQuestion = async () => {
  loading.value = true;
  try {
    const response = await fetch('http://localhost:8000/api/v1/query/ask', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        question: question.value,
        collection_name: 'Documents',
      }),
    });
    answer.value = await response.json();
  } catch (error) {
    console.error('Error:', error);
  } finally {
    loading.value = false;
  }
};
</script>
```

### **Vanilla JavaScript Example**

```javascript
// Simple HTML + JavaScript implementation
class KnowledgeAssistant {
  constructor(apiBase = 'http://localhost:8000/api/v1') {
    this.apiBase = apiBase;
    this.token = localStorage.getItem('token');
  }

  async login(username, password) {
    const response = await fetch(`${this.apiBase}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    const data = await response.json();
    this.token = data.access_token;
    localStorage.setItem('token', data.access_token);
    return data;
  }

  async askQuestion(question) {
    const response = await fetch(`${this.apiBase}/query/ask`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        question,
        collection_name: 'Documents',
      }),
    });
    return response.json();
  }
}

// Usage
const assistant = new KnowledgeAssistant();

document.getElementById('askBtn').addEventListener('click', async () => {
  const question = document.getElementById('question').value;
  const answer = await assistant.askQuestion(question);
  
  document.getElementById('answer').innerHTML = `
    <h3>Answer:</h3>
    <p>${answer.answer}</p>
    <div class="sources">
      ${answer.sources.map(s => `
        <div class="source">
          <strong>${s.title}</strong>
          <p>${s.chunk}</p>
        </div>
      `).join('')}
    </div>
  `;
});
```

### **Python Client Example**

```python
# client.py - Python SDK for the Knowledge Assistant
import requests
from typing import Optional, List, Dict

class KnowledgeAssistantClient:
    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        self.base_url = base_url
        self.token: Optional[str] = None
    
    def login(self, username: str, password: str) -> Dict:
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={"username": username, "password": password}
        )
        data = response.json()
        self.token = data["access_token"]
        return data
    
    def upload_document(
        self,
        file_path: str,
        title: str,
        department: str,
        access_level: str = "department"
    ) -> Dict:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {
                'title': title,
                'department': department,
                'access_level': access_level
            }
            response = requests.post(
                f"{self.base_url}/query/upload",
                headers={"Authorization": f"Bearer {self.token}"},
                files=files,
                data=data
            )
        return response.json()
    
    def ask_question(self, question: str) -> Dict:
        response = requests.post(
            f"{self.base_url}/query/ask",
            headers={"Authorization": f"Bearer {self.token}"},
            json={"question": question, "collection_name": "Documents"}
        )
        return response.json()
    
    def get_documents(self) -> List[Dict]:
        response = requests.get(
            f"{self.base_url}/query/documents",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        return response.json()

# Usage
client = KnowledgeAssistantClient()
client.login("john_doe", "password123")

# Upload document
client.upload_document(
    file_path="./company_policy.pdf",
    title="Company Policy",
    department="HR"
)

# Ask question
answer = client.ask_question("What is the vacation policy?")
print(f"Answer: {answer['answer']}")
print(f"Confidence: {answer['confidence']}")
```

### **Mobile App (React Native)**

```typescript
// services/KnowledgeAssistantService.ts
import AsyncStorage from '@react-native-async-storage/async-storage';

export class KnowledgeAssistantService {
  private baseUrl = 'http://localhost:8000/api/v1';
  private token: string | null = null;

  async login(username: string, password: string) {
    const response = await fetch(`${this.baseUrl}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    const data = await response.json();
    this.token = data.access_token;
    await AsyncStorage.setItem('token', data.access_token);
    return data;
  }

  async askQuestion(question: string) {
    const response = await fetch(`${this.baseUrl}/query/ask`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        question,
        collection_name: 'Documents',
      }),
    });
    return response.json();
  }
}

// screens/ChatScreen.tsx
import React, { useState } from 'react';
import { View, TextInput, Button, Text, ScrollView } from 'react-native';

export default function ChatScreen() {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState(null);
  const service = new KnowledgeAssistantService();

  const handleAsk = async () => {
    const response = await service.askQuestion(question);
    setAnswer(response);
  };

  return (
    <View style={{ flex: 1, padding: 20 }}>
      <TextInput
        value={question}
        onChangeText={setQuestion}
        placeholder="Ask a question..."
        style={{ borderWidth: 1, padding: 10, marginBottom: 10 }}
      />
      <Button title="Ask" onPress={handleAsk} />
      
      {answer && (
        <ScrollView style={{ marginTop: 20 }}>
          <Text style={{ fontSize: 18, fontWeight: 'bold' }}>Answer:</Text>
          <Text>{answer.answer}</Text>
          
          <Text style={{ marginTop: 10, fontWeight: 'bold' }}>Sources:</Text>
          {answer.sources.map((source, idx) => (
            <View key={idx} style={{ padding: 10, backgroundColor: '#f0f0f0', marginTop: 5 }}>
              <Text style={{ fontWeight: 'bold' }}>{source.title}</Text>
              <Text>{source.chunk}</Text>
            </View>
          ))}
        </ScrollView>
      )}
    </View>
  );
}
```

### **CORS Configuration**

For frontend integration, ensure CORS is properly configured in your FastAPI app:

```python
# src/app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Your frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🔒 Access Control

The system implements three-tier access control:

| Role | Permissions |
|------|-------------|
| **Admin** | Full access to all documents, can delete documents |
| **User** | Access to public documents + own department documents, can upload |
| **Viewer** | Read-only access to public documents only |

### Access Levels

- **Public**: Accessible to all users
- **Department**: Accessible only to users in the same department
- **Restricted**: Accessible only to admins

## 🛠️ Development

### Running the Application

There are multiple ways to run the application:

```bash
# 1. Direct execution (simplest)
python asgi.py

# 2. Using uv
uv run python asgi.py

# 3. Using uvicorn directly
uvicorn asgi:app --reload

# 4. Using Docker
docker-compose up --build
```

### Code Quality Tools

```bash
# Format code with Black
uv run black src/

# Lint with Ruff
uv run ruff check src/

# Fix linting issues automatically
uv run ruff check --fix src/

# Type checking with mypy
uv run mypy src/

# Run tests
uv run pytest
```

### Project Commands with uv

```bash
# Sync dependencies (install from pyproject.toml)
uv sync

# Add a new dependency
uv add package-name

# Add a dev dependency
uv add --dev package-name

# Update dependencies
uv lock --upgrade

# Create/activate virtual environment
uv venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

## 🧪 Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app --cov-report=html

# Run specific test file
uv run pytest src/tests/test_rag_service.py
```

## 📊 Monitoring & Logging

Logs are structured with timestamps and severity levels:

```text
2024-11-06 15:30:45 - app.services.rag_service - INFO - Processing query from user john_doe
2024-11-06 15:30:46 - app.adapters.weaviate_adapter - INFO - Found 5 relevant documents
2024-11-06 15:30:47 - app.services.rag_service - INFO - Successfully processed query
```

Configure log level via environment variable:

```bash
LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## 🔧 Configuration

All configuration is managed via environment variables (see `.env.example`):

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | Required |
| `POSTGRES_HOST` | PostgreSQL host | localhost |
| `WEAVIATE_HOST` | Weaviate host | localhost |
| `SECRET_KEY` | JWT secret key | Change in production! |
| `CHUNK_SIZE` | Document chunk size | 1000 |
| `TOP_K_RESULTS` | Number of results to retrieve | 5 |
| `SIMILARITY_THRESHOLD` | Minimum similarity score | 0.7 |

## 🐳 Docker Deployment

### Development with Docker Compose

```bash
# Build and start all services
docker-compose up --build

# Rebuild only the API service
docker-compose up --build api

# View logs
docker-compose logs -f api

# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

### Production Build

```bash
# Build production image
docker build -t ai-knowledge-assistant:latest .

# Run with environment file
docker run -d \
  --name ai-knowledge-assistant \
  --env-file .env \
  -p 8000:8000 \
  ai-knowledge-assistant:latest
```

### Troubleshooting Docker

```bash
# Check service health
docker-compose ps

# Restart a specific service
docker-compose restart api

# View PostgreSQL logs
docker-compose logs postgres

# View Weaviate logs
docker-compose logs weaviate

# Access the API container
docker-compose exec api bash
```

## 👨‍💻 Development

For local development without Docker:

### Development Prerequisites

- Python 3.13+
- PostgreSQL 15+ (or use Docker for databases only)
- Weaviate Vector Database (or use Docker for databases only)
- [uv](https://github.com/astral-sh/uv) package manager

### Setup Development Environment

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh  # Linux/Mac
# or
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"  # Windows

# Install dependencies
uv sync

# Start only databases with Docker
docker-compose up -d postgres weaviate

# Run the application locally
uv run asgi.py

# Or with hot reload
uv run uvicorn asgi:app --reload
```

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run unit tests only
make test-unit

# Run integration tests only
make test-integration

# Run tests in parallel
make test-fast

# Format code
make format

# Lint code
make lint
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Standards

- Follow SOLID principles
- Write comprehensive docstrings
- Add type hints to all functions
- Maintain test coverage above 80%
- Use Ruff for formatting and linting
- All tests must pass before merging

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **FastAPI** - Modern, fast web framework
- **Weaviate** - Vector database for semantic search
- **Google Gemini** - State-of-the-art LLM
- **PostgreSQL** - Reliable relational database
- **uv** - Fast Python package manager
