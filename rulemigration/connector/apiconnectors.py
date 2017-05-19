#!/usr/bin/python

import logging
import urllib2
import base64
import json


class EARTConnector(object):
    """docstring for EARTConnector"""

    def __init__(self, userName=None, password=None):
        super(EARTConnector, self).__init__()
        self.userName = userName
        self.password = password

    def simulateRule(self, **args):
        logger = logging.getLogger('root')
        body = {}
        body['name'] = args['resourceName']
        body['source'] = args['source']
        body['userId'] = args['userId']
        body['baseType'] = args['baseType']
        body['groupName'] = args['groupName']

        if(args['userName'] != None):
            self.userName = args['userName']
        if(args['password'] != None):
            self.password = args['password']

        url = args['url']
        data = json.dumps(body)
        logger.debug("call api %s" % url)
        logger.debug("request is %s" % data)
        req = urllib2.Request(url, data=data)
        base64string = base64.encodestring(
            '%s:%s' % (self.userName, self.password)).replace('\n', '')
        req.add_header("Authorization", "Basic %s" % base64string)
        req.add_header("Content-Type", "application/json")
        resp = urllib2.urlopen(req)
        res = resp.read()
        logger.debug("response is %s" % res)
        resJson = json.loads(res)
        resultData = resJson['resultData']
        actions = resultData['roleActions']
        logger.info('Orignal approval actions for resource %s is %s' %
                    (args['resourceName'], actions))
        return actions

    def setApprovals(self, **args):
        logger = logging.getLogger('root')
        if('actions' not in args):
            logger.warn('No actions for resource %s, skip set approvals' % args['resourceName'])
            return
        logger.info('Set approvals for resource %s', args['resourceName'])
        logger.info('Actions are %s', args['actions'])
        body = {}
        body['name'] = args['resourceName']
        body['actions'] = args['actions']
        body['userId'] = args['userId']
        body['default'] = args['default']
        body['groupName'] = args['groupName']
        body['alwaysUpdate'] = args['alwaysUpdate']

        if(args['userName'] != None):
            self.userName = args['userName']
        if(args['password'] != None):
            self.password = args['password']

        url = args['url']
        data = json.dumps(body)
        logger.debug("call api %s" % url)
        logger.debug("request is %s" % data)
        req = urllib2.Request(url, data=data)
        base64string = base64.encodestring(
            '%s:%s' % (self.userName, self.password)).replace('\n', '')
        req.add_header("Authorization", "Basic %s" % base64string)
        req.add_header("Content-Type", "application/json")
        resp = urllib2.urlopen(req)
        res = resp.read()
        logger.debug("response is %s" % res)


if __name__ == '__main__':
    body = {}
    print('list is %s' % body['actions'])
    #connector = EARTConnector()
    #connector.simulateRule(url='http://edsartrule-dev2.cloudapps.cisco.com/services/v1/rule/simulate/cepm', userName='artapi.gen',
    #                       password='cisco123', resourceName='SCAppGrp:1LEVELROLE2', source='CEPM', userId='zhenghu', baseType='RESOURCE', groupName='SCAppGrp')
