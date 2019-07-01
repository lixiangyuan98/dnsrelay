"""DNSServer and handler method."""
from util.log import logger
from core.data import Message
import threading
import asyncio
import socket


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

    def __init__(self, host: str, port: int) -> None:
        self.event_loop = asyncio.new_event_loop()
        self.host = host
        self.port = port
        self._socket = socket.socket(type=socket.SOCK_DGRAM)
        self._socket.bind((self.host, self.port))

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
                logger.info('Receive from {addr}: {data}'.format(
                    addr=addr, data=data))
                message = Message(data)
                asyncio.run_coroutine_threadsafe(
                    self._handle(data, addr), self.event_loop)
        except KeyboardInterrupt:
            logger.info('Stop server')
            exit(0)
        self._socket.close()

    async def _handle(self, data: bytes, addr: tuple) -> None:
        """Handle the received data.

        Parse received data to DNS message, loop up the requested domain name
        in local database or foreign DNS server and send the result back to
        the user.

        """
        # TODO: handle the request
        self._socket.sendto(data, addr)

    def start(self):
        """Start the DNS Server.

        Start the async event loop and listening on given host and post.

        """
        logger.info('Starting server...')
        event_thread = threading.Thread(target=self._start_event_loop, args=())
        event_thread.setName('EventThread')
        event_thread.setDaemon(True)
        event_thread.start()
        logger.info('Event loop thread stated')
        self._listen()
