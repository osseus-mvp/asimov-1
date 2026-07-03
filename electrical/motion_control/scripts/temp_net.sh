#!/bin/sh

echo "binding IP 192.168.123.222 to LAN interface"
sudo ifconfig enp5s0f3u1u1 10.0.0.3 netmask 255.255.255.0

