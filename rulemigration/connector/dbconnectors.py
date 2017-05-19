#/usr/bin/python

import cx_Oracle

import logging


class OracleConnector(object):
    """docstring for OracleConnector"""

    def __init__(self, url, userName, password, serviceName):
        super(OracleConnector, self).__init__()
        self.url = url
        self.userName = userName
        self.password = password
        self.serviceName = serviceName

    def getConnection(self):
        connectStr = "%s/%s@%s/%s" % (self.userName,
                                      self.password, self.url, self.serviceName)
        connection = cx_Oracle.connect(connectStr)
        return connection

    def getMigratedRuleForRole(self, resourceName, source):
        logger = logging.getLogger('root')
        connection = self.getConnection()
        query = ''' select * from (
                    select rsml2.id resource_id, rsml2.keyword, rsml2.source, rsml2.rule_set_id, rsml2.version from rule_set rs, rule,
                    (select rsml.*, res.keyword, res.source from resources res, (select rsm.id, rsm.base_type, rsm.rule_set_id, rsm.version from rule_set_map rsm,
                    (select id, base_type, max(creation_time) latest_time from rule_set_map group by id, base_type) rsmax
                    where rsm.id = rsmax.id and rsm.base_type=rsmax.base_type and rsm.creation_time = rsmax.latest_time) rsml where res.id = rsml.id
                    and rsml.base_type='RESOURCE' and res.keyword like 'SCAppGrp:%') rsml2 where rsml2.rule_set_id = rs.ID and rsml2.version = rs.version
                    and (
                    --(rs.request_rule_id = rule.id and rule.ruletype = 'requestRule')
                    --or
                    (rs.approve_rule_id = rule.id and rule.ruletype = 'approveRule')
                    --or 
                    --(rs.provision_rule_id = rule.id and rule.ruletype = 'provisionRule') 
                    ) order by resource_Id, RULETYPE
                    ) where keyword = :resourceName and source = :source'''
        cursor = connection.cursor()
        cursor.execute(query, {'resourceName': resourceName, 'source': source})
        row = cursor.fetchone()
        migrationRec = {}
        migrationRec['resourceName'] = row[1]
        migrationRec['source'] = row[2]
        migrationRec['ruleSetId'] = row[3]
        migrationRec['version'] = row[4]
        return migrationRec

    def listMigratedRuleRoles(self):
        logger = logging.getLogger('root')
        connection = self.getConnection()
        query = '''select rsml2.id resource_id, rsml2.keyword, rsml2.source, rsml2.rule_set_id, rsml2.version from rule_set rs, rule,
                    (select rsml.*, res.keyword, res.source from resources res, (select rsm.id, rsm.base_type, rsm.rule_set_id, rsm.version from rule_set_map rsm,
                    (select id, base_type, max(creation_time) latest_time from rule_set_map group by id, base_type) rsmax
                    where rsm.id = rsmax.id and rsm.base_type=rsmax.base_type and rsm.creation_time = rsmax.latest_time) rsml where res.id = rsml.id
                    and rsml.base_type='RESOURCE' and res.keyword like 'SCAppGrp:%') rsml2 where rsml2.rule_set_id = rs.ID and rsml2.version = rs.version
                    and (
                    --(rs.request_rule_id = rule.id and rule.ruletype = 'requestRule')
                    --or
                    (rs.approve_rule_id = rule.id and rule.ruletype = 'approveRule')
                    --or 
                    --(rs.provision_rule_id = rule.id and rule.ruletype = 'provisionRule') 
                    ) order by resource_Id, RULETYPE
                     '''
        cursor = connection.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        migrationRecs = []
        for row in rows:
            migrationRec = {}
            migrationRec['resourceName'] = row[1]
            migrationRec['source'] = row[2]
            migrationRec['ruleSetId'] = row[3]
            migrationRec['version'] = row[4]
            migrationRecs.append(migrationRec)
        return migrationRecs

    def insertMigrationLog(self, resourceName, source, ruleSetId, version):
        logger = logging.getLogger('root')
        print('version is %s' % version)
        connection = self.getConnection()
        sql = '''insert into rule_migration_log(resource_name, source, rule_set_id, version, migration_date, migrated_by)
                 values(:resourceName, :source, :ruleSetId, :version, sysdate, 'zhenghu')
                '''
        cursor = connection.cursor()
        result = cursor.execute(sql, {'resourceName': resourceName,
                                      'source': source, 'ruleSetId': ruleSetId, 'version': version})
        connection.commit()

    def rollbackMigrationOne(self, resourceName, source, ruleSetId, version):
        logger = logging.getLogger('root')
        logger.info('Rollback rule set for resource %s, source %s' %
                    (resourceName, source))
        connection = self.getConnection()
        sql = """update rule_set_map set rule_set_id = :ruleSetId, version = :version 
                where id = (select id from resources where type = 'role' and source = :source and keyword = :resourceName)
                and base_type = 'RESOURCE' and creation_time = (select max(creation_time) latest_time from rule_set_map group by id, base_type 
                having id = (select id from resources where type = 'role' and source = :source and keyword = :resourceName) 
                and base_type = 'RESOURCE')"""
        cursor = connection.cursor()
        result = cursor.execute(
            sql, {'resourceName': resourceName, 'source': source, 'ruleSetId': ruleSetId, 'version': version})
        connection.commit()

    def rollbackMigrationLog(self, resourceName, source, ruleSetId, version):
        connection = self.getConnection()
        sql = '''update rule_migration_log set status = 'rollback' where resource_name = :resourceName and source = :source
                 and rule_set_id = :ruleSetId and version = :version'''
        cursor = connection.cursor()
        result = cursor.execute(
            sql, {'resourceName': resourceName, 'source': source, 'ruleSetId': ruleSetId, 'version': version})
        connection.commit()

    def rollbackMigrationBatch(self):
        logger = logging.getLogger('root')
        logger.info('Rollback all rule sets')
        connection = self.getConnection()
        sql = """select resource_name, source, rule_set_id, version from rule_migration_log where (resource_name, source, migration_date) in (
              select resource_name, source, max(migration_date) latest_date from rule_migration_log group by resource_name, source
              ) and status = 'commit'"""
        cursor = connection.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        for row in rows:
            self.rollbackMigrationOne(row[0], row[1], row[2], row[3])
            self.rollbackMigrationLog(row[0], row[1], row[2], row[3])


if __name__ == '__main__':
    connector = OracleConnector(
        'dbs-dev-vm-3027.cisco.com:1526', 'EDSART', 'PrUr3#et', 'CEPMHDEV.CISCO.COM')
    #rows = connector.listMigratedRuleRoles()
    connector.insertMigrationLog('role1', 'CEPM', '1', 1)
