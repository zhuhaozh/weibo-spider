import logging
import logging.config
import threading
from concurrent.futures import thread
from time import sleep, time

import pymysql

from weibo_spider.SpiderRecovery import SpiderRecovery
from weibo_spider.WeiboIdManager import WeiboIdManager
from weibo_spider.WeiboInfoFetcher import WeiboInfoFetcher
from weibo_spider.WeiboMysqlSaver import WeiBoMysqlSaver
from weibo_spider.WeiboParser import WeiboParser


class WeiboSpiderClient(object):
    def __init__(self, initId_, limit=3000, sleepSeconds=2, recoverTimes=3):
        self.initId = initId_
        self.limit = limit
        self.sleepSeconds = sleepSeconds  # default
        self.recoverTimes = recoverTimes
        self.recoverCount = -1

        CONF_LOG = "configs/logging.conf"
        logging.config.fileConfig(CONF_LOG)  # 采用配置文件
        self.logger = logging.getLogger()

        self.recovery = None
        self.saver = WeiBoMysqlSaver.getInstanceByConf('configs/db.conf')
        self.parser = WeiboParser()
        self.fetcher = WeiboInfoFetcher()
        self.idManager = WeiboIdManager()
        self.idManager.addNewId(initId_)

    @staticmethod
    def __printSuccessMessage():
        print('--------------------------------------')
        print('---------   SUCCESSFULLY   -----------')
        print('--------------------------------------')

    def __isNotFinished(self):
        return self.idManager.hasNewId() and self.idManager.usedIdCount() < self.limit

    def setBackupToFile(self, trueOrFalse):
        self.recovery = SpiderRecovery(trueOrFalse)
        if self.recovery.isBackupExists() is False:
            self.recovery.updateBackup(self.initId, self.recovery.MODE_NEW)
        return self

    def setSleepSeconds(self, sleepSeconds):
        self.sleepSeconds = int(sleepSeconds)
        return self

    def setLimitRecords(self, limit):
        self.limit = limit
        return self

    def setRecoverTimes(self, times):
        self.recoverTimes = times
        return self

    def run(self):
        try:
            if self.idManager.isBackup(self.recovery) is False:
                self.idManager.addNewId(self.initId)

            while self.__isNotFinished():
                # while self.idManager.hasNewId():
                fans = None
                wbid = self.idManager.getNewId()
                print("clawing the id :%s" % wbid)

                usedCount = self.idManager.usedIdCount()
                leftCount = self.idManager.leftIdCount()
                fansContent = self.fetcher.fetchPageWithNum(self.fetcher.fansBaseUrl, wbid, 1)
                if leftCount + usedCount <= self.limit:
                    fans = self.parser.parseUserFansPage(fansContent)

                self.idManager.addNewIdList(fans)
                print('used id count %i,left id count %i,已使用所占百分比 %i %%，完成百分比 %i %%,'
                      % (usedCount, leftCount, (usedCount * 100 / (leftCount + usedCount)),
                         (usedCount * 100 / self.limit)))

                userInfoContent = self.fetcher.fetchPage(self.fetcher.infoBaseUrl, wbid)
                if userInfoContent is None:
                    print('userInfoContent is None !!!!')
                    continue
                wbuser = self.parser.parseUserInfo(userInfoContent, wbid)

                blogsContent = self.fetcher.fetchPageWithNum(self.fetcher.blogsBaseUrl, wbid, 1)
                if blogsContent is not None:
                    [wbuser.originalBlog, wbuser.forwardBlog, numberList] \
                        = self.parser.parseUserBlog(blogsContent)
                    if numberList is not None:
                        [wbuser.weiBoNum, wbuser.followNum, wbuser.fansNum, wbuser.verified] = numberList
                [userInfoDict, originalBlogs, forwardBlogs] = self.saver.generateWeiboUserAsDict(wbuser)

                # save to mysql
                try:
                    self.saver.saveWeiboUser(userInfoDict)
                    self.saver.saveOriginalWeiboList(originalBlogs)
                    self.saver.saveForwardWeiboList(forwardBlogs)
                except pymysql.err.InternalError:
                    self.logger.error('client persist to mysql error .')
                finally:
                    self.saver.closeConn()

                if self.recovery is not None:
                    self.recovery.updateBackup(wbid, self.recovery.MODE_OLD)  # backup
                    self.recovery.backupList(fans, self.recovery.MODE_NEW)  # backup

                sleep(self.sleepSeconds)

        except Exception as e:
            self.logger.exception(e)
            self.recoverCount += 1
        finally:

            # here to recovery from the file
            if self.__isNotFinished() \
                    and self.recoverCount <= self.recoverTimes \
                    and self.idManager.isBackup(self.recovery):
                self.logger.warning('Exceptions occurred and try to restart it .')
                self.run()
            self.__printSuccessMessage()


if __name__ == '__main__':
    initId = '1195054531'

    WeiboSpiderClient(initId) \
        .setSleepSeconds(0.05) \
        .setLimitRecords(10000) \
        .setRecoverTimes(3) \
        .setBackupToFile(True) \
        .run()
