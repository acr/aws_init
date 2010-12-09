#!/usr/bin/env python

import startami
import sys

if __name__ == '__main__':
    if len(sys.argv) != 9:
        print "Usage: %s [image] [instanceType] [accessKey] [secretKey] " \
            "[gitUrlOfInstanceBuilder] [softwareList] [pipelineUrl] " \
            "[webserverPort]" % sys.argv[0]
        exit()

    image = sys.argv[1]
    instanceType = sys.argv[2]
    accessKey = sys.argv[3]
    secretKey = sys.argv[4]
    gitUrlOfInstanceBuilder = sys.argv[5]
    softwareList = sys.argv[6]
    pipelineUrl = sys.argv[7]
    webserverPort = int(sys.argv[8])

    res = startami.startAndRun(image=image, instancetype=instanceType,
                               accesskey=accessKey, secretkey=secretKey,
                               pkname='',
                               gitUrlOfInstanceBuilder=gitUrlOfInstanceBuilder,
                               softwareList=softwareList,
                               pipelineUrl=pipelineUrl,
                               webserverPort=webserverPort)
    
    print str(res)
