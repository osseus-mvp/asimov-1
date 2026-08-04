"""CAN bus domain requirements: REQ-L1-CAN-DOMAINS down to REQ-L3-CM5-CAN-CONTROLLERS.

The chain these tests verify is the clearest decomposition in the register.
The port map declares six bus domains; the compute module's product brief caps
native CAN at three; the difference is exactly the three SPI bridges the board
carries. Change any one of the three numbers and the arithmetic stops working.
"""

from __future__ import annotations

from typing import Any

from conftest import requirement

NATIVE_CAN_COMPATIBLE = "rockchip,can-2.0"
BRIDGE_CAN_COMPATIBLE = "microchip,mcp2518fd"
ENABLED = 'status = "okay"'


def _node_bodies(text: str) -> list[str]:
    """The body of every brace-delimited node in the overlay."""
    bodies: list[str] = []
    opens: list[int] = []
    for index, char in enumerate(text):
        if char == "{":
            opens.append(index)
        elif char == "}" and opens:
            bodies.append(text[opens.pop() + 1 : index])
    return bodies


def _own_properties(body: str) -> str:
    """A node body with its children removed.

    Without this a parent node inherits every property its children declare,
    and `spi0` would look like three CAN controllers at once.
    """
    kept: list[str] = []
    depth = 0
    for char in body:
        if char == "{":
            depth += 1
        elif char == "}":
            depth = max(depth - 1, 0)
        elif depth == 0:
            kept.append(char)
    return "".join(kept)


def _enabled_can_nodes(device_tree_text: str, compatible: str) -> list[str]:
    """Bodies of the nodes declaring this CAN controller and switched on."""
    return [
        properties
        for properties in (_own_properties(body) for body in _node_bodies(device_tree_text))
        if f'compatible = "{compatible}"' in properties and ENABLED in properties
    ]


def test_device_tree_enables_six_can_interfaces(
    device_tree: str, register: dict[str, Any]
) -> None:
    """REQ-L1-CAN-DOMAINS: the overlay brings up one interface per declared port.

    electrical/README.md's port map is prose in a table. This test is the
    reason the port map can be treated as a system requirement at all: the
    overlay is the machine-readable half of the same statement.
    """
    entry = requirement(register, "REQ-L1-CAN-DOMAINS")

    native = _enabled_can_nodes(device_tree, NATIVE_CAN_COMPATIBLE)
    bridged = _enabled_can_nodes(device_tree, BRIDGE_CAN_COMPATIBLE)
    total = len(native) + len(bridged)

    assert total == entry["limit"], (
        f"the overlay enables {total} CAN interfaces ({len(native)} native,"
        f" {len(bridged)} bridged), REQ-L1-CAN-DOMAINS requires exactly {entry['limit']}"
    )


def test_three_can_domains_are_native_and_three_are_spi_bridges(
    device_tree: str, register: dict[str, Any]
) -> None:
    """REQ-L2-NATIVE-CAN-PORTS, REQ-L2-SPI-CAN-BRIDGES, REQ-L3-CM5-CAN-CONTROLLERS.

    Three requirements at three levels, one measurement, because they are the
    same fact seen from the part, the board and the system. The component
    ceiling is verified in the direction that can actually fail: the board must
    not enable more native controllers than the module provides.
    """
    native_entry = requirement(register, "REQ-L2-NATIVE-CAN-PORTS")
    bridge_entry = requirement(register, "REQ-L2-SPI-CAN-BRIDGES")
    module_entry = requirement(register, "REQ-L3-CM5-CAN-CONTROLLERS")

    native = _enabled_can_nodes(device_tree, NATIVE_CAN_COMPATIBLE)
    bridged = _enabled_can_nodes(device_tree, BRIDGE_CAN_COMPATIBLE)

    assert len(native) == native_entry["limit"], (
        f"the overlay enables {len(native)} native CAN interfaces,"
        f" REQ-L2-NATIVE-CAN-PORTS requires exactly {native_entry['limit']}"
    )
    assert len(bridged) == bridge_entry["limit"], (
        f"the overlay enables {len(bridged)} SPI-CAN bridges,"
        f" REQ-L2-SPI-CAN-BRIDGES requires exactly {bridge_entry['limit']}"
    )
    assert len(native) <= module_entry["limit"], (
        f"the overlay enables {len(native)} native CAN interfaces but the Radxa CM5"
        f" product brief allows at most {module_entry['limit']}"
    )

    chip_selects = 'num-cs = <3>'
    assert chip_selects in device_tree, (
        "the three SPI-CAN bridges share one SPI bus and need three chip selects;"
        f" {chip_selects!r} is not declared"
    )
