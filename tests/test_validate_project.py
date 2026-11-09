from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("validate_project", ROOT / "scripts" / "validate_project.py")
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class PilotValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.pilot = MODULE.load_json("config/pilot_bunker.json")

    def test_current_manifest_is_valid(self) -> None:
        self.assertEqual(MODULE.validate_pilot(self.pilot), [])

    def test_rejects_publication_in_mvp(self) -> None:
        changed = copy.deepcopy(self.pilot)
        changed["publication_enabled"] = True
        self.assertIn("A publicacao deve permanecer desativada no MVP.", MODULE.validate_pilot(changed))

    def test_rejects_timeline_gap(self) -> None:
        changed = copy.deepcopy(self.pilot)
        changed["timeline"][1]["start"] = 4
        self.assertTrue(any("lacuna" in error for error in MODULE.validate_pilot(changed)))

    def test_pipeline_gates_are_valid(self) -> None:
        pipeline = MODULE.load_json("config/pipeline_fatonauta.json")
        self.assertEqual(MODULE.validate_pipeline(pipeline, self.pilot, list(range(1, 16))), [])

    def test_rejects_bypass_of_publication_authorization(self) -> None:
        pipeline = MODULE.load_json("config/pipeline_fatonauta.json")
        pipeline["states"][10]["next"] = "published"
        errors = MODULE.validate_pipeline(pipeline, self.pilot, list(range(1, 16)))
        self.assertTrue(any("autorizacao" in error for error in errors))

    def test_rejects_pipeline_without_self_review(self) -> None:
        pipeline = MODULE.load_json("config/pipeline_fatonauta.json")
        pipeline["handoff_rule"]["self_review_required"] = False
        errors = MODULE.validate_pipeline(pipeline, self.pilot, list(range(1, 16)))
        self.assertTrue(any("auto-revisao" in error for error in errors))


if __name__ == "__main__":
    unittest.main()

