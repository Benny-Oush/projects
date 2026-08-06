from scapy.all import *
import random

rand_port = random.randint(20000, 60000)

host = input('Enter host: ')

dns_query = DNSQR(qname=host)
dns = DNS(qdcount=1, qd=dns_query)
udp = UDP(dport=53, sport=rand_port)
ip = IP(dst='8.8.8.8')

packet = ip / udp / dns

print(f'Sending dns query to find the ip of host {host}')

response = sr1(packet, verbose=0)

ip_addr = response[DNS][DNSRR].rdata
print(f'The ip of {host} is {ip_addr}')