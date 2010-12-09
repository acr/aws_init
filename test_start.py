#!/usr/bin/env python

import startami
import sys

if __name__ == '__main__':
    if len(sys.argv) != 10:
        print "Usage: %s [image] [instanceType] [accessKey] [secretKey] " \
            "[pkname] [gitUrlOfInstanceBuilder] [softwareList] [pipelineUrl] " \
            "[webserverPort]" % sys.argv[0]
        exit()

    image = sys.argv[1]
    instanceType = sys.argv[2]
    accessKey = sys.argv[3]
    secretKey = sys.argv[4]
    pkname = sys.argv[5]
    gitUrlOfInstanceBuilder = sys.argv[6]
    softwareList = sys.argv[7]
    pipelineUrl = sys.argv[8]
    webserverPort = int(sys.argv[9])

    res = startami.startAndRun(image, instanceType, accessKey, secretKey,
                               pkname, gitUrlOfInstanceBuilder, softwareList,
                               pipelineUrl, webserverPort)
    
    print str(res)
