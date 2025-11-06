"""
Performance Benchmark Script.

Measures embedding and RAG query performance for the AI Knowledge Assistant.
"""

import asyncio
import time
from statistics import mean, median, stdev

import httpx


class PerformanceBenchmark:
    """Benchmark tool for measuring system performance."""

    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        """Initialize benchmark with API base URL."""
        self.base_url = base_url
        self.token = None

    async def login(self, username: str, password: str) -> None:
        """Login and get authentication token."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/auth/login",
                data={"username": username, "password": password},
            )
            response.raise_for_status()
            data = response.json()
            self.token = data["access_token"]
            print(f"✓ Logged in as {username}")

    async def benchmark_query(
        self, question: str, iterations: int = 10
    ) -> dict[str, float]:
        """Benchmark RAG query performance."""
        if not self.token:
            raise ValueError("Must login first")

        times = []
        confidences = []
        source_counts = []

        print(f"\n🔄 Running {iterations} query iterations...")

        async with httpx.AsyncClient(timeout=60.0) as client:
            for i in range(iterations):
                start = time.perf_counter()

                response = await client.post(
                    f"{self.base_url}/query/ask",
                    headers={"Authorization": f"Bearer {self.token}"},
                    json={"question": question},
                )
                response.raise_for_status()

                elapsed = time.perf_counter() - start
                times.append(elapsed)

                data = response.json()
                confidences.append(data.get("confidence", 0))
                source_counts.append(len(data.get("sources", [])))

                print(f"  Iteration {i+1}/{iterations}: {elapsed:.3f}s")

        return {
            "mean_time": mean(times),
            "median_time": median(times),
            "min_time": min(times),
            "max_time": max(times),
            "stdev_time": stdev(times) if len(times) > 1 else 0,
            "mean_confidence": mean(confidences),
            "mean_sources": mean(source_counts),
        }

    async def benchmark_document_upload(
        self, file_path: str, iterations: int = 5
    ) -> dict[str, float]:
        """Benchmark document upload and embedding performance."""
        if not self.token:
            raise ValueError("Must login first")

        times = []

        print(f"\n🔄 Running {iterations} upload iterations...")

        async with httpx.AsyncClient(timeout=120.0) as client:
            for i in range(iterations):
                with open(file_path, "rb") as f:
                    start = time.perf_counter()

                    response = await client.post(
                        f"{self.base_url}/query/upload",
                        headers={"Authorization": f"Bearer {self.token}"},
                        files={"file": f},
                        data={"access_level": "public"},
                    )
                    response.raise_for_status()

                    elapsed = time.perf_counter() - start
                    times.append(elapsed)

                    # Delete the uploaded document for next iteration
                    data = response.json()
                    doc_id = data.get("document_id")
                    if doc_id:
                        await client.delete(
                            f"{self.base_url}/query/documents/{doc_id}",
                            headers={"Authorization": f"Bearer {self.token}"},
                        )

                    print(f"  Iteration {i+1}/{iterations}: {elapsed:.3f}s")

        return {
            "mean_time": mean(times),
            "median_time": median(times),
            "min_time": min(times),
            "max_time": max(times),
            "stdev_time": stdev(times) if len(times) > 1 else 0,
        }

    def print_results(self, title: str, results: dict[str, float]) -> None:
        """Print benchmark results in a formatted table."""
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")

        for key, value in results.items():
            label = key.replace("_", " ").title()
            if "time" in key:
                print(f"  {label:.<40} {value:.3f}s")
            elif "confidence" in key:
                print(f"  {label:.<40} {value:.2%}")
            else:
                print(f"  {label:.<40} {value:.2f}")

        print(f"{'='*60}\n")


async def main():
    """Run performance benchmarks."""
    print("🚀 AI Knowledge Assistant Performance Benchmark\n")

    benchmark = PerformanceBenchmark()

    # Login
    await benchmark.login("sabry", "sabry")

    # Benchmark RAG queries
    query_results = await benchmark.benchmark_query(
        question="What is this document about?",
        iterations=10,
    )
    benchmark.print_results("RAG Query Performance", query_results)

    # Optionally benchmark document upload
    # upload_results = await benchmark.benchmark_document_upload(
    #     file_path="path/to/test.pdf",
    #     iterations=5,
    # )
    # benchmark.print_results("Document Upload Performance", upload_results)

    print("✅ Benchmark complete!")


if __name__ == "__main__":
    asyncio.run(main())
