"""Simulation model requirements: REQ-L0-MASS, REQ-L0-DOF and their L1 children."""

from __future__ import annotations

import xml.etree.ElementTree as ElementTree
from typing import Any

from conftest import actuated_joints, named_joints, requirement


def _link_masses(model: ElementTree.Element) -> list[float]:
    return [
        float(inertial.get("mass", ""))
        for inertial in model.iter("inertial")
        if inertial.get("mass")
    ]


def test_total_link_mass_is_within_the_l0_budget(
    sim_model: ElementTree.Element, register: dict[str, Any]
) -> None:
    """REQ-L0-MASS: the modelled link mass stays under the 35 kg promise.

    The sum is over the simulation model, which is the only place in either
    repository that carries a per-link mass. It does not include the harness,
    the battery or the off-the-shelf fasteners, so passing this test is
    necessary for the 35 kg claim and not sufficient for it — which is what
    REQ-L0-MASS's basis says.
    """
    entry = requirement(register, "REQ-L0-MASS")
    total = sum(_link_masses(sim_model))

    assert total <= entry["limit"], (
        f"modelled link mass is {total} kg, REQ-L0-MASS allows at most {entry['limit']} kg"
    )


def test_every_link_declares_a_mass(
    sim_model: ElementTree.Element, register: dict[str, Any]
) -> None:
    """REQ-L1-LINK-INERTIALS: all 28 bodies carry an inertial mass.

    Stated separately from REQ-L0-MASS because the two fail differently. A
    link losing its inertial block makes the robot lighter on paper and would
    move the mass total further inside its budget, so the budget test alone
    would report the regression as an improvement.
    """
    entry = requirement(register, "REQ-L1-LINK-INERTIALS")

    bodies = [body for body in sim_model.iter("body")]
    masses = _link_masses(sim_model)

    assert len(masses) == entry["limit"], (
        f"{len(masses)} bodies declare an inertial mass, REQ-L1-LINK-INERTIALS requires"
        f" exactly {entry['limit']}"
    )
    assert len(bodies) == len(masses), (
        f"the model has {len(bodies)} bodies but only {len(masses)} declare a mass"
    )
    assert all(mass > 0 for mass in masses), "a link declares a non-positive mass"


def test_model_declares_the_actuated_joint_count(
    sim_model: ElementTree.Element, register: dict[str, Any]
) -> None:
    """REQ-L1-ACTUATED-JOINTS: the model declares 23 powered rotations.

    The model actuates 23 of the robot's 25 joints. The two neck joints are
    declared `fixed` in sim-model/urdf/asimov_1.urdf and carry no joint
    element in the MJCF at all, so the head is rigid in simulation while the
    harness still lands a connector on each of its two motors. REQ-L0-DOF is
    the entry that continues to hold the robot to 25, and it is measured from
    the harness rather than from this model for exactly that reason.

    The two passive toe joints this test used to count are gone: upstream
    replaced the foot with contact spheres and deleted both toe links, so
    every named joint in the model is now an actuated one.
    """
    system = requirement(register, "REQ-L1-ACTUATED-JOINTS")

    actuated = actuated_joints(sim_model)

    assert len(actuated) == system["limit"], (
        f"the model declares {len(actuated)} actuated joints, REQ-L1-ACTUATED-JOINTS"
        f" requires exactly {system['limit']}"
    )
    assert len(named_joints(sim_model)) == len(actuated), (
        f"the model declares {len(named_joints(sim_model))} named joints but"
        f" {len(actuated)} actuated ones; a passive joint has appeared without a"
        " requirement describing it"
    )

    unbounded = [
        joint.get("name")
        for joint in sim_model.iter("joint")
        if joint.get("name") and not joint.get("range")
    ]
    assert not unbounded, f"actuated joints declaring no travel limit: {unbounded}"
