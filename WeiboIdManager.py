import logging
import logging.config


class WeiboIdManager(object):
    def __init__(self):
        self.usedIdSet = set()
        self.newIdSet = set()
        CONF_LOG = "configs/logging.conf"
        logging.config.fileConfig(CONF_LOG)  # 采用配置文件
        self.logger = logging.getLogger()

    def isBackup(self, recovery):
        if recovery is None:
            return False
        else:
            self.usedIdSet, self.newIdSet = recovery.recover()
            if self.newIdSet == 0:
                return False
            return True

    def usedIdCount(self):
        return len(self.usedIdSet)

    def leftIdCount(self):
        return len(self.newIdSet)

    def addNewId(self, id_):
        if id_ is None:
            return
        if id_ not in self.newIdSet and id_ not in self.usedIdSet:
            self.newIdSet.add(id_)

    def addNewIdList(self, idList):
        if idList is None or len(idList) == 0:
            return
        for id_ in idList:
            self.addNewId(id_)

    def hasNewId(self):
        return len(self.newIdSet) != 0

    def getNewId(self):
        new_url = self.newIdSet.pop()
        self.usedIdSet.add(new_url)
        return new_url
