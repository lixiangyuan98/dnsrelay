"""TYPE filed values in RR."""
A = b'\x00\x01'   # a host address
NS = b'\x00\x02'  # an authoritative name server
MD = b'\x00\x03'  # a mail destination (Obsolete - use MX)
MF = b'\x00\x04'  # a mail forwarder (Obsolete - use MX)
CNAME = b'\x00\x05'  # the canonical name for an alias
SOA = b'\x00\x06'  # marks the start of a zone of authority
MB = b'\x00\x07'  # a mailbox domain name (EXPERIMENTAL)
MG = b'\x00\x08'  # a mail group member (EXPERIMENTAL)
MR = b'\x00\x09'  # a mail rename domain name (EXPERIMENTAL)
NULL = b'\x00\x0a'  # a null RR (EXPERIMENTAL)
WKS = b'\x00\x0b'  # a well known service description
PTR = b'\x00\x0c'  # a domain name pointer
HINFO = b'\x00\x0d'  # host information
MINFO = b'\x00\x0e'  # mailbox or mail list information
MX = b'\x00\x0f'  # mail exchange
TXT = b'\x00\x10'  # text strings
