import logging
import logging.config


class SpiderRecovery(object):
    """
    爬虫的备份恢复类
    """

    def __init__(self, isBackupToFile):
        self.MODE_NEW = 1
        self.MODE_OLD = 0
        self.crashDate = None
        self.usedData = set()
        self.newData = set()
        self.isBackupToFile = isBackupToFile
        self.__backupFilePath = self.__readLatestBackupFile()
        CONF_LOG = "configs/logging.conf"
        logging.config.fileConfig(CONF_LOG)  # 采用配置文件
        self.__logger = logging.getLogger()

    def __readLatestBackupFile(self):
        """
        从备份文件列表中恢复最新的备份文件信息
        :return: 返回最新的备份文件路径
        """
        f = open('backups/latest-backup-file', 'r')
        lines = f.readlines()
        if len(lines) == 0:
            from datetime import datetime
            fn = 'backups/backup-' + str(datetime.now()) + '.bak'
            self.__writeLatestBackupFile(fn)
        else:
            fn = lines[-1]
        return fn.lstrip().rstrip()

    @staticmethod
    def __writeLatestBackupFile(backupFile):
        """
        将最新的备份文件信息写入备份文件列表
        :param backupFile: 需要被写入备份文件列表的文件路径

        """
        f = open('backups/latest-backup-file', 'a')
        f.write(backupFile)
        f.write('\n')

    @staticmethod
    def __parseLine(line):
        """
        解析从备份文件中的每一行信息
        :param line: line
        :return: 如果匹配失败返回None，否则返回[data,mode]
        """
        import re
        pattenNum = re.compile('\d+')
        pattenMode = re.compile('\{\[\(\d+\)\]\}')
        pattenData = re.compile('.*\{\[\(')

        modeOnce = re.search(pattenMode, line).group(0)
        dataOnce = re.search(pattenData, line).group(0)
        if modeOnce is None and dataOnce is None:  # 匹配失败
            return None

        return dataOnce[0: len(dataOnce) - 3], re.search(pattenNum, modeOnce).group(0)

    def writeToFile(self, path, data, mode):
        """ writeToFile
        将data于mode信息写入文件
        :param path: 备份文件路径
        :param data: data
        :param mode: mode
        """
        try:
            backupFile = open(path, 'a')
            data = str(data)
            backupFile.write(data)  # 写入数据
            backupFile.write('{[(' + str(mode) + ')]}')  # 写入mode
            backupFile.write('\n')  # 数据分隔符
            backupFile.close()

        except Exception:
            self.__logger.warning('backup path does not exist , please create it ')

    def optimizeBackupFile(self):
        """
        优化备份文件信息
        缩短备份文件
        """
        from datetime import datetime

        bfp = 'backups/update-test-backup' + str(datetime.now()) + '.bak'
        for newdata in self.newData:
            self.writeToFile(bfp, newdata, self.MODE_NEW)
        for useddata in self.usedData:
            self.writeToFile(bfp, useddata, self.MODE_OLD)
        self.__backupFilePath = bfp
        self.__writeLatestBackupFile(bfp)

    def recoverFromFile(self):
        """
        从备份文件中恢复信息
        :return:
        """
        usedSet = set()
        newSet = set()
        rf = open(self.__backupFilePath, 'r')
        self.__logger.info('from file : %s' % self.__backupFilePath)
        lines = rf.readlines()
        for line in lines[::-1]:
            (data, mode) = self.__parseLine(line)
            mode = int(mode)
            if data not in usedSet and data not in newSet:  # 如果数据已经存在在其中一个集合，代表已经存在最新记录
                if mode == self.MODE_NEW:
                    newSet.add(data)
                elif mode == self.MODE_OLD:
                    usedSet.add(data)
        self.usedData = usedSet
        self.newData = newSet
        totalData = len(usedSet) + len(self.newData)
        self.__logger.info('Recovered %d data from %d lines' % (totalData, len(lines)))
        if totalData == 0:
            self.__logger.info('Backup is empty。')
        else:
            self.__logger.info('Recovered  : UsedData：%i , NewData：%i' % (
                len(self.usedData), len(self.newData)))

        if totalData + 10000 < len(lines):  # 如果两者相差10000条数据
            self.__logger.info('The backup file need to be optimized , it will start now .')
            self.optimizeBackupFile()
        return usedSet, newSet

    def isBackupExists(self):
        """
        判断备份当前的最新备份文件是否存在
        :return:
        """
        import os
        return os.path.exists(self.__backupFilePath)

    def recover(self):
        """
        外部调用的恢复 api
        如果可恢复则恢复
        :return: 返回恢复后的数据
        """
        if self.isBackupToFile is True:
            # self.recoverFromFile()
            if self.isBackupExists():
                self.__logger.info('backup file exists , starting recover from this file ...')
                self.usedData, self.newData = self.recoverFromFile()
                # return True
            else:
                self.__logger.info('backup file not found ...')
                # return False

        return self.usedData, self.newData

    def updateBackup(self, data, _mode):
        """
        更新备份信息，将数据置旧
        :param _mode:
        :param data:
        :return:
        """
        if data is None:
            pass
        if _mode == self.MODE_OLD:
            self.usedData.add(data)
            if data in self.newData:
                self.newData.remove(data)
            self.newData.add(data)
        if _mode == self.MODE_OLD or self.MODE_NEW:
            if self.isBackupToFile is True:
                self.writeToFile(self.__backupFilePath, data, _mode)

    def backupList(self, dataList, _mode):
        """

        :param _mode:
        :param dataList:
        :return:
        """
        if dataList is None or len(dataList) == 0:
            return
        for data in dataList:
            self.updateBackup(data, _mode)

    def printStatus(self):
        print("new data : ", len(self.newData))
        print("used data : ", len(self.usedData))


if __name__ == '__main__':
    r = SpiderRecovery(True)
    # r.backup('123')
    # r.updateBackup('123')

    r.recoverFromFile()
    r.printStatus()
    # r.optimizeBackupFile()
    r.recoverFromFile()
    r.printStatus()
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
