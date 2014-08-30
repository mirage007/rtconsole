import time
from IPython.kernel import get_connection_file
from rtconsole import start_console


if __name__ == '__main__':
    import logging
    logging.basicConfig(filename='test.log', level=0)
    app = start_console(locals())
    #print statements won't work as they are now routed to the console
    time.sleep(5)
    #we can optionally save the connection file somewhere, perhaps to be picked up by some other process
    connection_file = get_connection_file(app)
    logging.debug("the connection file is '%s'" % connection_file)

    #or we can manually connect to the latest session implicitly
    #at a command line, type `ipython console --existing`

    #see if you can inpsect tt in the command line and change its value!
    t = 0
    s = 0
    hello = lambda x: x**2
    print 'hello'
    while True:
        t += 1
        s = hello(t)
        time.sleep(1)
