from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "recipe_validator", ROOT / "scripts" / "validate.py"
)
assert SPEC is not None and SPEC.loader is not None
VALIDATOR_MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR_MODULE)


class RecipeValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.validator = VALIDATOR_MODULE.build_validator()
        cls.recipe = VALIDATOR_MODULE.load_document(
            ROOT / "recipes" / "v1" / "com.example.starlight-notes.toml"
        )

    def errors_for(self, recipe: dict) -> list[str]:
        return VALIDATOR_MODULE.validate_document(recipe, self.validator)

    def test_examples_are_valid(self) -> None:
        paths = sorted((ROOT / "recipes" / "v1").glob("*.toml"))
        paths += sorted((ROOT / "recipes" / "v1").glob("*.json"))
        for path in paths:
            with self.subTest(path=path.name):
                self.assertEqual(
                    [], self.errors_for(VALIDATOR_MODULE.load_document(path))
                )

    def test_toml_is_the_catalog_format(self) -> None:
        self.assertTrue(list((ROOT / "recipes" / "v1").glob("*.toml")))
        self.assertFalse(list((ROOT / "recipes" / "v1").glob("*.json")))

    def test_real_installers_are_typed_and_pinned(self) -> None:
        for name in [
            "org.notepad-plus-plus.notepad-plus-plus.toml",
            "org.7-zip.7-zip.toml",
        ]:
            recipe = VALIDATOR_MODULE.load_document(
                ROOT / "recipes" / "v1" / name
            )
            with self.subTest(path=name):
                installer = recipe["install"][0]
                self.assertEqual("run-installer", installer["action"])
                self.assertIn(installer["installerType"], {"exe", "msi"})
                self.assertEqual(64, len(recipe["sources"][0]["sha256"]))

    def test_unknown_action_is_rejected(self) -> None:
        recipe = copy.deepcopy(self.recipe)
        recipe["install"][0] = {"action": "shell", "command": "anything"}
        self.assertTrue(self.errors_for(recipe))

    def test_unknown_properties_are_rejected(self) -> None:
        recipe = copy.deepcopy(self.recipe)
        recipe["runtimeAccess"]["hostRoot"] = True
        self.assertTrue(self.errors_for(recipe))

    def test_insecure_download_is_rejected(self) -> None:
        recipe = copy.deepcopy(self.recipe)
        recipe["sources"][0]["url"] = "http://example.invalid/setup.exe"
        self.assertTrue(self.errors_for(recipe))

    def test_rosetta_is_macos_arm_only(self) -> None:
        recipe = copy.deepcopy(self.recipe)
        recipe["variants"][1]["platform"] = "linux"
        self.assertTrue(self.errors_for(recipe))

    def test_unknown_source_reference_is_rejected(self) -> None:
        recipe = copy.deepcopy(self.recipe)
        recipe["install"][0]["source"] = "missing"
        self.assertIn("unknown source id", " ".join(self.errors_for(recipe)))

    def test_duplicate_target_is_rejected(self) -> None:
        recipe = copy.deepcopy(self.recipe)
        recipe["variants"].append(copy.deepcopy(recipe["variants"][0]))
        self.assertIn("duplicate target", " ".join(self.errors_for(recipe)))


if __name__ == "__main__":
    unittest.main()
