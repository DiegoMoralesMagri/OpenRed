import socket
import json
import base64
import time
from pathlib import Path

# Use pynacl for Ed25519
try:
    from nacl.signing import SigningKey, VerifyKey
    from nacl.encoding import Base64Encoder
except Exception:
    print("Please install pynacl: pip install pynacl")
    raise

KEY_FILE = Path("node_key.seed")


def load_or_create_key():
    if KEY_FILE.exists():
        b = KEY_FILE.read_bytes()
        sk = SigningKey(b)
        return sk
    sk = SigningKey.generate()
    KEY_FILE.write_bytes(bytes(sk))
    return sk


def node_id_from_pubkey(pk_bytes):
    import hashlib
    h = hashlib.sha256(pk_bytes).digest()
    return base64.urlsafe_b64encode(h).decode().rstrip("=")


def make_announcement(sk: SigningKey, listen_port=40000):
    pk = sk.verify_key.encode()
    nid = node_id_from_pubkey(pk)
    ann = {
        "id": nid,
        "pubkey": base64.b64encode(pk).decode(),
        "listen_addrs": [f"udp4://0.0.0.0:{listen_port}"],
        "timestamp": int(time.time()),
        "sequence": 1,
        "capabilities": ["announce", "simple-discovery"]
    }
    blob = json.dumps(ann, separators=(",",":"), sort_keys=True).encode()
    sig = sk.sign(blob).signature
    ann["signature"] = base64.b64encode(sig).decode()
    return ann


def send_multicast(ann, mcast_group="224.0.0.251", mcast_port=5353):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    # TTL=1 for local network
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
    data = json.dumps(ann).encode()
    sock.sendto(data, (mcast_group, mcast_port))
    sock.close()


def listen_multicast(mcast_group="224.0.0.251", mcast_port=5353, timeout=5):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', mcast_port))
    # join group
    mreq = socket.inet_aton(mcast_group) + socket.inet_aton('0.0.0.0')
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    sock.settimeout(timeout)
    peers = []
    try:
        while True:
            data, addr = sock.recvfrom(65536)
            try:
                obj = json.loads(data.decode())
                peers.append((obj, addr))
            except Exception as e:
                print('invalid', e)
    except Exception:
        pass
    sock.close()
    return peers


if __name__ == '__main__':
    sk = load_or_create_key()
    ann = make_announcement(sk)
    print('Announcement:', ann)
    print('Sending multicast...')
    send_multicast(ann)
    print('Listening for 5s for peers...')
    peers = listen_multicast()
    print('Found peers:', peers)
