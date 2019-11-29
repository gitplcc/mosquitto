#!/usr/bin/env python3

# Test what the broker does if receiving a PUBACK in response to a QoS 2 PUBREL.

from mosq_test_helper import *

def do_test(proto_ver):
    rc = 1
    keepalive = 60

    connect_packet = mosq_test.gen_connect("subpub-qos2-test", keepalive=keepalive, proto_ver=proto_ver)
    connack_packet = mosq_test.gen_connack(rc=0, proto_ver=proto_ver)

    mid = 1
    subscribe_packet = mosq_test.gen_subscribe(mid, "subpub/qos2", 2, proto_ver=proto_ver)
    suback_packet = mosq_test.gen_suback(mid, 2, proto_ver=proto_ver)

    helper_connect = mosq_test.gen_connect("helper", keepalive=keepalive, proto_ver=proto_ver)
    helper_connack = mosq_test.gen_connack(rc=0, proto_ver=proto_ver)

    mid = 1
    publish1s_packet = mosq_test.gen_publish("subpub/qos2", qos=2, mid=mid, payload="message", proto_ver=proto_ver)
    pubrec1s_packet = mosq_test.gen_pubrec(mid, proto_ver=proto_ver)
    pubrel1s_packet = mosq_test.gen_pubrel(mid, proto_ver=proto_ver)
    pubcomp1s_packet = mosq_test.gen_pubcomp(mid, proto_ver=proto_ver)

    mid = 1
    publish1r_packet = mosq_test.gen_publish("subpub/qos2", qos=2, mid=mid, payload="message", proto_ver=proto_ver)
    pubrec1r_packet = mosq_test.gen_pubrec(mid, proto_ver=proto_ver)
    pubrel1r_packet = mosq_test.gen_pubrel(mid, proto_ver=proto_ver)
    puback1r_packet = mosq_test.gen_puback(mid, proto_ver=proto_ver)

    pingreq_packet = mosq_test.gen_pingreq()
    pingresp_packet = mosq_test.gen_pingresp()

    port = mosq_test.get_port()
    broker = mosq_test.start_broker(filename=os.path.basename(__file__), port=port)

    try:
        sock = mosq_test.do_client_connect(connect_packet, connack_packet, timeout=20, port=port)
        mosq_test.do_send_receive(sock, subscribe_packet, suback_packet, "suback")

        helper = mosq_test.do_client_connect(helper_connect, helper_connack, timeout=20, port=port)
        mosq_test.do_send_receive(helper, publish1s_packet, pubrec1s_packet, "pubrec 1s")
        mosq_test.do_send_receive(helper, pubrel1s_packet, pubcomp1s_packet, "pubcomp 1s")
        helper.close()

        if mosq_test.expect_packet(sock, "publish 1r", publish1r_packet):
            mosq_test.do_send_receive(sock, pubrec1s_packet, pubrel1s_packet, "pubrel 1r")
            sock.send(puback1r_packet)
            sock.send(pingreq_packet)
            p = sock.recv(len(pingresp_packet))
            if len(p) == 0:
                rc = 0

        sock.close()
    finally:
        broker.terminate()
        broker.wait()
        (stdo, stde) = broker.communicate()
        if rc:
            print(stde.decode('utf-8'))
            print("proto_ver=%d" % (proto_ver))
            exit(rc)


do_test(proto_ver=4)
do_test(proto_ver=5)
exit(0)
