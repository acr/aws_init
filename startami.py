from boto.ec2.connection import EC2Connection
import time
import paramiko
import os
import socket
import ssh_tools

# [AN] move these data and related functions to their own file/module
AVAILABLE_IMAGES = {
    'ubuntu1004x64': {'imageid': 'ami-04a95e6d', 'supported_instances':
                          ['m1.large', 'm1.xlarge', 't1.micro', 'm2.xlarge',
                           'm2.2xlarge', 'm2.4xlarge', 'c1.medium', 'c1.xlarge',
                           'cc1.4xlarge'],
                      'username': 'ubuntu'
                      }}
PRIVATE_KEY_FILE = os.path.join(os.path.dirname(__file__), 'auth', 'id_dsa')
USERNAME = 'root'
NODEJS_PATH = '/etc/chef/node.js'
CHEF_REPOSITORY_LOCATION = 'http://lyorn.idyll.org/~nolleyal/chef/' \
    'chef-solo.tar.gz'
NUM_RETRY_ATTEMPTS = 10
INIT_SECONDS = 3.0 * 60.0
SSH_PORT = 22

def get_available_images():
    """
    Returns a dictionary of name-amiId pairs of the Images availiable to run
    """
    return AVAILABLE_IMAGES

def get_image_username(image):
    """
    Returns the username used to login to the image
    """
    if not is_valid_image(image):
        return False

    return AVAILABLE_IMAGES[image]['username']

def get_image_id(image):
    """
    Returns the ID associated with the given IMAGE name
    """
    if not is_valid_image(image):
        return False

    return AVAILABLE_IMAGES[image]['imageid']

def is_valid_image(image):
    """
    Checks the image name to see if it is in the list of recognized images
    """
    if image not in AVAILABLE_IMAGES.keys():
        return False

    return True

def is_valid_instance_type(image, instancetype):
    """
    Checks the insance type and image to see if they are compatible
    """
    if not is_valid_image(image):
        return False

    if instancetype not in AVAILABLE_IMAGES[image]['supported_instances']:
        return False

    return True

# [AN] this is depricated
def generateRunList(softwareList):
    """
    Generates a string that can be used as a run list to install the software
    named in 'softwareList'
    """
    swEntrys = []
    for software in softwareList:
        swEntrys.append('"recipe[%s]"' % software)

    return '{ "run_list": [ %s ] }' % ', '.join(swEntrys)

# [AN] this is depricated
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

# [AN] this is depricated
def installSoftware(dnsname, softwareList):
    """
    SSH's onto the machine at 'dnsname' as root and invokes chef-solo
    to install the software in softwareList
    """
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    privkey = paramiko.DSSKey.from_private_key_file(PRIVATE_KEY_FILE)

    # Try connecting to port 22 until it is available
    for trial in range(0, NUM_RETRY_ATTEMPTS):
        print "connection try %d" % trial
        if is_port_open(dnsname, SSH_PORT):
            break
        elif trial == NUM_RETRY_ATTEMPTS-1:
            raise RuntimeError("Failed to connect to port %d on %s after " \
                                   "%s attempts" % (SSH_PORT, dnsname,
                                                    NUM_RETRY_ATTEMPTS))
        else:
            time.sleep(1)

    ssh.connect(dnsname, username=USERNAME, pkey=privkey)

    # Write the run list to the '/etc/chef/node.js' file on the Amazon server
    transport = paramiko.Transport((dnsname, 22))
    transport.connect(username=USERNAME, pkey=privkey)
    sftp = paramiko.SFTPClient.from_transport(transport)
    sfile = sftp.file(NODEJS_PATH, 'w')
    sfile.write(generateRunList(softwareList))
    sfile.close()
    sftp.close()
    transport.close()

    # Use chef to install software
    command = "chef-solo -j %s -r %s" % \
        (NODEJS_PATH,
         CHEF_REPOSITORY_LOCATION)

    # [AN] a function to parse the output and determine what happened?
    print "EXECUTING CHEF"
    stdin, stdout, stderr = ssh.exec_command(command)

    print "STDOUT:"
    for line in stdout.readlines():
        print line

    print "STDERR:"
    for line in stderr.readlines():
        print line

    ssh.close()


def startAndRun(image, instancetype, accesskey, secretkey, pkname,
                commandToExecute):
    """
    Launches an AMI instance using the supplied credentials and executes a
    command in a screen on the remote instance
    """
    # Start up the AMI
    username, dnsName = startami(image, instancetype, accesskey, secretkey,
                                 pkname)

    # Open an SSH connection onto the machine
    instance_ssh_session = ssh_tools.sshConnection(dnsName, SSH_PORT,
                                                   USERNAME, PRIVATE_KEY_FILE)
    
    # Run the script in a detached screen
    instance_ssh_session.executeCommandInScreen(commandToExecute)
    
    return (username, dnsName)

def startami(imageName, instancetype, accesskey, secretkey, pkname):
    """
    Launches an AMI instance using the supplied credentials. On success,
    the dns name of the instance is returned. If a failure occurs,
    an exception is raised
    """
    if not is_valid_instance_type(imageName, instancetype):
        raise ValueError("Invalid instance type: '%s'" % instancetype)

    conn = EC2Connection(accesskey, secretkey)
    image = conn.get_image(get_image_id(imageName))
    reservation = image.run(instance_type=instancetype, key_name=pkname)
    instance = reservation.instances[0]

    waitForInstanceToRun(instance)

    return (get_image_username(imageName), str(instance.dns_name))

def waitForInstanceToRun(instance):
    """
    Given an instance that has been requested to start, this method waits
    until it actually has been started
    """
    while True:
        try:
            instance.update()
            break
        except EC2ResponseError:
            continue

    before = time.time()
    while True:
        if instance.update() == u'running':
            break
        elif time.time() - before > INIT_SECONDS:
            raise RuntimeError("AWS instance failed to start after %f " \
                                   "seconds" % INIT_SECONDS)
        time.sleep(1)
