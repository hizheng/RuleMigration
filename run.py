#!/usr/bin/python

import sys
import logging
import logging.config
from rulemigration.manager.manager import Manager


def main():
    lifeCycle = 'dev'
    command = None
    CORRECT_LIFE_CYCLES = ['dev', 'stage', 'prod']
    logging.config.fileConfig('./config/logging.properties')
    logger = logging.getLogger('root')
    if(len(sys.argv) == 2):
        if(sys.argv[1] == '-h' or sys.argv[1] == 'help'):
            usage = '''Use Example:
            help: python run.py -h/help
            migration mode: python run.py dev/stage/prod 
            migration one mode: python run.py dev/stage/prod -c commit [resourceName]
            rollback mode: python run.py dev/stage/prod -c rollback [resourceName]
            '''
            print(usage)
            exit(0)
        lifeCycle = sys.argv[1]
    elif(len(sys.argv) == 4):
        lifeCycle = sys.argv[1]
        if(sys.argv[2] == '-c'):
            command = sys.argv[3]
        else:
            print('[ERROR]:Invalid args, %s' % sys.argv)
            logger.error('[ERROR]:Invalid args, %s' % sys.argv)
            exit(1)
    else:
        print('[ERROR]:Invalid args, %s' % sys.argv)
        logger.error('[ERROR]:Invalid args, %s' % sys.argv)
        exit(2)

    if(lifeCycle not in CORRECT_LIFE_CYCLES):
        print('[ERROR]:Invalid lifeCycle, %s' % lifeCycle)
        logger.error("ERROR: Invalid life cycle %s" % lifeCycle)
        exit(3)

    manager = Manager(lifeCycle)
    manager.initRuleMigrator()
    if(command == 'rollback'):
        if(len(sys.argv) == 4):
            manager.doRollback()
        elif(len(sys.argv) == 5):
            resourceName = sys.argv[4]
            source = 'CEPM'
            manager.doRollback(resourceName, source)
        elif(len(sys.argv) == 6):
            resourceName = sys.argv[4]
            source = sys.argv[5]
            manager.doRollback(resourceName, source)
        else:
            print('[ERROR]:Invalid args, %s' % sys.argv)
            logger.error('[ERROR]:Invalid args, %s' % sys.argv)
            exit(4)
    elif(command == 'commit'):
        if(len(sys.argv) == 5):
            resourceName = sys.argv[4]
            source = 'CEPM'
            manager.doMigrationForRole(resourceName, source)
        elif(len(sys.argv) == 6):
            resourceName = sys.argv[4]
            source = sys.argv[5]
            manager.doMigrationForRole(resourceName, source)
        else:
            print('[ERROR]:Invalid args, %s' % sys.argv)
            logger.error('[ERROR]:Invalid args, %s' % sys.argv)
            exit(4)
    else:
        manager.doMigrations()


if __name__ == '__main__':
    main()
