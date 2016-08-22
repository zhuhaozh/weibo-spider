import logging
import logging.config
import os

import requests


class WeiboLogin(object):
    def __init__(self):
        self.username = None
        self.password = None
        self.captcha = None
        self.captchaPicDir = ''
        self.baseLoginUrl = 'http://login.weibo.cn/login/'
        # login params
        self.passwordName = None
        self.captchaId = None
        self.vk = None
        self.urlParams = None

    def initLoginParams(self):
        r = requests.get(self.baseLoginUrl)
        from bs4 import BeautifulSoup
        content = r.text
        soup = BeautifulSoup(content, 'html.parser')
        captchaUrl = soup.find('img').get('src')
        captchaId = captchaUrl.split('cpt=')[1]
        ipts = soup.findAll('input')
        passwordName = ipts[1].get('name')
        urlParams = soup.find('form').get('action')
        vk = ''
        for ipt in ipts:
            if ipt.get('name') == 'vk':
                vk = ipt.get('value')

        # set login params
        self.saveCaptcha(captchaUrl)
        self.passwordName = passwordName
        self.captchaId = captchaId
        self.vk = vk
        self.urlParams = urlParams
        return self

    def saveCaptcha(self, captchaUrl):
        import datetime
        captchaUrlPath = self.captchaPicDir + 'captcha_+' + str(datetime.datetime.now()) + '.jpg'
        f = open(captchaUrlPath, 'wb')
        r = requests.get(captchaUrl, stream=True)
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
                f.flush()
        f.close()
        print('验证码已保存在：' + captchaUrlPath)

    def setUsername(self, username):
        self.username = username
        return self

    def setPassword(self, password):
        self.password = password
        return self

    def setCaptcha(self, captcha):
        self.captcha = captcha
        return self

    def setCaptchaPicPath(self, captchaPicPath):
        self.captchaPicDir = captchaPicPath
        return self

    def login(self):
        param = {
            'mobile': self.username,
            self.passwordName: self.password,
            'code': self.captcha,
            'remember': 'on',
            'backURL': 'http%3A%2F%2Fweibo.cn%2F',
            'backTitle': '微博',
            'tryCount': '',
            'vk': self.vk,
            'capId': self.captchaId,
            'submit': '登录',
        }
        url = 'http://login.weibo.cn/login/' + self.urlParams

        print(param)
        r = requests.post(url=url, data=param)

        if '搜索' in r.text:
            print('用户%s，登陆成功' % self.username)
        else:
            print('登陆不成功')
            print(r.text)
        return r


class CookiesPool(object):
    def __init__(self, configFile='configs/weibo_url_headers.conf',
                 maxSize=-1, force=True, continuous=50, sleepSecs=60.0):
        CONF_LOG = "configs/logging.conf"
        logging.config.fileConfig(CONF_LOG)  # 采用配置文件
        self.logger = logging.getLogger()

        self.configFile = configFile
        self.cookiesPool = list()

        self.current = -1
        self.last = -1
        self.continuousUseCount = 0

        self.sleepSecs = sleepSecs

        self.size = 0
        self.maxSize = maxSize
        self.force = force
        self.continuous = continuous

        self.invalidatedCookies = None
        self.loadConfigure()

    def loadConfigure(self):

        if os.path.exists(self.configFile):
            counter = 0
            conf = open(self.configFile, 'r')
            for line in conf.readlines():
                if line.rstrip().lstrip() == '':
                    continue
                if self.maxSize != -1 and self.maxSize >= counter:
                    break
                # headers = dict()
                try:
                    [username, password] = line.split(":")
                    username = str(username).lstrip().rstrip().replace('\n', '')
                    password = str(password).lstrip().rstrip().replace('\n', '')

                    weiboLogin = WeiboLogin() \
                        .setUsername(username) \
                        .setPassword(password) \
                        .initLoginParams()
                    print('请输入验证码：')
                    captcha = input()
                    r = weiboLogin.setCaptcha(captcha).login()
                    self.cookiesPool.append(r.request.headers)
                    counter += 1
                except ValueError:
                    self.logger.error('配置文件错误！格式为：【账号:密码】，冒号为英文冒号')
            self.size = len(self.cookiesPool)
            self.invalidatedCookies = self.__initArray(self.size)
        else:
            self.logger.warning('headers conf file does\'t exists.')

    @staticmethod
    def __initArray(length):
        arr = []
        for i in range(0, length):
            arr.append(0)
        return arr

    def getCookies(self):
        """
        只返回未失效的cookies
        :return:
        """
        print(self.invalidatedCookies)
        self.last = self.current
        index = -1
        for i in range(0, len(self.invalidatedCookies)):
            if self.invalidatedCookies[i] == 0:  # 未被休眠
                if i == self.last:  # 如果于上一次使用的为同一个cookies
                    self.continuousUseCount += 1
                    # self.invalidateCurrent()
                    print('连续使用次数:%s : ' % self.continuousUseCount, self.continuous)
                    if self.continuousUseCount >= self.continuous:  # 如果连续使用的次数大于40，则继续选择下一个
                        index = i
                        self.invalidateCurrent()
                        continue

                else:
                    self.current = i
                    self.continuousUseCount = 0
                self.logger.info("use pool index : %s" % i)
                self.invalidateReduce()
                return self.cookiesPool[i]

        # 如果可以执行到这里，代表所有的资源都已失效
        if self.force:
            from time import sleep
            self.logger.warning('cookiesPool中的所有资源都已失效。请等待%s秒' % self.sleepSecs)
            sleep(self.sleepSecs)
        if index == -1:
            import random
            index = random.randint(0, self.size - 1)
        self.logger.info("use pool index : %s" % index)
        self.invalidateReduce()
        return self.cookiesPool[index]

    def invalidateReduce(self):
        for i in range(self.size):
            if self.invalidatedCookies[i] != 0:
                self.invalidatedCookies[i] -= 1

    def invalidateCurrent(self):
        if self.size > 10:  # 如果有10个以上的cookies 则不需要中途休眠
            self.invalidatedCookies[self.current] = self.continuous * (self.size - 1)
        else:
            self.invalidatedCookies[self.current] = (self.continuous + 1) * (self.size - 1)


class WeiboInfoFetcher(object):
    def __init__(self, failedTryNum=-1):
        self.fansBaseUrl = 'http://weibo.cn/%s/fans?page=%s'
        self.blogsBaseUrl = 'http://weibo.cn/%s?page=%s'
        self.infoBaseUrl = 'http://weibo.cn/%s/info'
        self.failedTryNum = failedTryNum
        self.failedTryCounter = 0
        self.cookiesPool = CookiesPool(sleepSecs=0.1, continuous=50)
        if self.failedTryNum == -1:
            self.failedTryNum = self.cookiesPool.size

        CONF_LOG = "configs/logging.conf"
        logging.config.fileConfig(CONF_LOG)  # 采用配置文件
        self.logger = logging.getLogger()

    def fetchPageWithNum(self, baseUrl, userId, pageNum):

        url = baseUrl % (userId, pageNum)
        resp = requests.get(url, headers=self.cookiesPool.getCookies())
        if resp.status_code is 200:
            return str(resp.content, 'utf-8')
        else:
            self.cookiesPool.invalidateCurrent()
            self.fetchPageWithNum(baseUrl, userId, pageNum)

    def fetchPage(self, baseUrl, userId):
        url = baseUrl % userId
        resp = requests.get(url, headers=self.cookiesPool.getCookies())
        if resp.status_code is 200:
            return str(resp.content, 'utf-8')
        else:
            self.cookiesPool.invalidateCurrent()
            if self.failedTryNum < self.failedTryCounter:
                self.failedTryCounter += 1
                self.fetchPage(baseUrl, userId)
                print('继续尝试,已经尝试次数%s' % self.failedTryCounter)

    def test(self):
        resp = requests.get("http://weibo.cn/2413995587/profile",
                            headers=self.cookiesPool.getCookies())
        print(resp.status_code)
        if resp.status_code != 200:
            self.cookiesPool.invalidateCurrent()
            if self.failedTryNum > self.failedTryCounter:
                self.failedTryCounter += 1
                print('继续尝试,已经尝试次数: %s' % self.failedTryCounter)
                self.test()
            else:
                print('已达到尝试次数%s' % self.failedTryCounter)

        else:
            self.failedTryCounter = 0

    def test1(self):
        url = 'http://weibo.cn/1195054531/fans'
        cookies = self.cookiesPool.getCookies()
        print(cookies)
        resp = requests.get(url, headers=cookies)
        print(resp.text)
        return resp


if __name__ == '__main__':
    def testCookiesPoolOffline():
        pool = CookiesPool(sleepSecs=0.3, continuous=50)
        pool.getCookies()
        for i in range(0, 1200):
            pool.getCookies()
        pool.invalidateCurrent()
        pool.getCookies()


    def testCookiesPoolOnline():
        fetcher = WeiboInfoFetcher()
        fetcher.test()


    def login():
        return WeiboLogin().login()


    fetcher = WeiboInfoFetcher()
    fetcher.test1()
    # userInfoContent = fetcher.fetchPage(fetcher.infoBaseUrl, '1195054531')

# testCookiesPoolOffline()
# testCookiesPoolOnline()


# testCookiesPoolOffline()
