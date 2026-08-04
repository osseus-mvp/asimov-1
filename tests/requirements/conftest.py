"""Shared fixtures for the requirement tests.

Every test in this directory verifies a numbered entry in requirements.yaml,
and every one of them reads an artifact this repository already publishes —
the fabrication manifest, the wiring harness, the device tree overlay, the
MuJoCo model. Nothing here re-derives a value; the tests compare what the
artifacts say against what the register promises.

The MJCF is read with ElementTree rather than MuJoCo on purpose: these tests
assert what the model file declares, not what a compiled simulation does, so
they need no simulator and CI needs no wheel for one.
"""

from __future__ import annotations

import json
import xml.etree.ElementTree as ElementTree
from pathlib import Path
from typing import Any

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]

MANIFEST_PATH = REPO_ROOT / "mechanical" / "FABRICATION_MANIFEST.json"
WIRING_PATH = REPO_ROOT / "electrical" / "wiring" / "wiring.yaml"
DEVICE_TREE_PATH = REPO_ROOT / "electrical" / "motion_control" / "mcb-io.dts"
SIM_MODEL_PATH = REPO_ROOT / "sim-model" / "xmls" / "asimov.xml"
REGISTER_PATH = REPO_ROOT / "tests" / "requirements" / "requirements.yaml"
ARCHITECTURE_PATH = REPO_ROOT / "tests" / "requirements" / "system-architecture.yaml"

#: Substring identifying the two passive toe joints. README.md states
#: "25 actuated + 2 passive" and "Legs | 6 DOF x 2 + toe x 2", so the toes are
#: the passive pair and everything else named in the model is actuated.
PASSIVE_JOINT_MARKER = "toe"


@pytest.fixture(scope="session")
def manifest() -> dict[str, Any]:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def wiring() -> dict[str, Any]:
    return yaml.safe_load(WIRING_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def device_tree() -> str:
    return DEVICE_TREE_PATH.read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def sim_model() -> ElementTree.Element:
    return ElementTree.parse(SIM_MODEL_PATH).getroot()


@pytest.fixture(scope="session")
def register() -> dict[str, Any]:
    return yaml.safe_load(REGISTER_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def architecture() -> dict[str, Any]:
    return yaml.safe_load(ARCHITECTURE_PATH.read_text(encoding="utf-8"))


def named_joints(model: ElementTree.Element) -> list[str]:
    """Joint names declared in the model, in document order.

    Joints inside the `default` block carry no name and are class defaults
    rather than degrees of freedom, so the name filter is what separates the
    two.
    """
    return [joint.get("name", "") for joint in model.iter("joint") if joint.get("name")]


def actuated_joints(model: ElementTree.Element) -> list[str]:
    return [name for name in named_joints(model) if PASSIVE_JOINT_MARKER not in name]


def passive_joints(model: ElementTree.Element) -> list[str]:
    return [name for name in named_joints(model) if PASSIVE_JOINT_MARKER in name]


def requirement(register_document: dict[str, Any], requirement_id: str) -> dict[str, Any]:
    """The register entry with this id, or a failure naming the missing id.

    Tests read their limit from the register rather than restating it, so a
    limit can only be changed in one place and a test can never silently
    disagree with the requirement it claims to verify.
    """
    for entry in register_document["requirements"]:
        if entry["id"] == requirement_id:
            return entry
    raise AssertionError(f"{requirement_id} is not in tests/requirements/requirements.yaml")
