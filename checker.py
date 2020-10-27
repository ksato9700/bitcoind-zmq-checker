import zmq
import sys
import binascii
import struct


def handle(data):
    topic, body, seq = data
    sequence = 'Unknown'
    if len(seq) == 4:
        sequence = str(struct.unpack('<I', seq)[-1])
    if topic == b'hashblock':
        print('- HASH BLOCK ('+sequence+') -')
        print(binascii.hexlify(body))
    elif topic == b'hashtx':
        print('- HASH TX  ('+sequence+') -')
        print(binascii.hexlify(body))
    elif topic == b'rawblock':
        print('- RAW BLOCK HEADER ('+sequence+') -')
        print(binascii.hexlify(body[:80]))
    elif topic == b'rawtx':
        print('- RAW TX ('+sequence+') -')
        print(binascii.hexlify(body)[:32])
    elif topic == b'sequence':
        hash = binascii.hexlify(body[:32])
        label = chr(body[32])
        mempool_sequence = None if len(
            body) != 32+1+8 else struct.unpack('<Q', body[32+1:])[0]
        print('- SEQUENCE ('+sequence+') -')
        print(hash, label, mempool_sequence)


def main():
    if len(sys.argv) != 2:
        print(f'Usage: {sys.argv[0]} <bitcoind_zmq_url>')
        sys.exit(1)

    bitcoind_zmq_url = sys.argv[1]
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.setsockopt(zmq.RCVHWM, 0)
    socket.setsockopt_string(zmq.SUBSCRIBE, 'hashblock')
    socket.setsockopt_string(zmq.SUBSCRIBE, 'hashtx')
    socket.setsockopt_string(zmq.SUBSCRIBE, 'rawblock')
    socket.setsockopt_string(zmq.SUBSCRIBE, 'rawtx')
    socket.setsockopt_string(zmq.SUBSCRIBE, 'sequence')
    socket.connect(bitcoind_zmq_url)

    while True:
        data = socket.recv_multipart()
        print('data:', len(data))
        handle(data)


if __name__ == '__main__':
    main()
