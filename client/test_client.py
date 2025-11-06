"""
Test script for the Knowledge Assistant Client.

This script demonstrates how to use the Python client to interact with
the AI Knowledge Assistant API. It includes examples of all major operations.

Usage:
    python test_client.py
"""

import sys

from client import (
    APIError,
    AuthenticationError,
    KnowledgeAssistantClient,
)


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print("=" * 70)


def test_authentication(client: KnowledgeAssistantClient):
    """Test authentication operations."""
    print_section("AUTHENTICATION TESTS")

    try:
        # Test health check
        print("\n1. Checking API health...")
        health = client.health_check()
        print(f"   ✓ API Status: {health.get('status', 'unknown')}")

        # Test login
        print("\n2. Logging in...")
        login_response = client.login("test_user", "SecurePass123!")
        print("   ✓ Login successful")
        print(f"   - Token type: {login_response.get('token_type')}")
        print(f"   - Expires in: {login_response.get('expires_in')} seconds")

        # Test get current user
        print("\n3. Getting current user info...")
        user = client.get_current_user()
        print(f"   ✓ Current user: {user.get('username')}")
        print(f"   - Role: {user.get('role')}")
        print(f"   - Department: {user.get('department')}")
        print(f"   - User ID: {user.get('user_id')}")

        return True

    except AuthenticationError as e:
        print(f"   ✗ Authentication failed: {e}")
        print("\n   Note: Make sure you have registered a user first:")
        print("   - Username: test_user")
        print("   - Password: SecurePass123!")
        print("   - Department: Engineering")
        return False
    except APIError as e:
        print(f"   ✗ API error: {e}")
        return False


def test_document_operations(client: KnowledgeAssistantClient):
    """Test document management operations."""
    print_section("DOCUMENT MANAGEMENT TESTS")

    try:
        # Test get documents
        print("\n1. Fetching accessible documents...")
        documents = client.get_documents(limit=10)
        print(f"   ✓ Found {len(documents)} documents")

        if documents:
            print("\n   Sample documents:")
            for i, doc in enumerate(documents[:3], 1):
                print(f"   {i}. {doc.get('title')} (ID: {doc.get('id')})")
                print(f"      - Department: {doc.get('department')}")
                print(f"      - Access: {doc.get('access_level')}")
                print(f"      - Uploaded: {doc.get('created_at', 'N/A')[:10]}")

        # Test upload document (commented out - requires actual file)
        print("\n2. Document upload test (skipped - requires file)")
        print("   To test upload, uncomment the code in test_client.py")
        print("   Example:")
        print("   ```python")
        print("   doc = client.upload_document(")
        print("       file_path='./sample.pdf',")
        print("       title='Sample Document',")
        print("       department='Engineering',")
        print("       access_level='department'")
        print("   )")
        print("   ```")

        return True

    except APIError as e:
        print(f"   ✗ API error: {e}")
        return False


def test_query_operations(client: KnowledgeAssistantClient):
    """Test query and RAG operations."""
    print_section("QUERY & RAG TESTS")

    try:
        # Test ask question
        print("\n1. Asking a question...")
        question = "What is the company vacation policy?"
        print(f"   Question: '{question}'")

        answer = client.ask_question(question)

        print("\n   ✓ Answer received:")
        print(f"   {answer.get('answer', 'No answer')[:200]}...")
        print(f"\n   - Confidence: {answer.get('confidence', 0):.2%}")
        print(f"   - Tokens used: {answer.get('tokens_used', 0)}")
        print(f"   - Sources: {len(answer.get('sources', []))} documents")

        # Display sources
        if answer.get("sources"):
            print("\n   Top sources:")
            for i, source in enumerate(answer["sources"][:2], 1):
                print(f"   {i}. {source.get('title', 'Unknown')}")
                print(f"      Relevance: {source.get('score', 0):.2%}")
                excerpt = source.get("chunk", "")[:100]
                print(f"      Excerpt: {excerpt}...")

        # Test query history
        print("\n2. Fetching query history...")
        history = client.get_query_history(limit=5)
        print(f"   ✓ Found {len(history)} recent queries")

        if history:
            print("\n   Recent queries:")
            for i, query in enumerate(history[:3], 1):
                q_text = query.get("question", "N/A")
                timestamp = query.get("created_at", "N/A")[:19]
                print(f"   {i}. {q_text[:50]}... ({timestamp})")

        return True

    except APIError as e:
        print(f"   ✗ API error: {e}")
        print("   Note: This might fail if no documents are uploaded yet.")
        return False


def test_error_handling(client: KnowledgeAssistantClient):
    """Test error handling."""
    print_section("ERROR HANDLING TESTS")

    try:
        # Test invalid authentication
        print("\n1. Testing invalid authentication...")
        temp_client = KnowledgeAssistantClient()
        try:
            temp_client.get_current_user()
            print("   ✗ Should have raised AuthenticationError")
        except AuthenticationError:
            print("   ✓ Correctly raised AuthenticationError")

        # Test invalid document ID
        print("\n2. Testing invalid document ID...")
        try:
            client.get_document(999999)
            print("   ✗ Should have raised APIError")
        except APIError:
            print("   ✓ Correctly raised APIError for non-existent document")

        # Test invalid file path
        print("\n3. Testing invalid file path...")
        try:
            client.upload_document(
                file_path="./nonexistent.pdf", title="Test", department="Engineering"
            )
            print("   ✗ Should have raised FileNotFoundError")
        except FileNotFoundError:
            print("   ✓ Correctly raised FileNotFoundError")

        return True

    except Exception as e:
        print(f"   ✗ Unexpected error: {e}")
        return False


def run_all_tests():
    """Run all client tests."""
    print("\n" + "=" * 70)
    print("  AI KNOWLEDGE ASSISTANT - PYTHON CLIENT TEST SUITE")
    print("=" * 70)

    # Initialize client
    client = KnowledgeAssistantClient(base_url="http://localhost:8000/api/v1", timeout=30)

    print(f"\nClient initialized: {client}")

    # Run tests
    results = {
        "Authentication": test_authentication(client),
        "Document Operations": test_document_operations(client),
        "Query Operations": test_query_operations(client),
        "Error Handling": test_error_handling(client),
    }

    # Logout
    print_section("CLEANUP")
    client.logout()
    print("   ✓ Logged out successfully")

    # Print summary
    print_section("TEST SUMMARY")
    print()
    passed = sum(1 for result in results.values() if result)
    total = len(results)

    for test_name, result in results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"   {status}: {test_name}")

    print(f"\n   Total: {passed}/{total} tests passed")

    if passed == total:
        print("\n   🎉 All tests passed!")
        return 0
    else:
        print(f"\n   ⚠️  {total - passed} test(s) failed")
        return 1


def interactive_mode():
    """Run client in interactive mode."""
    print("\n" + "=" * 70)
    print("  AI KNOWLEDGE ASSISTANT - INTERACTIVE MODE")
    print("=" * 70)

    client = KnowledgeAssistantClient()

    # Login
    print("\nPlease login to continue:")
    username = input("Username: ").strip()
    password = input("Password: ").strip()

    try:
        client.login(username, password)
        print(f"\n✓ Logged in as {username}")
    except AuthenticationError as e:
        print(f"\n✗ Login failed: {e}")
        return 1

    # Interactive loop
    while True:
        print("\n" + "-" * 70)
        print("What would you like to do?")
        print("1. Ask a question")
        print("2. List documents")
        print("3. View query history")
        print("4. Upload document")
        print("5. Exit")

        choice = input("\nChoice (1-5): ").strip()

        try:
            if choice == "1":
                question = input("\nYour question: ").strip()
                if question:
                    print("\nThinking...")
                    answer = client.ask_question(question)
                    print(f"\nAnswer: {answer.get('answer')}")
                    print(f"Confidence: {answer.get('confidence', 0):.2%}")

            elif choice == "2":
                docs = client.get_documents(limit=20)
                print(f"\nFound {len(docs)} documents:")
                for i, doc in enumerate(docs, 1):
                    print(f"{i}. {doc.get('title')} (ID: {doc.get('id')})")

            elif choice == "3":
                history = client.get_query_history(limit=10)
                print(f"\nQuery history ({len(history)} queries):")
                for i, query in enumerate(history, 1):
                    print(f"{i}. {query.get('question', 'N/A')[:60]}...")

            elif choice == "4":
                file_path = input("\nFile path: ").strip()
                title = input("Title: ").strip()
                department = input("Department: ").strip()

                if file_path and title and department:
                    result = client.upload_document(
                        file_path=file_path, title=title, department=department
                    )
                    print(f"\n✓ Uploaded document ID: {result.get('document_id')}")

            elif choice == "5":
                client.logout()
                print("\n✓ Logged out. Goodbye!")
                break

            else:
                print("\n✗ Invalid choice")

        except (APIError, AuthenticationError) as e:
            print(f"\n✗ Error: {e}")
        except KeyboardInterrupt:
            print("\n\nInterrupted by user")
            break

    return 0


def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        return interactive_mode()
    else:
        return run_all_tests()


if __name__ == "__main__":
    sys.exit(main())
