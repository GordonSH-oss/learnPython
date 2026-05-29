"""A small asyncio worker pipeline.

Run:
    python 11-concurrency/asyncio_pipeline.py
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
import time


@dataclass(frozen=True)
class Job:
    job_id: int
    delay: float


async def fetch(job: Job) -> str:
    async with asyncio.timeout(1.0):
        await asyncio.sleep(job.delay)
        return f"job-{job.job_id}: done after {job.delay:.1f}s"


async def worker(name: str, queue: asyncio.Queue[Job]) -> None:
    while True:
        job = await queue.get()
        try:
            try:
                result = await fetch(job)
                print(f"{name} -> {result}")
            except TimeoutError:
                print(f"{name} -> job-{job.job_id}: timeout")
        finally:
            queue.task_done()


async def run_pipeline(jobs: list[Job], worker_count: int = 2) -> None:
    queue: asyncio.Queue[Job] = asyncio.Queue()
    workers = [asyncio.create_task(worker(f"worker-{i}", queue)) for i in range(worker_count)]

    for job in jobs:
        await queue.put(job)

    await queue.join()

    for task in workers:
        task.cancel()
    await asyncio.gather(*workers, return_exceptions=True)


def main() -> None:
    jobs = [Job(1, 0.2), Job(2, 0.8), Job(3, 1.4), Job(4, 0.1)]
    start = time.perf_counter()
    asyncio.run(run_pipeline(jobs))
    print(f"elapsed: {time.perf_counter() - start:.2f}s")


if __name__ == "__main__":
    main()
