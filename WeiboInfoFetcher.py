import logging, logging.config
import os

import requests


class WeiboInfoFetcher(object):
    def __init__(self):
        self.headers = {}
        self.fansBaseUrl = 'http://weibo.cn/%s/fans?page=%s'
        self.blogsBaseUrl = 'http://weibo.cn/%s?page=%s'
        self.infoBaseUrl = 'http://weibo.cn/%s/info'
        self.confHeaders()

        CONF_LOG = "configs/logging.conf"
        logging.config.fileConfig(CONF_LOG)  # 采用配置文件
        self.logger = logging.getLogger()

    def confHeaders(self):

        confFIle = 'configs/weibo_url_headers.conf'
        if os.path.exists(confFIle):
            conf = open(confFIle, 'r')
            self.headers = dict()
            for line in conf.readlines():
                [k, v] = line.split(":")
                k = str(k).rstrip().replace('\n', '')
                v = str(v).lstrip().replace('\n', '')
                self.headers[k] = v
        else:
            self.logger.warning('headers conf file does\'t exists.')

    def fetchPageWithNum(self, baseUrl, userId, pageNum):

        url = baseUrl % (userId, pageNum)
        resp = requests.get(url, headers=self.headers)
        if resp.status_code is 200:
            return str(resp.content, 'utf-8')

    def fetchPage(self, baseUrl, userId):
        url = baseUrl % userId
        resp = requests.get(url, headers=self.headers)
        if resp.status_code is 200:
            return str(resp.content, 'utf-8')


if __name__ == '__main__':
    pass
    # fetcher = WeiboInfoFetcher()
    # r = fetcher.getUserFansPage("2413995587")
