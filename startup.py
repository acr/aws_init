#!/usr/bin/env python

from boto.ec2.connection import EC2Connection
import sys, time

CREDENTS = {'access': 'AKIAIPTGCRTMWK3JGNDQ',
            'secret': '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' }

AVAILABLEOSS = {'ubuntu': 'ami-c2986cab'}
AVAILABLESOFTWARE = ['screen', 'zsh', 'git']

def startAwsInstance(os, accessid, secretkey, keypair):
    """
    This function starts an AWS instance using the given login information
    and OS information. On success, a reference to the instance is returned
    """
    conn = EC2Connection(accessid, secretkey)
    image = conn.get_image(AVAILABLEOSS[os])
    reservation = image.run(key_name=keypair, instance_type='m1.large')
    instance = reservation.instances[0]

    while( instance.update() == u'pending' ):
        time.sleep(1)

    return instance

def createRunList(softwareList):
    """
    This function generates a node.json file that contains a run list
    consisting of the software in 'softwareList'. The Amazon virtual server
    referenced in 'instance' is then ssh'd into and chef-solo is run,
    pointing its node.json file to the one created

    Model after this:
    {
      "run_list": [ "recipe[zsh]", "recipe[screen]", "recipe[git]", "recipe[screed]" ]
    }
    """
    result = []
    result.append('{ "run_list": [ ')

    elements = []
    for program in softwareList:
        elements.append('"recipe[%s]"' % program)

    result.append(", ".join(elements))
    result.append(']}')
    return "".join(result)

def startAws(instance):
    """
    This function starts up the given amazon virtual server referenced in 'instance'.
    The server is ssh'd into and chef-solo is run, pointing it toward the auto-generated
    node.json file
    """

def printUsage():
    """
    Prints to stdout how the program should be invoked
    """
    print "Usage: [arg1][arg2]..."
    print
    print "Argument:      Values"
    print "-os            debian, ubuntu"
    print "-software      git, screen, zsh"
    print "-accessid      your aws access id"
    print "-secretkey     your aws secret key"
    print "-keypair       name of your keypair to use"
    return

if __name__ == '__main__':
    os = None
    software = None
    accessid = None
    secretkey = None
    keypair = None

    for argIdx in range(1, len(sys.argv)):
        arg = sys.argv[argIdx]

        if arg == "-os":
            os = sys.argv[argIdx+1].lower()
        elif arg == "-software":
            software = sys.argv[argIdx+1].split(',')
        elif arg == "-accessid":
            accessid = sys.argv[argIdx+1]
        elif arg == "-secretkey":
            secretkey = sys.argv[argIdx+1]
        elif arg == "-keypair":
            keypair = sys.argv[argIdx+1]

    if not os or not software or not accessid or not secretkey or not keypair:
        printUsage()
        exit()

    startupResult = startAwsInstance(os, accessid, secretkey, keypair)
    print "Instance started"
    print startupResult.dns_name
#    installResult = installSoftware(startupResult, software)
#    print "Software installed, login information"
#    print "SSH login string: %s@%s" % (installResult.username,
#                                       installResult.dnsname)
