"""DNSServer and handler method."""
import threading
import asyncio
import socket

from util.log import logger
from .data import Message, ResourceRecord
from util import ip
from . import cache
from . import settings
from . import RR_type
from . import RR_class


class DNSServer:
    """DNS Server that accepts the requests, handle them and response.

    Instance of this class is singleton.
    """

    _lock = threading.Lock()

    @classmethod
    def __new__(cls, *args, **kwargs):
        """Singleton."""

        if not hasattr(cls, '_instance'):
            with cls._lock:
                if not hasattr(cls, '_instance'):
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, host: str, port: int, remote_host: str, 
                 cache_engine: str, host_filename: str) -> None:
        self.event_loop = asyncio.new_event_loop()
        self.host = host
        self.port = port
        self._remote_host = remote_host
        self._host_filename = host_filename
        try:
            self._cache = getattr(cache, settings.cache_engines[cache_engine])()  # type: cache.BaseCache
            self._socket = socket.socket(type=socket.SOCK_DGRAM)
            self._socket.bind((self.host, self.port))
        except KeyError:
            logger.error('Invalid cache engine: no such engine in settings')
        except AttributeError:
            logger.error('Invalid cache engine: not implemented engine')
        except PermissionError:
            logger.error('Permission denied, try sudo')
        else:
            return
        logger.info('Exit with errors')
        exit(0)

    def _start_event_loop(self):
        asyncio.set_event_loop(self.event_loop)
        self.event_loop.run_forever()

    def _listen(self):
        """Listen the given host and post.

        Listen for a UDP message and start a coroutine for each message
        to handle.
        """

        logger.info('Start listening on {host}:{port}'.format(
            host=self.host, port=self.port))
        try:
            while True:
                data, addr = self._socket.recvfrom(1024)
                logger.info('{addr}Receive from client: {data}'.format(
                    addr=addr, data=data))
                self._handle(data, addr)
                # asyncio.run_coroutine_threadsafe(
                #     self._handle(data, addr), self.event_loop)
        except KeyboardInterrupt:
            logger.info('Stop server')
            exit(0)
        self._socket.close()

    def _handle(self, data: bytes, source_addr: tuple) -> None:
        """Handle the received data.

        Parse received data to DNS message, loop up the requested domain name
        in local database or foreign DNS server and send the result back to
        the user.

        Args:

            data: Received data.
            source_addr: Source host addr.
        """

        message = Message.from_bytes(data)
        question = message.Questions[0]
        if question is None:
            logger.info('{addr}Format error'.format(addr=source_addr))
            return
        if question.QTYPE == RR_type.A:
            rdata = self._cache.get(question.get_QNAME(), 'A')
            if rdata is not None:
                if rdata != b'\x00\x00\x00\x00':
                    logger.info('{addr}Found A of {name}'.format(
                        name=question.get_QNAME(), addr=source_addr))
                    header = message.Header
                    header.RA = b'\x01'
                    header.QDCOUNT = b'\x00\x00'
                    header.ANCOUNT = b'\x00\x01'
                    header.QR = b'\x01'
                    ttl = self._cache.get_ttl(question.get_QNAME()) \
                            if self._cache.get_ttl(question.get_QNAME()) != -1 else 0
                    answer = ResourceRecord(b'\xc0\x0c', RR_type.A, RR_class.IN, ttl, 4, 
                            self._cache.get(question.get_QNAME(), 'A'))
                    response = Message(header, [], [answer], [], []).get_bytes()
                else:
                    logger.info('{addr}Blocked {name}'.format(
                        name=question.get_QNAME(), addr=source_addr))
                    header = message.Header
                    header.RA = b'\x01'
                    header.QDCOUNT = b'\x00\x00'
                    header.ANCOUNT = b'\x00\x00'
                    header.QR = b'\x01'
                    header.RCODE = b'\x03'
                    response = Message(header, [], [], [], []).get_bytes()
            else:
                logger.info('{addr}Forward to remote DNS server: {name}'.format(
                    name=question.get_QNAME(), addr=source_addr))
                response = self._forward(data)
        else:
            logger.info('{addr}Forward to remote DNS server: {name}'.format(
                name=question.get_QNAME(), addr=source_addr))
            response = self._forward(data)
        self._socket.sendto(response, source_addr)
    
    def _forward(self, data: bytes) -> bytes:
        """Forward the message to remote server."""

        remote_socket = socket.socket(type=socket.SOCK_DGRAM)
        remote_socket.sendto(data, (self._remote_host, 53))
        response, _ = remote_socket.recvfrom(2048)
        logger.info('Receive from remote DNS server: {data}'.format(data=response))
        message = Message.from_bytes(response)
        for answer in message.Answers:
            if answer.TYPE == RR_type.A and answer.TTL != b'\x00\x00':
                # cache the record
                self._cache.put(message.Questions[0].get_QNAME(), 
                  'A', answer.RDATA)
                self._cache.set_ttl(message.Questions[0].get_QNAME(), 
                  int(answer.TTL.hex(), 16))
                logger.info('Cache the record {answer}, TTL={ttl}'
                  .format(answer=answer.RDATA, ttl=int(answer.TTL.hex(), 16)))
        return response

    def start(self):
        """Start the DNS Server.

        Start the async event loop, load the host file to cache 
        and listening on given host and post.
        """

        logger.info('Starting server...')
        event_thread=threading.Thread(target=self._start_event_loop, args=())
        event_thread.setName('EventThread')
        event_thread.setDaemon(True)
        event_thread.start()
        logger.info('Event loop thread started')
        logger.info('Load host file {filename}'.format(filename=self._host_filename))
        for line in open(self._host_filename):
            addr, domain = line.split(' ')
            domain = domain.replace('\n', '')
            addr = ip.get_bytes_from_ipv4(addr)
            self._cache.put(domain, 'A', addr)
        logger.info('Loading finished')
        self._listen()
