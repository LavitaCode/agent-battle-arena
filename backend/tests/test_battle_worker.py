"""Tests for the public alpha battle worker."""
import unittest

from backend.app.services.battle_worker import InProcessBattleWorker


class InProcessBattleWorkerTestCase(unittest.TestCase):
    def test_enqueue_keeps_job_pending_until_worker_processes_it(self) -> None:
        executed: list[str] = []
        worker = InProcessBattleWorker(lambda battle_id: executed.append(battle_id), auto_start=False)

        worker.enqueue("battle-123")

        self.assertEqual(worker.pending_count(), 1)
        self.assertEqual(executed, [])

        processed = worker.run_next()

        self.assertTrue(processed)
        self.assertEqual(worker.pending_count(), 0)
        self.assertEqual(executed, ["battle-123"])

    def test_failed_job_retries_once_before_being_dropped(self) -> None:
        attempts: list[str] = []

        def handler(battle_id: str) -> None:
            attempts.append(battle_id)
            raise RuntimeError("boom")

        worker = InProcessBattleWorker(handler, auto_start=False, max_attempts=2)

        worker.enqueue("battle-456")
        first = worker.run_next()
        second = worker.run_next()

        self.assertTrue(first)
        self.assertTrue(second)
        self.assertEqual(worker.pending_count(), 0)
        self.assertEqual(attempts, ["battle-456", "battle-456"])


if __name__ == "__main__":
    unittest.main()
