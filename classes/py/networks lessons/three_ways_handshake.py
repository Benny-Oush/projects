from scapy.all import *

syn_tcp = TCP(dport=80, sport=41678, seq=123, flags='S')

ip = IP(dst='google.com')

packet = ip / syn_tcp

response = sr1(packet, timeout=5)

ack_tcp = TCP(dport=80, sport=41678, flags='A', seq=124, ack=(response[TCP].seq)+1)

packet = ip / ack_tcp

send(packet)

fyn_tcp = TCP(dport=80, sport=41678, seq=124, flags='F')

packet = ip / fyn_tcp

send(packet)