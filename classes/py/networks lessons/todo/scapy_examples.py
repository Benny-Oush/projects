from scapy.all import *

packets = sniff(count=2, lfilter=lambda p: DNS in p)

my_packet = packets[0]
my_packet.show()

print(my_packet.qd[0].qname) # ex: b'google.com'

my_packet[DNS].show()

print(my_packet[DNS].opcode)

# CREATING

my_packet = IP(src='127.0.0.1')
my_packet.show()
my_packet.dst = '127.0.0.24'

my_packet = Ether() / IP(ttl=4) / TCP(port=80) / Raw('Get / HTTP/1.1\r\n\r\n')

hexdump(my_packet)

# resolving

my_packet = IP(dst='google.com') / Raw('hello')
print(my_packet.dst)
send(my_packet)