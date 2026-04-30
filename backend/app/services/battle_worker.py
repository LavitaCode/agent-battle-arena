"""Small in-process worker for queued public alpha battles."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from queue import Empty, Queue
from threading import Thread
from typing import Callable


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


@dataclass(frozen=True)
class BattleJob:
    """Queued battle execution request."""

    battle_id: str
    attempt: int = 1


class InProcessBattleWorker:
    """Run battle jobs from a simple FIFO queue."""

    def __init__(
        self,
        handler: Callable[[str], None],
        *,
        auto_start: bool = True,
        max_attempts: int = 2,
    ) -> None:
        self._handler = handler
        self._queue: Queue[BattleJob] = Queue()
        self._max_attempts = max(1, max_attempts)
        self._thread: Thread | None = None
        if auto_start:
            self.start()

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._thread = Thread(target=self._run_forever, daemon=True)
        self._thread.start()

    def enqueue(self, battle_id: str) -> None:
        logger.info("battle_job_queued", extra={"battle_id": battle_id})
        self._queue.put(BattleJob(battle_id=battle_id))

    def pending_count(self) -> int:
        return self._queue.qsize()

    def run_next(self) -> bool:
        try:
            job = self._queue.get_nowait()
        except Empty:
            return False
        try:
            logger.info(
                "battle_job_started",
                extra={"battle_id": job.battle_id, "attempt": job.attempt},
            )
            self._handler(job.battle_id)
            logger.info(
                "battle_job_completed",
                extra={"battle_id": job.battle_id, "attempt": job.attempt},
            )
        except Exception:
            logger.exception(
                "battle_job_failed",
                extra={"battle_id": job.battle_id, "attempt": job.attempt},
            )
            if job.attempt < self._max_attempts:
                self._queue.put(BattleJob(battle_id=job.battle_id, attempt=job.attempt + 1))
        finally:
            self._queue.task_done()
        return True

    def _run_forever(self) -> None:
        while True:
            job = self._queue.get()
            try:
                logger.info(
                    "battle_job_started",
                    extra={"battle_id": job.battle_id, "attempt": job.attempt},
                )
                self._handler(job.battle_id)
                logger.info(
                    "battle_job_completed",
                    extra={"battle_id": job.battle_id, "attempt": job.attempt},
                )
            except Exception:
                logger.exception(
                    "battle_job_failed",
                    extra={"battle_id": job.battle_id, "attempt": job.attempt},
                )
                if job.attempt < self._max_attempts:
                    self._queue.put(BattleJob(battle_id=job.battle_id, attempt=job.attempt + 1))
            finally:
                self._queue.task_done()
