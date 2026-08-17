"""Wiring harness requirements: REQ-L2-CAN-DROP-PER-JOINT and the cable rules."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ElementTree
from typing import Any

from conftest import actuated_joints, requirement

#: The connector the project fits to every actuator: two power contacts and
#: two signal contacts in one XT30 shell.
ACTUATOR_CONNECTOR_TYPE = "XT30(2+2)"

#: What that connector must carry. Power without CAN is a motor that cannot be
#: commanded; CAN without power is one that cannot move.
ACTUATOR_PINLABELS = ("BATT+", "BATT-", "CAN_H", "CAN_L")

#: electrical/README.md: "W-<ID>-<TYPE>, ID = unique ID, TYPE = Power (PWR) or
#: Signal (SIG) cable bundle".
CABLE_NAME_PATTERN = re.compile(r"^W-(?P<id>\d+)-(?P<type>PWR|SIG)$")

#: The gauge each bundle type carries, uniformly, across the whole harness.
GAUGE_BY_TYPE = {"PWR": "17 AWG", "SIG": "26 AWG"}

#: Conductor pair per bundle: BATT+/BATT- on power, CAN_H/CAN_L on signal.
CONDUCTORS_PER_CABLE = 2

#: Joints the robot actuates and the simulation model does not. Neck yaw and
#: neck pitch are `fixed` joints in sim-model/urdf/asimov_1.urdf, so the MJCF
#: nests both neck bodies rigidly and declares no joint element for either —
#: but both motors are real, and the harness lands a drop on each. Named as a
#: constant so that the harness/model comparison below stays an equality: an
#: unexplained 24th joint or 26th connector still fails.
RIGIDLY_MODELLED_JOINTS = 2


def test_every_actuated_joint_has_a_power_and_can_drop(
    wiring: dict[str, Any],
    sim_model: ElementTree.Element,
    register: dict[str, Any],
) -> None:
    """REQ-L2-CAN-DROP-PER-JOINT: 25 actuator connectors, matching the 25 joints.

    This is the cross-artifact check the register exists for. The simulation
    model and the harness are maintained separately, and the only thing tying
    them together is that both describe the same robot: a joint added to one
    and not the other breaks the equality here rather than at assembly.
    """
    entry = requirement(register, "REQ-L2-CAN-DROP-PER-JOINT")

    drops = {
        name: connector
        for name, connector in wiring["connectors"].items()
        if connector.get("type") == ACTUATOR_CONNECTOR_TYPE
    }
    assert len(drops) == entry["limit"], (
        f"harness has {len(drops)} {ACTUATOR_CONNECTOR_TYPE} actuator connectors,"
        f" REQ-L2-CAN-DROP-PER-JOINT requires exactly {entry['limit']}"
    )

    incomplete = {
        name: connector.get("pinlabels")
        for name, connector in drops.items()
        if tuple(connector.get("pinlabels") or ()) != ACTUATOR_PINLABELS
    }
    assert not incomplete, (
        f"actuator connectors not carrying {list(ACTUATOR_PINLABELS)}: {incomplete}"
    )

    joints = actuated_joints(sim_model)
    assert len(drops) == len(joints) + RIGIDLY_MODELLED_JOINTS, (
        f"the harness gives {len(drops)} joints a drop and the simulation model declares"
        f" {len(joints)} actuated joints; the difference should be exactly the"
        f" {RIGIDLY_MODELLED_JOINTS} rigidly-modelled neck joints, so one of the two"
        " artifacts is out of date"
    )


def test_every_cable_follows_the_declared_naming_convention(
    wiring: dict[str, Any], register: dict[str, Any]
) -> None:
    """REQ-L2-CABLE-NAMING: all 53 cables match W-<ID>-<PWR|SIG>.

    The suffix is not cosmetic. It is the only thing in the harness that says
    whether a bundle belongs to the power tree or the CAN tree, so a cable
    that does not carry one cannot be placed in either.
    """
    entry = requirement(register, "REQ-L2-CABLE-NAMING")
    cables = wiring["cables"]

    violations = sorted(name for name in cables if not CABLE_NAME_PATTERN.match(name))
    assert not violations, f"cables not matching W-<ID>-<PWR|SIG>: {violations}"

    assert len(cables) == entry["limit"], (
        f"harness declares {len(cables)} cables, REQ-L2-CABLE-NAMING requires exactly"
        f" {entry['limit']}"
    )


def test_power_and_signal_cables_carry_their_declared_gauge(
    wiring: dict[str, Any], register: dict[str, Any]
) -> None:
    """REQ-L2-HARNESS-GAUGE: 17 AWG on every PWR run, 26 AWG on every SIG run."""
    entry = requirement(register, "REQ-L2-HARNESS-GAUGE")
    cables = wiring["cables"]

    wrong_gauge: dict[str, str] = {}
    wrong_count: dict[str, int] = {}
    for name, cable in cables.items():
        match = CABLE_NAME_PATTERN.match(name)
        if match is None:
            continue
        expected = GAUGE_BY_TYPE[match.group("type")]
        if cable.get("gauge") != expected:
            wrong_gauge[name] = f"{cable.get('gauge')} (expected {expected})"
        if cable.get("wirecount") != CONDUCTORS_PER_CABLE:
            wrong_count[name] = cable.get("wirecount")

    assert not wrong_gauge, f"cables whose gauge does not match their type: {wrong_gauge}"
    assert not wrong_count, (
        f"cables not carrying {CONDUCTORS_PER_CABLE} conductors: {wrong_count}"
    )

    conforming = len(cables) - len(wrong_gauge) - len(wrong_count)
    assert conforming == entry["limit"], (
        f"{conforming} cables match their declared gauge, REQ-L2-HARNESS-GAUGE requires"
        f" exactly {entry['limit']}"
    )
