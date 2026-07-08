from scapy.all import *

ip = IP(dst='127.0.0.1')

ports = []

for i in range(20, 1001):

    syn_tcp = TCP(dport=i, sport=41678, seq=123, flags='S')

    packet = ip / syn_tcp

    response = sr1(packet, timeout=0.5, verbose=0)

    if response and response[TCP].flags == 'SA':
        ports.append(i)

        rst_tcp = TCP(dport=i, sport=41678, seq=123, flags='R')

        packet = ip / rst_tcp

        send(packet)


print(ports)
