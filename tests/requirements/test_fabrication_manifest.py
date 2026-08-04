"""Fabrication manifest requirements: REQ-L0-SELF-SOURCE and its L1 children."""

from __future__ import annotations

import subprocess
import sys
from typing import Any

from conftest import REPO_ROOT, requirement


def test_manifest_enumerates_every_fabricated_part(
    manifest: dict[str, Any], register: dict[str, Any]
) -> None:
    """REQ-L0-SELF-SOURCE: at least 170 parts, each with a repo-local STEP file.

    A self-source builder works from this file alone, so an entry that names
    no path, or a declared count that disagrees with the list, is the failure
    that matters — not the round number.
    """
    entry = requirement(register, "REQ-L0-SELF-SOURCE")
    entries = manifest["entries"]

    assert len(entries) >= entry["limit"], (
        f"manifest lists {len(entries)} parts, REQ-L0-SELF-SOURCE requires at least"
        f" {entry['limit']}"
    )
    assert manifest["entry_count"] == len(entries), (
        f"manifest declares entry_count {manifest['entry_count']} but lists"
        f" {len(entries)} entries"
    )

    pathless = [part["part_id"] for part in entries if not part.get("path")]
    assert not pathless, f"manifest entries without a fabrication path: {pathless}"

    missing = [
        part["part_id"] for part in entries if not (REPO_ROOT / part["path"]).exists()
    ]
    assert not missing, f"manifest entries whose STEP file is absent from the tree: {missing}"


def test_manifest_declares_the_seven_cad_subassemblies(
    manifest: dict[str, Any], register: dict[str, Any]
) -> None:
    """REQ-L1-SUBASSEMBLY-COUNT: exactly 7 subassemblies, and no orphan parts.

    The count and the membership are one requirement: seven directories with a
    part filed under an eighth would still be a broken decomposition.
    """
    entry = requirement(register, "REQ-L1-SUBASSEMBLY-COUNT")
    declared = manifest["subassemblies"]

    assert len(declared) == entry["limit"], (
        f"manifest declares {len(declared)} subassemblies {declared},"
        f" REQ-L1-SUBASSEMBLY-COUNT requires exactly {entry['limit']}"
    )

    used = {part["subassembly"] for part in manifest["entries"]}
    assert used == set(declared), (
        f"parts are filed under {sorted(used)} but the manifest declares {sorted(declared)}"
    )


def test_every_part_uses_a_declared_fabrication_class(
    manifest: dict[str, Any], register: dict[str, Any]
) -> None:
    """REQ-L1-FABRICATION-CLASSES: at most 4 processes, all of them documented.

    A part filed under a fifth class is a process the assembly manual does not
    describe, which is a build a self-source customer cannot complete.
    """
    entry = requirement(register, "REQ-L1-FABRICATION-CLASSES")
    declared = manifest["fabrication_classes"]

    assert len(declared) <= entry["limit"], (
        f"manifest declares {len(declared)} fabrication classes {declared},"
        f" REQ-L1-FABRICATION-CLASSES allows at most {entry['limit']}"
    )

    undeclared = sorted(
        {
            part["fabrication_class"]
            for part in manifest["entries"]
            if part["fabrication_class"] not in declared
        }
    )
    assert not undeclared, f"parts use undeclared fabrication classes: {undeclared}"


def test_manifest_regenerates_from_the_cad_tree(
    manifest: dict[str, Any], register: dict[str, Any]
) -> None:
    """REQ-L1-MANIFEST-REPRODUCIBLE: --check reproduces all 170 committed entries.

    The generator and its --check mode are the project's own and predate this
    register. This test binds them to a requirement so the CI evidence lands
    against a numbered promise rather than only against a green tick.
    """
    entry = requirement(register, "REQ-L1-MANIFEST-REPRODUCIBLE")
    assert len(manifest["entries"]) == entry["limit"], (
        f"manifest holds {len(manifest['entries'])} entries,"
        f" REQ-L1-MANIFEST-REPRODUCIBLE requires exactly {entry['limit']}"
    )

    result = subprocess.run(
        [sys.executable, "scripts/generate_fabrication_manifest.py", "--check"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, (
        "regenerating the manifest from the CAD tree does not reproduce the committed"
        f" files:\n{result.stdout}\n{result.stderr}"
    )
