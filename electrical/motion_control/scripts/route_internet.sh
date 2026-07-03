sudo iptables -t nat -A POSTROUTING -o enp5s0f3u1u1 -j MASQUERADE  
sudo iptables -A FORWARD -i enp5s0f3u1u1 -o wlp4s0 -m state --state RELATED,ESTABLISHED -j ACCEPT
sudo iptables -A FORWARD -i wlp4s0 -o enp5s0f3u1u1 -j ACCEPT
