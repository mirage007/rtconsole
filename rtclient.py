from IPython.kernel import BlockingKernelClient, get_connection_file, find_connection_file

cf= find_connection_file("kernel-305.json")
client = BlockingKernelClient(connection_file=cf)
client.load_connection_file()
client.start_channels()
client.execute('ddd')
msg = client.get_shell_msg(block=True, timeout=3000)
print msg
