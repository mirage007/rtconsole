from threading import Thread
from IPython.config import catch_config_error
from IPython.kernel import KernelManager, get_connection_file, BlockingKernelClient
from IPython.kernel.inprocess.ipkernel import InProcessKernel
from IPython.kernel.inprocess import InProcessKernelManager, BlockingInProcessKernelClient
import time
from IPython.kernel.zmq.kernelapp import IPKernelApp
from IPython.kernel.zmq.ipkernel import Kernel
import sys
from zmq.eventloop.zmqstream import ZMQStream

__author__ = 'mirage007'

import zmq

class ThreadKernel(Kernel):
    def dispatch_shell(self, stream, msg):
        """dispatch shell requests"""
        # flush control requests first
        if self.control_stream:
            self.control_stream.flush()

        idents,msg = self.session.feed_identities(msg, copy=False)
        try:
            msg = self.session.unserialize(msg, content=True, copy=False)
        except:
            self.log.error("Invalid Message", exc_info=True)
            return

        header = msg['header']
        msg_id = header['msg_id']
        msg_type = msg['header']['msg_type']

        # Print some info about this message and leave a '--->' marker, so it's
        # easier to trace visually the message chain when debugging.  Each
        # handler prints its message at the end.
        self.log.debug('\n*** MESSAGE TYPE:%s***', msg_type)
        self.log.debug('   Content: %s\n   --->\n   ', msg['content'])

        if msg_id in self.aborted:
            self.aborted.remove(msg_id)
            # is it safe to assume a msg_id will not be resubmitted?
            reply_type = msg_type.split('_')[0] + '_reply'
            status = {'status' : 'aborted'}
            md = {'engine' : self.ident}
            md.update(status)
            reply_msg = self.session.send(stream, reply_type, metadata=md,
                        content=status, parent=msg, ident=idents)
            return

        handler = self.shell_handlers.get(msg_type, None)
        if handler is None:
            self.log.error("UNKNOWN MESSAGE TYPE: %r", msg_type)
        else:
            # ensure default_int_handler during handler call
            #sig = signal(SIGINT, default_int_handler)
            try:
                handler(stream, idents, msg)
            except Exception:
                self.log.error("Exception in message handler:", exc_info=True)
            finally:
                pass#signal(SIGINT, sig)

    def enter_eventloop(self):
        """enter eventloop"""
        self.log.info("entering eventloop %s", self.eventloop)
        for stream in self.shell_streams:
            # flush any pending replies,
            # which may be skipped by entering the eventloop
            stream.flush(zmq.POLLOUT)
        # restore default_int_handler
        #signal(SIGINT, default_int_handler)
        while self.eventloop is not None:
            try:
                self.eventloop(self)
            except KeyboardInterrupt:
                # Ctrl-C shouldn't crash the kernel
                self.log.error("KeyboardInterrupt caught in kernel")
                continue
            else:
                # eventloop exited cleanly, this means we should stop (right?)
                self.eventloop = None
                break
        self.log.info("exiting eventloop")

class ThreadIPKernelApp(IPKernelApp):

    kernel_class = ThreadKernel

    def init_kernel(self):
        """Create the Kernel object itself"""
        shell_stream = ZMQStream(self.shell_socket)
        control_stream = ZMQStream(self.control_socket)


        kernel = self.kernel_class(parent=self, session=self.session,
                                shell_streams=[shell_stream, control_stream],
                                iopub_socket=self.iopub_socket,
                                stdin_socket=self.stdin_socket,
                                log=self.log,
                                profile_dir=self.profile_dir,
                                user_ns=self.user_ns,
        )
        kernel.record_ports(self.ports)
        self.kernel = kernel

    @catch_config_error
    def initialize(self, argv=None):
        super(IPKernelApp, self).initialize(argv)
        self.init_blackhole()
        self.init_connection_file()
        self.init_session()
        self.init_poller()
        self.init_sockets()
        self.init_heartbeat()
        # writing/displaying connection info must be *after* init_sockets/heartbeat
        self.log_connection_info()
        self.write_connection_file()
        self.init_io()
        #self.init_signal()
        self.init_kernel()
        # shell init steps
        self.init_path()
        self.init_shell()
        self.init_gui_pylab()
        self.init_extensions()
        self.init_code()
        # flush stdout/stderr, so that anything written to these streams during
        # initialization do not get associated with the first execution request
        sys.stdout.flush()
        sys.stderr.flush()

def setup_app(**kargs):
    return ThreadIPKernelApp(**kargs)

def _start_console(app, namespace):
    app.initialize()
    kn = app.kernel
    namespace.update(kn.shell.user_ns)
    kn.shell.user_ns = namespace
    app.start()

def start_console(namespace, **kwargs):
    app = setup_app(**kwargs)
    a = Thread(target=_start_console, args=(app, namespace))
    a.daemon = True
    a.start()
    return app

if __name__ == '__main__':
    import logging
    app = start_console(locals())
    time.sleep(5)

    connection_file = get_connection_file(app)
    logging.debug('print the connection file is %s' % connection_file)

    tt = 0
    while True:
        tt += 1
        time.sleep(1)