#!/bin/sh
sudo nmcli connection add type ethernet con-name "static-dongle" ifname enp5s0f3u1u1 ipv4.method manual ipv4.addresses 10.0.0.3/24 ipv4.gateway 0.0.0.1 ipv4.dns 8.8.8.8
sudo nmcli connection up "static-dongle"

