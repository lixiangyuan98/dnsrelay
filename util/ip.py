"""IP address manipulation."""

def get_bytes_from_ipv4(ip: str) -> bytes:
    """Get 4 bytes from a given IPv4 address."""

    addr = b''
    ip = ip.split('.')
    for i in range(4):
        addr += int(ip[i]).to_bytes(1, 'big')
    return addr

def get_ipv4_from_bytes(ip: bytes) -> str:
    """Get ip address from given 4 bytes."""
    ip = []
    for i in range(4):
        ip.append(int(ip[i].hex(), 16))
    return '.'.join(ip)
