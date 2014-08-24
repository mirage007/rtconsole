from threading import Thread
from IPython.kernel.inprocess import BlockingInProcessKernelClient
import time
from rtconsole import startKernel

__author__ = 'mirage007'

import unittest


class MyTestCase(unittest.TestCase):
    def testInProcKernel(self):
        km = startKernel(locals())
        kc = BlockingInProcessKernelClient(kernel=km.kernel)
        kc.start_channels()
        res = kc.execute("hello='wassup'")
        print hello

    def testInProcKernelThread(self):
        a=Thread(target=startKernel, args=(locals(),))
        a.daemon=True
        a.start()
        someData = {}
        for i in range(100):
            someData[i] = i
            time.sleep(1)

if __name__ == '__main__':
    unittest.main()
