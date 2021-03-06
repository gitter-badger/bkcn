import unittest
import asyncio
import logging

from ...gw import bfx
from ...fw import log

# https://stackoverflow.com/a/23642269/267482
# https://stackoverflow.com/a/23036785/267482
# https://stackoverflow.com/a/5929165/267482
def async_test(loop):
    def decorator(func):
        def wrapper(*args, **kwargs):
            loop.run_until_complete(asyncio.coroutine(func)(*args, **kwargs))
        return wrapper
    return decorator

class BfxTest(unittest.TestCase):
    def setUp(self):
        logging.info("test set up")
        self.loop = asyncio.new_event_loop()

    def tearDown(self):
        logging.info("test tear down")
        if self.loop.is_running():
            self.loop.stop()

        if not self.loop.is_closed():
            self.loop.close()

        self.loop = None

    def runTest(self):
        async def snippet():
            async with bfx.Gateway(uri='wss://api.bitfinex.com/ws/2', loop=self.loop) as gw:
                await gw.prime('BTCUSD')
                await gw.prime('ETHUSD')
                key = await gw.sub('ETHBTC',
                             qh=lambda st, evt: logging.info('%s (%s)', st, evt),
                             th=lambda st, evt: logging.info('%s (%s)', st, evt))
                logging.info("sleeping")
                await asyncio.sleep(5, loop=self.loop)
                logging.info("unsubscribing")
                gw.drop(key)
                logging.info("sleeping")
                await asyncio.sleep(5, loop=self.loop)
                logging.info("back from sleep")
            logging.info("test coroutine done inside")

        logging.info("running test coroutine")
        self.loop.run_until_complete(snippet())
        logging.info("test coroutine done")

# should be run with pwd=.../sandbox/ for relative imports to work
if __name__ == '__main__':
    log.configure()
    unittest.main()
