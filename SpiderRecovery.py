import logging
import logging.config


class SpiderRecovery(object):
    def __init__(self, backupToFile):
        self.MODE_NEW = 1
        self.MODE_OLD = 0
        self.crashDate = None
        self.usedData = set()
        self.newData = set()
        self.backupToFile = backupToFile
        self.backupFilePath = 'backups/weibo.bak'
        CONF_LOG = "configs/logging.conf"
        logging.config.fileConfig(CONF_LOG)  # 采用配置文件
        self.logger = logging.getLogger()

    def __parseLine(self, line):
        import re
        pattenNum = re.compile('\d+')
        pattenMode = re.compile('\{\[\(\d+\)\]\}')
        pattenData = re.compile('.*\{\[\(')

        modeOnce = re.search(pattenMode, line).group(0)
        dataOnce = re.search(pattenData, line).group(0)
        if modeOnce is None and dataOnce is None:  # 匹配失败
            return None

        return dataOnce[0: len(dataOnce) - 3], re.search(pattenNum, modeOnce).group(0)

    def writeToFile(self, data, mode):
        # if not os.path.exists(self.backupFilePath):
        try:
            backupFile = open(self.backupFilePath, 'a')
        except Exception:
            self.logger.warning('backup path does not exist , please create it ')
            return

        data = str(data)
        backupFile.write(data)  # 写入数据
        backupFile.write('{[(' + str(mode) + ')]}')  # 写入mode
        backupFile.write('\n')  # 数据分隔符
        backupFile.close()

    def recoverFromFile(self):
        usedSet = set()
        newSet = set()
        rf = open(self.backupFilePath, 'r')
        for line in rf.readlines()[::-1]:
            (data, mode) = self.__parseLine(line)
            mode = int(mode)
            if data not in usedSet and data not in newSet:  # 如果数据已经存在在其中一个集合，代表已经存在最新记录
                if mode == self.MODE_NEW:
                    newSet.add(data)
                elif mode == self.MODE_OLD:
                    usedSet.add(data)
        self.usedData = usedSet
        self.newData = newSet
        self.logger.info('recovered %d data ' % (len(usedSet) + len(self.newData)))
        return usedSet, newSet

    def isBackupExists(self):
        import os
        return os.path.exists(self.backupFilePath)

    def recover(self):
        if self.backupToFile is True:
            self.recoverFromFile()
            if self.isBackupExists():
                self.logger.info('backup file exists , starting recover from this file ...')
                self.usedData, self.newData = self.recoverFromFile()
                # return True
            else:
                self.logger.info('backup file not found ...')
                # return False

        return self.usedData, self.newData
        # newSet = set()
        # return usedSet, newSet

    def updateBackup(self, data):
        # data = self.newData.pop()
        # print(data)
        self.usedData.add(data)
        # print('new data set : ', self.newData)
        # print(data)
        if data in self.newData:
            self.newData.remove(data)
        if self.backupToFile is True:
            self.writeToFile(data, self.MODE_OLD)

    def backup(self, data):
        if data is None:
            return
        # if data not in self.usedData and data not in self.newData:
        self.newData.add(data)
        if self.backupToFile is True:
            self.writeToFile(data, self.MODE_NEW)

    def backupList(self, dataList):
        if dataList is None or len(dataList) == 0:
            return
        for data in dataList:
            self.backup(data)

    def printStatus(self):
        print("new data : ", self.newData)
        print("used data : ", self.usedData)

# if __name__ == '__main__':
# pattenNum = re.compile('\d+')
# pattenMode = re.compile('\{\[\(\d+\)\]\}')
# pattenData = re.compile('.*\{\[\(')
#
# string = '123456{[(1)]}'
#
# modeOnce = re.search(pattenMode, string).group(0)
# dataOnce = re.search(pattenData, string).group(0)
#
# print(re.search(pattenNum, modeOnce).group(0))
# print(dataOnce[0: len(dataOnce) - 3])
