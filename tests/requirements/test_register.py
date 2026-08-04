"""The register's own integrity, and its agreement with the architecture.

A register that points at a test which does not exist, or allocates to a
subsystem nobody declared, is worse than no register: it reads as coverage.
These tests are what let every other test's docstring be believed.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

import pytest
from conftest import REPO_ROOT

LEVELS = ("L0", "L1", "L2", "L3")
COMPARATORS = ("at_most", "at_least", "equals", "between")

#: The fields the Osseus register parser refuses an entry without. Kept here so
#: this repository fails first, on a diff, rather than at ingest time.
REQUIRED_FIELDS = ("id", "statement", "limit", "unit", "measured_source", "basis")


def _test_functions_in(path: Path) -> set[str]:
    """Test function names defined in a module, by AST rather than by import."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return {
        node.name
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
    }


def test_every_entry_carries_the_fields_the_parser_requires(
    register: dict[str, Any],
) -> None:
    entries = register["requirements"]
    seen: set[str] = set()

    for index, entry in enumerate(entries):
        identifier = entry.get("id", f"requirements[{index}]")

        missing = [field for field in REQUIRED_FIELDS if not entry.get(field)]
        assert not missing, f"{identifier} is missing: {', '.join(missing)}"

        # A limit of zero would read as absent to the parser's truthiness check,
        # so counts are stated positively ("53 cables conform") rather than as
        # a violation count that ought to be zero.
        assert isinstance(entry["limit"], (int, float)) and not isinstance(
            entry["limit"], bool
        ), f"{identifier} has a non-numeric limit {entry['limit']!r}"

        assert entry.get("level") in LEVELS, f"{identifier} has level {entry.get('level')!r}"
        assert entry.get("comparator") in COMPARATORS, (
            f"{identifier} has comparator {entry.get('comparator')!r}"
        )

        assert identifier not in seen, f"duplicate requirement id {identifier}"
        seen.add(identifier)

    assert len(entries) >= 30, f"the register holds {len(entries)} entries, expected at least 30"
    assert set(entry["level"] for entry in entries) == set(LEVELS), (
        "the register must decompose across all four levels"
    )


def test_every_parent_resolves_and_climbs_exactly_one_level(
    register: dict[str, Any],
) -> None:
    """Decomposition runs L0 to L1 to L2 to L3, or stays inside a level.

    A parent two levels up hides a missing requirement, so the register either
    names the intermediate one or admits the entry has no parent — which is
    what REQ-L3-IMU-TEMPERATURE-MIN does.
    """
    by_id = {entry["id"]: entry for entry in register["requirements"]}

    for entry in register["requirements"]:
        parent_id = entry.get("parent")
        if parent_id is None:
            continue
        assert parent_id in by_id, f"{entry['id']} names unknown parent {parent_id}"

        child_level = LEVELS.index(entry["level"])
        parent_level = LEVELS.index(by_id[parent_id]["level"])
        assert 0 <= child_level - parent_level <= 1, (
            f"{entry['id']} ({entry['level']}) derives from {parent_id}"
            f" ({by_id[parent_id]['level']}), skipping a level"
        )


def test_every_allocation_names_a_declared_subsystem_or_function(
    register: dict[str, Any], architecture: dict[str, Any]
) -> None:
    """Allocations resolve against system-architecture.yaml, and it against itself."""
    subsystems = {subsystem["id"] for subsystem in architecture["subsystems"]}
    functions = {function["id"] for function in architecture["functions"]}
    safety = {function["id"] for function in architecture["safety_functions"]}
    known = {architecture["system"]["id"]} | subsystems | functions | safety

    unresolved = sorted(
        {
            target
            for entry in register["requirements"]
            for target in entry.get("allocated_to") or ()
            if target not in known
        }
    )
    assert not unresolved, f"allocations naming nothing in the architecture: {unresolved}"

    assert set(architecture["system"]["contains"]) == subsystems, (
        "the system's contains list and the subsystem list disagree"
    )

    dangling = sorted(
        {
            target
            for function in architecture["functions"] + architecture["safety_functions"]
            for target in function.get("allocated_to") or ()
            if target not in known
        }
    )
    assert not dangling, f"functions allocated to nothing declared: {dangling}"


def test_every_constrains_entry_names_something_this_repository_has(
    register: dict[str, Any], architecture: dict[str, Any]
) -> None:
    """`constrains` resolves against a real file or a declared subsystem.

    The field says which rolled-up number a limit is compared against, written
    `<subject>@<property>:<aggregation>`. Its whole value is that the subject
    is a thing this repository publishes, so a subject naming a file that does
    not exist, or a subsystem the architecture never declares, would read
    downstream as a requirement with no number rather than as a typo here —
    and the fix would be in a different repository from the symptom. Same rule
    as `test_every_allocation_names_a_declared_subsystem_or_function`: this
    repository fails first, on a diff.
    """
    subsystems = {subsystem["id"] for subsystem in architecture["subsystems"]}
    functions = {function["id"] for function in architecture["functions"]}
    safety = {function["id"] for function in architecture["safety_functions"]}
    declared = {architecture["system"]["id"]} | subsystems | functions | safety

    for entry in register["requirements"]:
        stated = entry.get("constrains")
        if stated is None:
            continue
        identifier = entry["id"]
        subject, separator, budget = str(stated).rpartition("@")
        assert separator and subject, (
            f"{identifier} states constrains {stated!r};"
            " the shape is subject@property:aggregation"
        )
        prop, separator, aggregation = budget.partition(":")
        assert separator and prop and aggregation, (
            f"{identifier} states budget {budget!r}, which is not property:aggregation"
        )
        if subject in declared:
            continue
        assert (REPO_ROOT / subject).is_file(), (
            f"{identifier} constrains {subject!r}, which is neither a subsystem"
            " system-architecture.yaml declares nor a file in this repository"
        )


def test_every_in_repo_verifying_test_exists(register: dict[str, Any]) -> None:
    """`verifies` points at real test functions in this repository.

    Entries naming a test in asimovinc/asimov-mjlab are repo-qualified and
    skipped here — that fork runs its own suite, and a cross-repo import would
    make this one unrunnable rather than honest.
    """
    here = Path(__file__).parent
    defined: dict[str, set[str]] = {
        f"tests/requirements/{path.name}": _test_functions_in(path)
        for path in sorted(here.glob("test_*.py"))
    }

    missing: list[str] = []
    for entry in register["requirements"]:
        for node_id in entry.get("verifies") or ():
            if ":" in node_id.split("::")[0]:
                continue
            module, _, function = node_id.partition("::")
            if module not in defined or function not in defined[module]:
                missing.append(f"{entry['id']} -> {node_id}")

    assert not missing, f"register names tests that do not exist: {missing}"


@pytest.mark.parametrize(
    "requirement_id",
    [
        "REQ-L0-HEIGHT",
        "REQ-L0-KIT-COST",
        "REQ-L0-PAYLOAD-CURL",
        "REQ-L1-CAN-BITRATE",
        "REQ-L3-CM5-AVAILABILITY",
        "REQ-L3-IMU-TEMPERATURE-MIN",
    ],
)
def test_unverified_requirements_stay_declared_rather_than_disappearing(
    register: dict[str, Any], requirement_id: str
) -> None:
    """The six requirements nothing can check must keep saying so.

    Each of these has a real limit and no actual to compare it against. The
    failure mode this guards is not a regression in the robot, it is someone
    quietly deleting the uncomfortable rows so the register looks complete.
    """
    by_id = {entry["id"]: entry for entry in register["requirements"]}
    assert requirement_id in by_id, (
        f"{requirement_id} was removed from the register; an unverifiable requirement"
        " is deleted by meeting it or by superseding it, not by dropping the row"
    )
    assert not by_id[requirement_id].get("verifies"), (
        f"{requirement_id} now names a verifying test; move it out of this list"
    )
