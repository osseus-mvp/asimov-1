#!/bin/bash
ip link set end1 down
ip addr add 10.0.0.2/24 dev end1
ip link set end1 up
