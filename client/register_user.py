"""
Quick user registration script.

Usage:
    python register_user.py
"""

from client import APIError, AuthenticationError, KnowledgeAssistantClient


def main():
    """Register a new user."""
    print("=" * 70)
    print("  USER REGISTRATION")
    print("=" * 70)

    client = KnowledgeAssistantClient()

    # Get user input
    print("\nEnter user details:")
    username = input("Username: ").strip()
    email = input("Email: ").strip()
    password = input("Password (min 8 characters): ").strip()
    department = input("Department: ").strip()
    role = input("Role (user/admin) [user]: ").strip() or "user"

    # Validate password length
    if len(password) < 8:
        print("\n✗ Password must be at least 8 characters long")
        return 1

    try:
        # Register user
        result = client.register(
            username=username,
            email=email,
            password=password,
            department=department,
            role=role,
        )

        print("\n✓ User registered successfully!")
        print(f"  - Username: {result.get('username')}")
        print(f"  - Email: {result.get('email')}")
        print(f"  - Role: {result.get('role')}")
        print(f"  - Department: {result.get('department')}")
        print("\nYou can now login with:")
        print(f"  Username: {username}")
        print(f"  Password: {password}")

        return 0

    except AuthenticationError as e:
        print(f"\n✗ Registration failed: {e}")
        print("\nPossible reasons:")
        print("  - Username already exists")
        print("  - Email already registered")
        print("  - Invalid credentials format")
        return 1

    except APIError as e:
        print(f"\n✗ API error: {e}")
        return 1

    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
