from socket import *
import os
import sys
import struct
import time
import select
import binascii  

ICMP_ECHO_REQUEST = 8

def checksum(string):
    # In this function we make the checksum of our packet 
    string = bytearray(string)
    csum = 0
    countTo = (len(string) // 2) * 2

    for count in range(0, countTo, 2):
        thisVal = string[count+1] * 256 + string[count]
        csum = csum + thisVal
        csum = csum & 0xffffffff

    if countTo < len(string):
        csum = csum + string[-1]
        csum = csum & 0xffffffff

    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer

def receiveOnePing(mySocket, ID, timeout, destAddr):
    timeLeft = timeout
    while 1:
        startedSelect = time.time()
        whatReady = select.select([mySocket], [], [], timeLeft)
        howLongInSelect = (time.time() - startedSelect)
        if whatReady[0] == []: # Timeout
            return "Request timed out."
        
        timeReceived = time.time()
        recPacket, addr = mySocket.recvfrom(1024)

        # Fill in start
        # one or multiple lines of your code
        # You can use "struct.unpack" function with
        # parameter "bbHHh" to decode the ICMP header
        # Fill in end
        icmp_header = recPacket[20:28]
        type, code, checksum, packetID, sequence = struct.unpack("bbHHh", icmp_header)

        #debug code
        #print("debug : " + str(type))

         
         
        if type != 8 and packetID == ID:
            bytesInDouble = struct.calcsize("d")
            timeSent = struct.unpack("d", recPacket[28:28 + bytesInDouble])[0]
            return timeReceived - timeSent
            
        timeLeft = timeLeft - howLongInSelect
        #debug code
        print("debug" + str(timeLeft))
        if timeLeft <= 0:
            return "Request timed out."

def sendOnePing(mySocket, destAddr, ID):
    # Header is type (8), code (8), checksum (16), id (16), sequence (16)
    myChecksum = 0
    # Make a dummy header with a 0 checksum
    # struct -- Interpret strings as packed binary data
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    data = struct.pack("d", time.time())


    # Fill in start
    # one or multiple lines of your code
    # Calculate the checksum on the data and the dummy header.
    # Fill in end
    myChecksum = checksum(header+data) 


    # Get the right checksum, and put in the header
    if sys.platform == 'darwin':
        # Convert 16-bit integers from host to network byte order
        myChecksum = htons(myChecksum) & 0xffff
    else:
        myChecksum = htons(myChecksum)
    
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)


    # Fill in start
    # one or multiple lines of your code
    # use the socket to send the ICMP packet
    # Fill in end
    mySocket.sendto(header+data, (destAddr, 1))



def doOnePing(destAddr, timeout): 
    icmp = getprotobyname("icmp")
    # SOCK_RAW is a powerful socket type. For more details:   http://sock-raw.org/papers/sock_raw
    #mySocket = socket(AF_INET, SOCK_RAW, icmp)
    mySocket = socket(AF_INET, SOCK_DGRAM, icmp) #Encountered "Operation not permitted" when using SOCK_RAW
    
    myID = os.getpid() & 0xFFFF  # Return the current process i
    sendOnePing(mySocket, destAddr, myID)
    delay = receiveOnePing(mySocket, myID, timeout, destAddr)
    mySocket.close()
    return delay

def ping(host, timeout=1):
    # timeout=1 means: If one second goes by without a reply from the server,
    # the client assumes that either the client's ping or the server's pong is lost
    dest = gethostbyname(host)
    print("Pinging " + dest + " using Python:")
    print("")
    # Send ping requests to a server separated by approximately one second
    while 1:
        delay = doOnePing(dest, timeout)
        print(delay)
        time.sleep(1)# one second
    return delay

ping("127.0.0.1")
#ping("google.com")

