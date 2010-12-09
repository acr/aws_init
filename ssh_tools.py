"""
This file contains a library that provides methods to execute a command on a
a remote computer that is running an SSH server
"""

import paramiko
import socket
import time
import os

def is_port_open(host, port):
    """
    Returns True if the port on the given host is open, False if it is not
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
        sock.close()
        return True
    except:
        return False

class sshConnection(object):
    """
    This class contains methods executing commands on any computer running an
    SSH server
    """
    def __init__(self, serveraddress, port, username, privatekeyfile):
        """
        Initializes constants used to connecting to the server and opens an
        SSH conneself._privatekeyfilection
        """
        self._serveraddress = serveraddress
        self._port = port
        self._username = username
        self._connectionretries = 10
        self._privkey = \
            paramiko.DSSKey.from_private_key_file(privatekeyfile)
        self._ssh = paramiko.SSHClient()
        self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to the server
        for trial in range(0, self._connectionretries):
            if is_port_open(serveraddress, port):
                break
            elif trial == self._connectionretries:
                raise RuntimeError("Failed to connect to port %d on %s after " \
                                       "%s attempts" % \
                                       (port, serveraddress,
                                        self._connectionretries))
            else:
                time.sleep(1)

        # This usually fails a few times before the ssh server has come up
        while True:
            try:
                self._ssh.connect(serveraddress, username=username,
                                  pkey=self._privkey)
                break;
            except EOFError:
                time.sleep(1)

    def __del__(self):
        self._ssh.close()

    def executeCommand(self, command, verbose=False):
        """
        Executes a command over the SSH connection. If verbose
        is true, this command prints the stdoutput of the remote command
        """
        stdin, stdout, stderr = self._ssh.exec_command(command)

        if verbose:
            print "STDOUT"
        for line in stdout.readlines():
            if verbose:
                print line.strip()

        if verbose:
            print "STDERR:"
        for line in stderr.readlines():
            if verbose:
                print line.strip()

    def executeCommandInScreen(self, command):
        """
        Executes a command in a screen
        """
        command = "screen -d -m %s" % command
        self.executeCommand(command, False)

    def _getTransport(self):
        """
        Returns an opened transport connection
        """
        transport = paramiko.Transport((self._serveraddress, self._port))
        transport.connect(username=self._username, pkey=self._privkey)

        return transport

    def writeFile(self, fileData, remotefilename):
        """
        Writes given string contents to a remote file
        """
        transport = self._getTransport()
        sftp = paramiko.SFTPClient.from_transport(transport)
        sfile = sftp.file(remotefilename, 'w')
        sfile.write(fileData)
        sfile.close()
        sftp.close()
        transport.close()

    def sendFile(self, localfilename, remotefilename):
        """
        Sends a file from the local machine to the remote machine over the
        SSH connection
        """
        if not os.path.isfile(localfilename):
            return False

        transport = self._getTransport()
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.put(localfilename, remotefilename)
        sftp.close()
        transport.close()

        return True
