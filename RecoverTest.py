from weibo_spider.SpiderRecovery import SpiderRecovery

if __name__ == '__main__':
    recovery = SpiderRecovery(True)
    dataList = []
    for i in range(30):
        dataList.append(str(1000 + i))

    # print(dataList)
    recovery.backupList(dataList)
    # recovery.printStatus()
    # for i in range(10):
    #     recovery.updateBackup()
    # recovery.recoverFromFile()

