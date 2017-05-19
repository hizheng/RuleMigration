#!/usr/bin/python

import sys
import ConfigParser
import logging
from rulemigration.processor.rulemigrator import RuleMigrator


class Manager(object):
    """docstring for Manager"""

    def __init__(self, lifeCycle):
        super(Manager, self).__init__()
        self.lifeCycle = lifeCycle
        self.ruleMigrator = RuleMigrator()
        self.initRuleMigrator()

    def initRuleMigrator(self):
        logger = logging.getLogger('root')
        logger.info('init rule migrator')
        config = ConfigParser.ConfigParser()
        confDir = sys.path[0] + "/config"
        confFile = confDir + "/" + self.lifeCycle + "_conf.ini"
        config.read(confFile)
        dbUrl = config.get("db", "url")
        dbUsername = config.get("db", "userName")
        dbPassword = config.get("db", "password")
        serviceName = config.get("db", "serviceName")
        self.ruleMigrator.initDBConnector(
            dbUrl, dbUsername, dbPassword, serviceName)

        simulateApiUrl = config.get('api-simulateRule', 'url')
        simulateApiUserName = config.get('api-simulateRule', 'userName')
        simulateApiPassword = config.get('api-simulateRule', 'password')
        setApprovalUrl = config.get('api-setApprovals', 'url')
        setApprovalUserName = config.get('api-setApprovals', 'userName')
        setApprovalPassword = config.get('api-setApprovals', 'password')
        self.ruleMigrator.initSimulateRuleConfDict(
            url=simulateApiUrl, userName=simulateApiUserName, password=simulateApiPassword)
        self.ruleMigrator.initSetApprovalsConfDict(
            url=setApprovalUrl, userName=setApprovalUserName, password=setApprovalPassword)
        self.ruleMigrator.initEARTConnector()

    def doMigrationForRole(self, resourceName, source):
        self.ruleMigrator.doMigrationForRole(resourceName, source)

    def doMigrations(self):
        self.ruleMigrator.migrateRuleSets()

    def doRollback(self, resourceName=None, source=None):
        if(resourceName == None and source == None):
            self.ruleMigrator.rollbackRuleSets()
        else:
            self.ruleMigrator.rollbackRuleSet(resourceName, source)
