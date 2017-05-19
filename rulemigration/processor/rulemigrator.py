#!/usr/bin/python

import logging
from rulemigration.connector.dbconnectors import OracleConnector
from rulemigration.connector.apiconnectors import EARTConnector


class RuleMigrator(object):
    """docstring for RuleMigrator"""

    def __init__(self):
        super(RuleMigrator, self).__init__()
        self.dbConnctor = None
        self.apiConnector = None
        self.simulateRuleConfDict = None
        self.setApprovalsConfDict = None

    def initSimulateRuleConfDict(self, **args):
        logger = logging.getLogger('root')
        logger.info('Init simulate rule api configuration')
        self.simulateRuleConfDict = args

    def initSetApprovalsConfDict(self, **args):
        logger = logging.getLogger('root')
        logger.info('Init set approvals api configuration')
        self.setApprovalsConfDict = args

    def initDBConnector(self, url, userName, password, serviceName):
        logger = logging.getLogger('root')
        logger.info('Init DB connector')
        self.dbConnctor = OracleConnector(url, userName, password, serviceName)

    def initEARTConnector(self, userName=None, password=None):
        logger = logging.getLogger('root')
        logger.info('Init EART connector')
        self.apiConnector = EARTConnector(userName, password)

    def migrationRuleSetForRole(self, resourceName, source):
        migrationRec = self.dbConnctor.getMigratedRuleForRole(
            resourceName, source)
        self.migrationRuleSet(**migrationRec)

    def migrateRuleSet(self, **args):
        logger = logging.getLogger('root')
        logger.info('Migrate rule set for resource %s' % args['resourceName'])
        args['userId'] = 'zhenghu'
        args['baseType'] = 'RESOURCE'
        args['groupName'] = 'SCAppGrp'
        args.update(self.simulateRuleConfDict)
        actions = self.apiConnector.simulateRule(**args)
        args['actions'] = actions
        args['default'] = False
        args['alwaysUpdate'] = 'true'
        args.update(self.setApprovalsConfDict)
        self.apiConnector.setApprovals(**args)
        self.dbConnctor.insertMigrationLog(args['resourceName'], args['source'], args[
            'ruleSetId'], args['version'])

    def migrateRuleSets(self):
        logger = logging.getLogger('root')
        logger.info('Start to do rule sets migration')
        migrationRecs = self.dbConnctor.listMigratedRuleRoles()
        for migrationRec in migrationRecs:
            self.migrateRuleSet(**migrationRec)

    def rollbackRuleSets(self):
        self.dbConnctor.rollbackMigrationBatch()

    def rollbackRuleSet(self, resourceName, source):
        self.dbConnctor.rollbackMigrationOne(resourceName, source)
        self.dbConnctor.rollbackMigrationLog(resourceName, source)
