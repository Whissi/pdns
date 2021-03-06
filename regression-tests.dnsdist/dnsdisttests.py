#!/usr/bin/env python2

import clientsubnetoption
import dns
import dns.message
import Queue
import os
import socket
import struct
import subprocess
import sys
import threading
import time
import unittest
import random


class DNSDistTest(unittest.TestCase):
    """
    Set up a dnsdist instance and responder threads.
    Queries sent to dnsdist are relayed to the responder threads,
    who reply with the response provided by the tests themselves
    on a queue. Responder threads also queue the queries received
    from dnsdist on a separate queue, allowing the tests to check
    that the queries sent from dnsdist were as expected.
    """
    _dnsDistPort = 5340
    _testServerPort = 5350
    _toResponderQueue = Queue.Queue()
    _fromResponderQueue = Queue.Queue()
    _dnsdist = None
    _responsesCounter = {}
    _config_template = """
    newServer{address="127.0.0.1:%s"}
    truncateTC(true)
    addAnyTCRule()
    addAction(RegexRule("evil[0-9]{4,}\\\\.regex\\\\.tests\\\\.powerdns\\\\.com$"), RCodeAction(5))
    mySMN = newSuffixMatchNode()
    mySMN:add(newDNSName("nameAndQtype.tests.powerdns.com."))
    addAction(AndRule{SuffixMatchNodeRule(mySMN), QTypeRule("TXT")}, RCodeAction(4))
    block=newDNSName("powerdns.org.")
    function blockFilter(remote, qname, qtype, dh)
        if(qname:isPartOf(block))
        then
            print("Blocking *.powerdns.org")
            return true
        end
        return false
    end
    """
    _config_params = ['_testServerPort']
    _acl = ['127.0.0.1/32']

    @classmethod
    def startResponders(cls):
        print("Launching responders..")
        # clear counters
        for key in cls._responsesCounter:
            cls._responsesCounter[key] = 0

        cls._UDPResponder = threading.Thread(name='UDP Responder', target=cls.UDPResponder, args=[cls._testServerPort])
        cls._UDPResponder.setDaemon(True)
        cls._UDPResponder.start()
        cls._TCPResponder = threading.Thread(name='TCP Responder', target=cls.TCPResponder, args=[cls._testServerPort])
        cls._TCPResponder.setDaemon(True)
        cls._TCPResponder.start()

    @classmethod
    def startDNSDist(cls, shutUp=True):
        print("Launching dnsdist..")
        conffile = 'dnsdist_test.conf'
        params = tuple([getattr(cls, param) for param in cls._config_params])
        print(params)
        with open(conffile, 'w') as conf:
            conf.write("-- Autogenerated by dnsdisttests.py\n")
            conf.write(cls._config_template % params)

        dnsdistcmd = [os.environ['DNSDISTBIN'], '-C', conffile,
                      '-l', '127.0.0.1:%d' % cls._dnsDistPort]
        for acl in cls._acl:
            dnsdistcmd.extend(['--acl', acl])
        print(' '.join(dnsdistcmd))

        if shutUp:
            with open(os.devnull, 'w') as fdDevNull:
                cls._dnsdist = subprocess.Popen(dnsdistcmd, close_fds=True, stdout=fdDevNull)
        else:
            cls._dnsdist = subprocess.Popen(dnsdistcmd, close_fds=True)

        time.sleep(1)

        if cls._dnsdist.poll() is not None:
            cls._dnsdist.terminate()
            cls._dnsdist.wait()
            sys.exit(cls._dnsdist.returncode)

    @classmethod
    def setUpSockets(cls):
        print("Setting up UDP socket..")
        cls._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        cls._sock.connect(("127.0.0.1", cls._dnsDistPort))

    @classmethod
    def setUpClass(cls):

        cls.startResponders()
        cls.startDNSDist()
        cls.setUpSockets()

        print("Launching tests..")

    @classmethod
    def tearDownClass(cls):
        if cls._dnsdist:
            cls._dnsdist.terminate()
            cls._dnsdist.wait()

    @classmethod
    def ResponderIncrementCounter(cls):
        if threading.currentThread().name in cls._responsesCounter:
            cls._responsesCounter[threading.currentThread().name] += 1
        else:
            cls._responsesCounter[threading.currentThread().name] = 1

    @classmethod
    def UDPResponder(cls, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        sock.bind(("127.0.0.1", port))
        while True:
            data, addr = sock.recvfrom(4096)
            request = dns.message.from_wire(data)
            if len(request.question) != 1:
                print("Skipping query with question count %d" % (len(request.question)))
                continue
            if str(request.question[0].name).endswith('tests.powerdns.com.') and not cls._toResponderQueue.empty():
                response = cls._toResponderQueue.get()
                response.id = request.id
                cls._fromResponderQueue.put(request)
                cls.ResponderIncrementCounter()
            else:
                # unexpected query, or health check
                response = dns.message.make_response(request)
                if request.question[0].rdclass == dns.rdataclass.IN:
                    if request.question[0].rdtype == dns.rdatatype.A:
                        rrset = dns.rrset.from_text(request.question[0].name,
                                                    3600,
                                                    request.question[0].rdclass,
                                                    request.question[0].rdtype,
                                                    '127.0.0.1')
                    elif request.question[0].rdtype == dns.rdatatype.AAAA:
                        rrset = dns.rrset.from_text(request.question[0].name,
                                                    3600,
                                                    request.question[0].rdclass,
                                                    request.question[0].rdtype,
                                                    '::1')
                if rrset:
                    response.answer.append(rrset)

            sock.sendto(response.to_wire(), addr)
        sock.close()

    @classmethod
    def TCPResponder(cls, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        try:
            sock.bind(("127.0.0.1", port))
        except socket.error as e:
            print("Error binding in the TCP responder: %s" % str(e))
            sys.exit(1)

        sock.listen(100)
        while True:
            (conn, address) = sock.accept()
            data = conn.recv(2)
            (datalen,) = struct.unpack("!H", data)
            data = conn.recv(datalen)
            request = dns.message.from_wire(data)
            if len(request.question) != 1:
                print("Skipping query with question count %d" % (len(request.question)))
                continue
            if str(request.question[0].name).endswith('tests.powerdns.com.') and not cls._toResponderQueue.empty():
                response = cls._toResponderQueue.get()
                response.id = request.id
                cls._fromResponderQueue.put(request)
                cls.ResponderIncrementCounter()
            else:
                # unexpected query, or health check
                response = dns.message.make_response(request)
                if request.question[0].rdclass == dns.rdataclass.IN:
                    if request.question[0].rdtype == dns.rdatatype.A:
                        rrset = dns.rrset.from_text(request.question[0].name,
                                                    3600,
                                                    request.question[0].rdclass,
                                                    request.question[0].rdtype,
                                                    '127.0.0.1')
                    elif request.question[0].rdtype == dns.rdatatype.AAAA:
                        rrset = dns.rrset.from_text(request.question[0].name,
                                                    3600,
                                                    request.question[0].rdclass,
                                                    request.question[0].rdtype,
                                                    '::1')
                if rrset:
                    response.answer.append(rrset)

            wire = response.to_wire()
            conn.send(struct.pack("!H", len(wire)))
            conn.send(wire)
            conn.close()
        sock.close()

    @classmethod
    def sendUDPQuery(cls, query, response, useQueue=True, timeout=2.0):
        if useQueue:
            cls._toResponderQueue.put(response)

        if timeout:
            cls._sock.settimeout(timeout)

        try:
            cls._sock.send(query.to_wire())
            data = cls._sock.recv(4096)
        except socket.timeout as e:
            data = None
        finally:
            if timeout:
                cls._sock.settimeout(None)

        receivedQuery = None
        message = None
        if useQueue and not cls._fromResponderQueue.empty():
            receivedQuery = cls._fromResponderQueue.get(query)
        if data:
            message = dns.message.from_wire(data)
        return (receivedQuery, message)

    @classmethod
    def sendTCPQuery(cls, query, response, useQueue=True, timeout=2.0):
        if useQueue:
            cls._toResponderQueue.put(response)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(("127.0.0.1", cls._dnsDistPort))

        if timeout:
            sock.settimeout(timeout)

        try:
            wire = query.to_wire()
            sock.send(struct.pack("!H", len(wire)))
            sock.send(wire)
            data = sock.recv(2)
            if data:
                (datalen,) = struct.unpack("!H", data)
                data = sock.recv(datalen)
        except socket.timeout as e:
            print("Timeout: %s" % (str(e)))
            data = None
        except socket.error as e:
            print("Network error: %s" % (str(e)))
            data = None
        finally:
            sock.close()

        receivedQuery = None
        message = None
        if useQueue and not cls._fromResponderQueue.empty():
            receivedQuery = cls._fromResponderQueue.get(query)
        if data:
            message = dns.message.from_wire(data)
        return (receivedQuery, message)
