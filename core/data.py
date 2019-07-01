"""Data structure."""


class Message:
    """DNS Message.

    Message format:
    +---------------------+
    |        Header       |
    +---------------------+
    |       Question      | the question for the name server
    +---------------------+
    |        Answer       | RRs answering the question
    +---------------------+
    |      Authority      | RRs pointing toward an authority
    +---------------------+
    |      Additional     | RRs holding additional information
    +---------------------+

    """

    def __init__(self, message: bytes):
        """Construct DNS Message from message bytes."""
        self.Header = Header(message[0:12])
        questions_count = int(self.Header.QDCOUNT.hex(), 16)
        answers_count = int(self.Header.ANCOUNT.hex(), 16)
        authorities_count = int(self.Header.NSCOUNT.hex(), 16)
        additionals_count = int(self.Header.ARCOUNT.hex(), 16)
        self.Questions = [None] * questions_count
        self.Answers = [None] * answers_count
        self.Authorities = [None] * authorities_count
        self.Additionals = [None] * additionals_count
        next_start = 12
        if questions_count != 0:
            next_start = self._parse_question(message[next_start:])
        if answers_count != 0:
            next_start = self._parse_rr(
                message[next_start:], self.Answers, answers_count)
        if authorities_count != 0:
            next_start = self._parse_rr(
                message[next_start:], self.Authorities, authorities_count)
        if additionals_count != 0:
            next_start = self._parse_rr(
                message[next_start:], self.Additionals, additionals_count)

    def _parse_question(self, message: bytes) -> int:
        """Parse Questions in Message.

        Given the bytes after Header to parse the questions and
        return the byte index after the end of Question section.

        Raise AssertionError when the length of message <= 0.

        """
        assert len(message) > 0
        index = 0
        for i in range(int(self.Header.QDCOUNT.hex(), 16)):
            next_start = message.find(0) + 5
            self.Questions[i] = Question(message[index:next_start])
            index = next_start
        return index

    def _parse_rr(self, message: bytes, dest: list, count: int) -> int:
        """Parse Resource Record(RR) in Message.

        Given the bytes after Header and Question section and RRs 
        to parse the RRs and return the byte index after the end 
        of RRs.

        Raise AssertionError when the length of message <= 0.

        """
        assert len(message) > 0
        index = 0
        for i in range(count):
            TYPE_start = message.find(0) + 1
            RDLENGTH = int(message[TYPE_start + 8:TYPE_start + 10].hex(), 16)
            next_start = TYPE_start + RDLENGTH + 10
            dest[i] = ResourceRecord(message[index:next_start], RDLENGTH)
            index = next_start
        return index


class Header:
    """DNS Message Header field.

    Header format:

                                    1  1  1  1  1  1
      0  1  2  3  4  5  6  7  8  9  0  1  2  3  4  5
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                      ID                       |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |QR|   Opcode  |AA|TC|RD|RA|   Z    |   RCODE   |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                    QDCOUNT                    |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                    ANCOUNT                    |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                    NSCOUNT                    |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                    ARCOUNT                    |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+

    """

    def __init__(self, data: bytes = None):
        """Constructs Header from bytes."""

        self.ID = data[0:2]
        self.QR = bytes(hex(data[2] >> 7 & 0x01), encoding='ascii')
        self.Opcode = bytes(hex(data[2] >> 3 & 0x0F), encoding='ascii')
        self.AA = bytes(hex(data[2] >> 2 & 0x01), encoding='ascii')
        self.TC = bytes(hex(data[2] >> 1 & 0x01), encoding='ascii')
        self.RD = bytes(hex(data[2] & 0x01), encoding='ascii')
        self.RA = bytes(hex(data[3] >> 7 & 0x01), encoding='ascii')
        self.Z = bytes(hex(data[3] >> 4 & 0x07), encoding='ascii')
        self.RCODE = bytes(hex(data[3] & 0x0F), encoding='ascii')
        self.QDCOUNT = data[4:6]
        self.ANCOUNT = data[6:8]
        self.NSCOUNT = data[8:10]
        self.ARCOUNT = data[10:12]


class Question:
    """DNS Message Question field.

    Question format:
                                    1  1  1  1  1  1
      0  1  2  3  4  5  6  7  8  9  0  1  2  3  4  5
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                                               |
    /                     QNAME                     /
    /                                               /
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                     QTYPE                     |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                     QCLASS                    |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+

    """

    def __init__(self, data: bytes):
        """Construct Question from bytes"""

        self.QNAME = data[:-4]
        self.QTYPE = data[-4:-2]
        self.QCLASS = data[-2:]


class ResourceRecord:
    """DNS Message Resource Record(RR) field.

    Resource Record format:
                                    1  1  1  1  1  1
      0  1  2  3  4  5  6  7  8  9  0  1  2  3  4  5
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                                               |
    /                                               /
    /                      NAME                     /
    |                                               |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                      TYPE                     |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                     CLASS                     |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                      TTL                      |
    |                                               |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                   RDLENGTH                    |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--|
    /                     RDATA                     /
    /                                               /
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+

    """

    def __init__(self, data: bytes, RDLENGTH: int):
        """Construct Resource Record(RR) from bytes"""

        self.NAME = data[:-(RDLENGTH + 10)]
        self.TYPE = data[-(RDLENGTH + 10):-(RDLENGTH + 8)]
        self.CLASS = data[-(RDLENGTH + 8): -(RDLENGTH + 6)]
        self.TTL = data[-(RDLENGTH + 6):-(RDLENGTH + 2)]
        self.RDLENGTH = data[-(RDLENGTH + 2): -RDLENGTH]
        self.RDATA = data[-RDLENGTH:]
    