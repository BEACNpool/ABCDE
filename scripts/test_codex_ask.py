import json
import unittest
from unittest.mock import patch
import ask

class AskTests(unittest.TestCase):
    def test_sql_is_local_and_answer_needs_evidence(self):
        actions = iter([
            {"action":"answer", "sql":"", "answer":"invented"},
            {"action":"run_sql", "sql":"SELECT 1", "answer":""},
            {"action":"answer", "sql":"", "answer":"1"},
        ])
        def infer(*args, **kwargs):
            return json.dumps(next(actions))
        with patch.object(ask, "run_select", return_value={"columns":["1"], "rows":[[1]]}) as select:
            self.assertEqual(ask.answer(infer, "test", "schema", "question"), "1")
            select.assert_called_once_with("SELECT 1", max_rows=ask.MAX_ROWS)

    def test_writes_are_rejected_before_database_access(self):
        self.assertIn("rejected", ask._do_run_sql("DROP TABLE seeds"))

    def test_unknown_action_fails_closed(self):
        def infer(*args, **kwargs):
            return '{"action":"shell", "sql":"", "answer":""}'
        with self.assertRaisesRegex(RuntimeError, "unsupported"):
            ask.answer(infer, "test", "schema", "question")

if __name__ == "__main__":
    unittest.main()
