"""
Python Client for AI Knowledge Assistant.

A comprehensive client library for interacting with the AI Knowledge Assistant API.
Provides easy-to-use methods for authentication, document management, and querying.

Usage:
    from client import KnowledgeAssistantClient

    client = KnowledgeAssistantClient()
    client.login("username", "password")

    # Upload a document
    client.upload_document("./document.pdf", "My Document", "Engineering")

    # Ask a question
    answer = client.ask_question("What is the company policy?")
    print(answer['answer'])
"""

import logging
from pathlib import Path
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class KnowledgeAssistantError(Exception):
    """Base exception for Knowledge Assistant client errors."""

    pass


class AuthenticationError(KnowledgeAssistantError):
    """Raised when authentication fails."""

    pass


class APIError(KnowledgeAssistantError):
    """Raised when API request fails."""

    pass


class KnowledgeAssistantClient:
    """
    Client for interacting with the AI Knowledge Assistant API.

    This client provides a high-level interface for all API operations including
    authentication, document management, and querying the knowledge base.

    Attributes:
        base_url: Base URL of the API
        token: JWT authentication token
        session: Requests session with retry logic
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000/api/v1",
        timeout: int = 30,
        max_retries: int = 3,
    ):
        """
        Initialize the Knowledge Assistant client.

        Args:
            base_url: Base URL of the API (default: http://localhost:8000/api/v1)
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum number of retries for failed requests (default: 3)
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.token: str | None = None

        # Setup session with retry logic
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        logger.info(f"Initialized client with base URL: {self.base_url}")

    def _get_headers(self) -> dict[str, str]:
        """Get headers for API requests."""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _handle_response(self, response: requests.Response) -> dict[str, Any]:
        """
        Handle API response and raise appropriate exceptions.

        Args:
            response: Response object from requests

        Returns:
            Parsed JSON response

        Raises:
            AuthenticationError: If authentication fails
            APIError: If API request fails
        """
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise AuthenticationError("Authentication failed. Please login again.") from e
            elif response.status_code == 403:
                raise AuthenticationError("Access denied. Insufficient permissions.") from e
            else:
                try:
                    error_detail = response.json().get("detail", str(e))
                except ValueError:
                    error_detail = str(e)
                raise APIError(f"API request failed: {error_detail}") from e
        except requests.exceptions.RequestException as e:
            raise APIError(f"Request failed: {str(e)}") from e

    # ========================================================================
    # Authentication Methods
    # ========================================================================

    def register(
        self, username: str, email: str, password: str, department: str, role: str = "user"
    ) -> dict[str, Any]:
        """
        Register a new user.

        Args:
            username: Username for the new user
            email: Email address
            password: Password (min 8 characters)
            department: Department name
            role: User role (default: "user")

        Returns:
            User information

        Raises:
            APIError: If registration fails
        """
        logger.info(f"Registering user: {username}")

        response = self.session.post(
            f"{self.base_url}/auth/register",
            json={
                "username": username,
                "email": email,
                "password": password,
                "department": department,
                "role": role,
            },
            timeout=self.timeout,
        )

        result = self._handle_response(response)
        logger.info(f"Successfully registered user: {username}")
        return result

    def login(self, username: str, password: str) -> dict[str, Any]:
        """
        Login and obtain authentication token.

        Args:
            username: Username
            password: Password

        Returns:
            Authentication response with token

        Raises:
            AuthenticationError: If login fails
        """
        logger.info(f"Logging in user: {username}")

        response = self.session.post(
            f"{self.base_url}/auth/login",
            json={"username": username, "password": password},
            timeout=self.timeout,
        )

        data = self._handle_response(response)
        self.token = data.get("access_token")

        if not self.token:
            raise AuthenticationError("No token received from login")

        logger.info(f"Successfully logged in as: {username}")
        return data

    def get_current_user(self) -> dict[str, Any]:
        """
        Get current authenticated user information.

        Returns:
            User information

        Raises:
            AuthenticationError: If not authenticated
        """
        if not self.token:
            raise AuthenticationError("Not authenticated. Please login first.")

        response = self.session.get(
            f"{self.base_url}/auth/me", headers=self._get_headers(), timeout=self.timeout
        )

        return self._handle_response(response)

    def logout(self):
        """Logout and clear authentication token."""
        self.token = None
        logger.info("Logged out successfully")

    # ========================================================================
    # Document Management Methods
    # ========================================================================

    def upload_document(
        self, file_path: str, title: str, department: str, access_level: str = "department"
    ) -> dict[str, Any]:
        """
        Upload a document to the knowledge base.

        Args:
            file_path: Path to the document file (PDF, TXT, or DOCX)
            title: Document title
            department: Department name
            access_level: Access level ("public", "department", or "restricted")

        Returns:
            Upload response with document ID

        Raises:
            APIError: If upload fails
            FileNotFoundError: If file doesn't exist
        """
        if not self.token:
            raise AuthenticationError("Not authenticated. Please login first.")

        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        logger.info(f"Uploading document: {title} from {file_path}")

        with open(file_path, "rb") as f:
            files = {"file": (file_path_obj.name, f, self._get_mime_type(file_path_obj))}
            data = {"title": title, "department": department, "access_level": access_level}

            headers = {"Authorization": f"Bearer {self.token}"}

            response = self.session.post(
                f"{self.base_url}/query/documents/upload",
                headers=headers,
                files=files,
                data=data,
                timeout=self.timeout * 2,  # Longer timeout for uploads
            )

        result = self._handle_response(response)
        logger.info(f"Successfully uploaded document: {title}")
        return result

    def get_documents(self, skip: int = 0, limit: int = 100) -> list[dict[str, Any]]:
        """
        Get list of accessible documents.

        Args:
            skip: Number of documents to skip (pagination)
            limit: Maximum number of documents to return

        Returns:
            List of documents

        Raises:
            AuthenticationError: If not authenticated
        """
        if not self.token:
            raise AuthenticationError("Not authenticated. Please login first.")

        response = self.session.get(
            f"{self.base_url}/query/documents",
            headers=self._get_headers(),
            params={"skip": skip, "limit": limit},
            timeout=self.timeout,
        )

        result = self._handle_response(response)
        # API returns {"documents": [...], "total": N}, extract the documents list
        return result.get("documents", []) if isinstance(result, dict) else result

    def get_document(self, document_id: int) -> dict[str, Any]:
        """
        Get details of a specific document.

        Args:
            document_id: Document ID

        Returns:
            Document details

        Raises:
            APIError: If document not found or access denied
        """
        if not self.token:
            raise AuthenticationError("Not authenticated. Please login first.")

        response = self.session.get(
            f"{self.base_url}/query/documents/{document_id}",
            headers=self._get_headers(),
            timeout=self.timeout,
        )

        return self._handle_response(response)

    def delete_document(self, document_id: int) -> dict[str, Any]:
        """
        Delete a document.

        Args:
            document_id: Document ID to delete

        Returns:
            Deletion confirmation

        Raises:
            APIError: If deletion fails or access denied
        """
        if not self.token:
            raise AuthenticationError("Not authenticated. Please login first.")

        logger.info(f"Deleting document: {document_id}")

        response = self.session.delete(
            f"{self.base_url}/query/documents/{document_id}",
            headers=self._get_headers(),
            timeout=self.timeout,
        )

        result = self._handle_response(response)
        logger.info(f"Successfully deleted document: {document_id}")
        return result

    # ========================================================================
    # Query Methods
    # ========================================================================

    def ask_question(self, question: str, collection_name: str = "Documents") -> dict[str, Any]:
        """
        Ask a question to the knowledge base.

        Args:
            question: Question to ask
            collection_name: Collection to query (default: "Documents")

        Returns:
            Answer with sources and confidence score

        Raises:
            AuthenticationError: If not authenticated
        """
        if not self.token:
            raise AuthenticationError("Not authenticated. Please login first.")

        logger.info(f"Asking question: {question}")

        response = self.session.post(
            f"{self.base_url}/query/ask",
            headers=self._get_headers(),
            json={"question": question, "collection_name": collection_name},
            timeout=self.timeout * 2,  # Longer timeout for AI generation
        )

        result = self._handle_response(response)
        logger.info(f"Received answer with confidence: {result.get('confidence', 0):.2f}")
        return result

    def get_query_history(self, limit: int = 10) -> list[dict[str, Any]]:
        """
        Get query history for the current user.

        Args:
            limit: Maximum number of queries to return

        Returns:
            List of previous queries and answers

        Raises:
            AuthenticationError: If not authenticated
        """
        if not self.token:
            raise AuthenticationError("Not authenticated. Please login first.")

        response = self.session.get(
            f"{self.base_url}/query/history",
            headers=self._get_headers(),
            params={"limit": limit},
            timeout=self.timeout,
        )

        return self._handle_response(response)

    # ========================================================================
    # Utility Methods
    # ========================================================================

    def health_check(self) -> dict[str, Any]:
        """
        Check API health status.

        Returns:
            Health status information
        """
        response = self.session.get(
            f"{self.base_url.replace('/api/v1', '')}/health", timeout=self.timeout
        )
        return self._handle_response(response)

    @staticmethod
    def _get_mime_type(file_path: Path) -> str:
        """Get MIME type for file."""
        suffix = file_path.suffix.lower()
        mime_types = {
            ".pdf": "application/pdf",
            ".txt": "text/plain",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".doc": "application/msword",
        }
        return mime_types.get(suffix, "application/octet-stream")

    def __repr__(self) -> str:
        """String representation of the client."""
        auth_status = "authenticated" if self.token else "not authenticated"
        return f"KnowledgeAssistantClient(base_url='{self.base_url}', {auth_status})"


# ========================================================================
# Example Usage
# ========================================================================


def main():
    """Example usage of the Knowledge Assistant client."""

    # Initialize client
    client = KnowledgeAssistantClient()

    try:
        # Check API health
        health = client.health_check()
        print(f"✓ API Health: {health}")

        # Register a new user (optional)
        # client.register(
        #     username="test_user",
        #     email="test@example.com",
        #     password="SecurePass123!",
        #     department="Engineering"
        # )

        # Login
        login_response = client.login("test_user", "SecurePass123!")
        print("✓ Logged in successfully")
        print(f"  Token expires in: {login_response.get('expires_in')} seconds")

        # Get current user info
        user = client.get_current_user()
        print(f"✓ Current user: {user.get('username')} ({user.get('role')})")

        # Upload a document
        # doc = client.upload_document(
        #     file_path="./sample_document.pdf",
        #     title="Sample Document",
        #     department="Engineering",
        #     access_level="department"
        # )
        # print(f"✓ Uploaded document: {doc.get('document_id')}")

        # Get all documents
        documents = client.get_documents(limit=10)
        print(f"✓ Found {len(documents)} documents")

        # Ask a question
        answer = client.ask_question("What is the company vacation policy?")
        print("\n✓ Question: What is the company vacation policy?")
        print(f"  Answer: {answer.get('answer')}")
        print(f"  Confidence: {answer.get('confidence', 0):.2%}")
        print(f"  Sources: {len(answer.get('sources', []))} documents")

        # Get query history
        history = client.get_query_history(limit=5)
        print(f"\n✓ Query history: {len(history)} recent queries")

        # Logout
        client.logout()
        print("\n✓ Logged out successfully")

    except AuthenticationError as e:
        print(f"✗ Authentication error: {e}")
    except APIError as e:
        print(f"✗ API error: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


if __name__ == "__main__":
    main()
