"""Check uploaded documents and their processing status."""

from client import KnowledgeAssistantClient

client = KnowledgeAssistantClient()
client.login("sabry", "12345678")

# Get all documents
docs = client.get_documents()
print(f"\n✓ Found {len(docs)} documents:\n")

for i, doc in enumerate(docs, 1):
    print(f"{i}. {doc.get('title', 'Untitled')}")
    print(f"   ID: {doc.get('id')}")
    print(f"   File Type: {doc.get('file_type')}")
    print(f"   Department: {doc.get('department')}")
    print(f"   Access Level: {doc.get('access_level')}")
    print(f"   Uploaded: {doc.get('created_at', 'N/A')[:19]}")
    print()

# Try a simple question
if docs:
    print("\nAsking a test question...")
    answer = client.ask_question("What is this document about?")
    print(f"\nAnswer: {answer.get('answer')}")
    print(f"Confidence: {answer.get('confidence', 0):.2%}")
    print(f"Sources found: {len(answer.get('sources', []))}")

    if answer.get("sources"):
        print("\nSources:")
        for src in answer["sources"]:
            print(f"  - {src.get('title')}: {src.get('score', 0):.2%} relevance")
