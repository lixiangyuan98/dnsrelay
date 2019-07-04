"""Data structure."""
from typing import List


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

    Attributes:

        ID(bytes): The identifier of this message.
        QR(bytes): Specify the message is a query(0) or a response(1).
        Opcode(bytes): Kind of query:
            - 0 a standard query (QUERY).
            - 1 an inverse query (IQUERY).
            - 2 a server status request (STATUS).
            - 3-15 reserved for future use.
        AA(bytes): 1 for authoritative answer.
        TC(bytes): 1 for truncation.
        RD(bytes): Recursion desired.
        RA(bytes): Recursion Available.
        Z(bytes): Reserved, set 0.
        RCODE(bytes): Error code:
            - 0   No error condition.
            - 1   Format error.
            - 2   Server failure.
            - 3   Name Error.
            - 4   Not Implemented.
            - 5   Refused.
        QDCOUNT(bytes): Number of questions.
        ANCOUNT(bytes): Number of answers.
        NSCOUNT(bytes): Number of authorities.
        ARCOUNT(bytes): Number of additionals.
    """

    def __init__(self, ID: int, QR: int, Opcode: int, AA: int, TC: int,
                    RD: int, RA: int, RCODE: int, Z: int, QDCOUNT: int,
                    ANCOUNT: int, NSCOUNT: int, ARCOUNT: int):
        """Construct `Header` from args."""

        self.ID = ID.to_bytes(2, 'big')
        self.QR = b'\x00' if QR == 0 else b'\x01'
        self.Opcode = Opcode.to_bytes(1, 'big')
        self.AA = AA.to_bytes(1, 'big')
        self.TC = TC.to_bytes(1, 'big')
        self.RD = b'\x00' if RD == 0 else b'\x01'
        self.RA = b'\x00' if RA == 0 else b'\x01'
        self.Z = Z.to_bytes(1, 'big')
        self.RCODE = RCODE.to_bytes(1, 'big')
        self.QDCOUNT = QDCOUNT.to_bytes(2, 'big')
        self.ANCOUNT = ANCOUNT.to_bytes(2, 'big')
        self.NSCOUNT = NSCOUNT.to_bytes(2, 'big')
        self.ARCOUNT = ARCOUNT.to_bytes(2, 'big')

    @classmethod
    def from_bytes(cls, data: bytes):
        """Construct `Header` from bytes."""

        ID = int(data[0:2].hex(), 16)
        QR = data[2] >> 7 & 0x01
        Opcode = data[2] >> 3 & 0x0F
        AA = data[2] >> 2 & 0x01
        TC = data[2] >> 1 & 0x01
        RD = data[2] & 0x01
        RA = data[3] >> 7 & 0x01
        Z = data[3] >> 4 & 0x07
        RCODE = data[3] & 0x0F
        QDCOUNT = int(data[4:6].hex(), 16)
        ANCOUNT = int(data[6:8].hex(), 16)
        NSCOUNT = int(data[8:10].hex(), 16)
        ARCOUNT = int(data[10:12].hex(), 16)

        return Header(ID, QR, Opcode, AA, TC, RD, RA, RCODE, Z,
                      QDCOUNT, ANCOUNT, NSCOUNT, ARCOUNT)

    def get_bytes(self) -> bytes:
        """Get `bytes` of `Header` in DNS message."""

        return self.ID + (self.QR[0] << 7 & 0x80 | self.Opcode[0] << 3 & 0x78 |
                          self.AA[0] << 2 & 0x04 | self.TC[0] << 1 & 0x02 | self.RD[0]) \
            .to_bytes(1, 'big') + \
            (self.RA[0] << 7 & 0x80 | self.Z[0] << 4 & 0x07 | self.RCODE[0]) \
            .to_bytes(1, 'big') + \
            self.QDCOUNT + self.ANCOUNT + self.NSCOUNT + self.ARCOUNT


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

    Attributes:

        QNAME(bytes): Domain name, could be a pointer.
        QTYPE(bytes): Question type.
        QCLASS(bytes): Question class.
    """

    def __init__(self, QNAME: bytes, QTYPE: bytes, QCLASS: bytes):
        self.QNAME = QNAME
        self.QTYPE = QTYPE
        self.QCLASS = QCLASS

    @classmethod
    def from_bytes(cls, data: bytes):
        """Construct `Question` from bytes."""

        return Question(data[:-4], data[-4:-2],  data[-2:])

    def get_bytes(self) -> bytes:
        """Get `bytes` of `Question` in DNS message"""

        return self.QNAME + self.QTYPE + self.QCLASS

    def get_QNAME(self) -> str:
        """Get human readable domain name."""

        start = 0
        length = self.QNAME[0]
        name = []
        while length != 0:
            name.append(self.QNAME[start + 1:start +
                                   length + 1].decode('utf8'))
            start = start + length + 1
            length = self.QNAME[start]
        return '.'.join(name)


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

    Attributes:

        NAME(bytes): The domain name. It can be a pointer.
        TYPE(bytes): RR type.
        CLASS(bytes): RR class.
        TTL(bytes): Time to live.
        RDLENGTH(bytes): Number of bytes of RDATA.
        RDATA(bytes): RR data.
    """

    def __init__(self, NAME: bytes, TYPE: int, CLASS: int,
                 TTL: int, RDLENGTH: int, RDATA: bytes):
        """Construct `ResourceRecord` (RR) from bytes."""

        self.NAME = NAME
        self.TYPE = TYPE.to_bytes(2, 'big')
        self.CLASS = CLASS.to_bytes(2, 'big')
        self.TTL = TTL.to_bytes(4, 'big')
        self.RDLENGTH = RDLENGTH.to_bytes(2, 'big')
        self.RDATA = RDATA

    @classmethod
    def from_bytes(cls, data: bytes, RDLENGTH: int):
        """Construct `bytes` from bytes."""

        NAME = data[:-(RDLENGTH + 10)]
        TYPE = int(data[-(RDLENGTH + 10):-(RDLENGTH + 8)].hex(), 16)
        CLASS = int(data[-(RDLENGTH + 8): -(RDLENGTH + 6)].hex(), 16)
        TTL = int(data[-(RDLENGTH + 6):-(RDLENGTH + 2)].hex(), 16)
        RDATA = data[-RDLENGTH:]

        return ResourceRecord(NAME, TYPE, CLASS, TTL, RDLENGTH, RDATA)

    def get_bytes(self) -> bytes:
        """Get `bytes` in RRs in DNS message."""

        return self.NAME + self.TYPE + self.CLASS + self.TTL + \
            self.RDLENGTH + self.RDATA


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

    Attributes:

        Header(Header): Header field in DNS message.
        Questions(list[Question]): List of questions contains Question section in DNS message.
        Answers(ResourceRecord): List of questions contains Answer section in DNS message.
        Authorities(ResourceRecord): List of questions contains Authority section in DNS message.
        Additionals(ResourceRecord): List of questions contains Additional section in DNS message.
    """

    def __init__(self, header: Header, questions: List[Question], answers: List[ResourceRecord], 
                    authorities: List[ResourceRecord], additionals: List[ResourceRecord]):
        """Construct DNS `Message`"""

        self.Header = header
        self.Questions = questions
        self.Answers = answers
        self.Authorities = authorities
        self.Additionals = additionals

    @classmethod
    def from_bytes(cls, data: bytes):
        """Construct DNS `Message` from bytes"""

        header = Header.from_bytes(data[0:12])
        questions_count = int(header.QDCOUNT.hex(), 16)
        answers_count = int(header.ANCOUNT.hex(), 16)
        authorities_count = int(header.NSCOUNT.hex(), 16)
        additionals_count = int(header.ARCOUNT.hex(), 16)
        questions = [None] * questions_count
        answers = [None] * answers_count
        authorities = [None] * authorities_count
        additionals = [None] * additionals_count
        next_start = 12
        if questions_count != 0:
            next_start = cls._parse_question(
                data, next_start, questions, int(header.QDCOUNT.hex(), 16))
        if answers_count != 0:
            next_start = cls._parse_rr(
                data, next_start, answers, answers_count)
        if authorities_count != 0:
            next_start = cls._parse_rr(
                data, next_start, authorities, authorities_count)
        if additionals_count != 0:
            next_start = cls._parse_rr(
                data, next_start, additionals, additionals_count)

        return Message(header, questions, answers, authorities, additionals)

    @classmethod
    def _parse_question(cls, message: bytes, start: int, dest: list, count: int) -> int:
        """Parse Questions in Message.

        Args:

            message: Whole DNS message.
            start: Start byte index of Questions Section in message.

        Returns:

            Start byte index of next section.
        """
        index = start
        for i in range(count):
            next_start = index + message[index:].find(0) + 5
            dest[i] = Question.from_bytes(message[index:next_start])
            index = next_start
        return index

    @classmethod
    def _parse_rr(cls, message: bytes, start: int, dest: list, count: int) -> int:
        """Parse Resource Record(RR) in Message.

        Args:

            message: Whole DNS message.
            start: Start byte index of RRs(Answer, Authority or Additional) Section in message.
            dest: Destination list to store the parsed RR.
            count: Number of RRs to parse.

        Returns:

            Start byte index of the next section.
        """
        index = start
        for i in range(count):
            if message[index] >> 6 & 0b0011 == 0b0011:
                TYPE_start = index + 2
            else:
                TYPE_start = index + message[index:].find(0) + 1
            RDLENGTH = int(message[TYPE_start + 8:TYPE_start + 10].hex(), 16)
            next_start = TYPE_start + RDLENGTH + 10
            dest[i] = ResourceRecord.from_bytes(
                message[index:next_start], RDLENGTH)
            index = next_start
        return index
    
    def get_bytes(self) -> bytes:
        """Get `bytes` of a DNS message."""

        questions = b''
        for question in self.Questions:
            questions += question.get_bytes()
        answers = b''
        for answer in self.Answers:
            answers += answer.get_bytes()
        authorities = b''
        for authority in self.Authorities:
            authorities += authority.get_bytes()
        additionals = b''
        for additional in self.Additionals:
            additionals += additional.get_bytes()
        
        return self.Header.get_bytes() + questions + answers + authorities + additionals
