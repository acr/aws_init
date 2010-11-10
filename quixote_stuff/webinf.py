from quixote.publish import Publisher
from quixote.directory import Directory
from quixote import get_request
from quixote.server.simple_server import run
from xml.etree import ElementTree as ET
import startami

class WebRoot(Directory):
    _q_exports = ['', 'launchami', 'nodegen']

    def _q_index(self):
        return 'the index'

    def nodegen(self):
        """
        Creates a run list in the proper 'node.json' format given a string of
        url-encoded software*=<value> entries
        """
        softwareList = []
        request = get_request().get_fields()
        
        for key in request:
            if key.startswith('software'):
                softwareList.append('"recipe[%s]"' % request[key])

        return '{ "run_list": [ %s ] }' % ', '.join(softwareList)

    def launchami(self):
        """
        This portion of the webpage is responsible for launching an AMI with the
        arguments specified in the request. Valid arguments are:
        os=[ubuntu]
        instancetype=[m1.large]
        accesskey=<user's access key>
        secretkey=<user's secret key>
        pkname=<user's private key name>
        """

        # [AN] the url has to be properly escaped, some of the characters in the
        # keys are invalid for urls
        # Parse the arguments in the GET/POST request
        os = None
        instancetype = None
        accesskey = None
        secretkey = None
        pkname = None
        softwareList = []
        request = get_request().get_fields()
        for key in request:
            if key == 'os':
                os = request[key]
            elif key == 'instancetype':
                instancetype = request[key]
            elif key == 'accesskey':
                accesskey = request[key]
            elif key == 'secretkey':
                secretkey = request[key]
            elif key == 'pkname':
                pkname = request[key]
            elif key.startswith('software'):
                softwareList.append(request[key])

        startupresult = startami.prepareInstance(os, instancetype, accesskey,
                                                 secretkey, pkname,
                                                 softwareList)

#        startupresult = startami.startami(os, instancetype, accesskey, secretkey,
#                                          pkname, softwareList)
        return formatstartupresult(startupresult)

def formatstartupresult(startupresult):
    """
    Formats the result of starting an AMI into an XML string
    """
    response = ET.Element('response')

    for key in startupresult:
        keyfield = ET.SubElement(response, key)
        keyfield.text = startupresult[key]

    return ET.tostring(response)

def create_publisher():
    return Publisher(WebRoot(),
                     display_exceptions='plain')

if __name__ == '__main__':
    port = 8080
    host = 'localhost'

    print 'listening on %s:%d' % (host, port)
    run(create_publisher, host=host, port=port)
