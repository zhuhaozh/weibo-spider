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

        # print(param)
        r = requests.post(url=url, data=param)

        if '搜索' in r.text:
            print('用户%s，登陆成功' % self.username)
        else:
            print('登陆不成功')
        return r


class CookiesPool(object):
    """ CookiesPool
     缓存连接池，用于管理多个账号的缓存信息，均匀分配每个账号的使用次数。
     以达到有效解决微博访问403的问题，目前测试1小时，使用5个账号信息，未出现过403

     需要配置参数 :
     1. maxSize : 设置最大的缓存个数
     2. continuous : 每个缓存连续使用的次数，默认50次后 将该缓存失效
     3. force : 在所有缓存都失效后是否sleep一段时间
     4. sleepSecs : 在设置force后生效，设置sleep的时间
    """

    def __init__(self, configFile='configs/accounts-list.conf',
                 maxSize=-1, continuous=50, force=True, sleepSecs=5.0):
        CONF_LOG = "configs/logging.conf"
        logging.config.fileConfig(CONF_LOG)  # 采用配置文件
        self.logger = logging.getLogger()

        self.__configFile = configFile
        self.__cookiesPool = list()

        self.__current = -1
        self.__last = -1
        self.__continuousUseCount = 0

        self.__sleepSecs = sleepSecs

        self.size = 0
        self.__maxSize = maxSize
        self.force = force
        self.__continuous = continuous

        self.__invalidatedCookies = None
        self.__loadConfigure()

    def __loadConfigure(self):
        if self.__isPersistCookies():
            self.__recCookies()
        else:
            if os.path.exists(self.__configFile):
                counter = 0
                conf = open(self.__configFile, 'r')
                for line in conf.readlines():
                    if line.rstrip().lstrip() == '':
                        continue
                    if self.__maxSize != -1 and self.__maxSize >= counter:
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
                        self.__cookiesPool.append(r.request.headers)
                        counter += 1
                    except ValueError:
                        self.logger.error('配置文件错误！格式为：【账号:密码】，冒号为英文冒号')
                self.persistCookies()
            else:
                self.logger.warning('headers conf file does\'t exists.')

        self.size = len(self.__cookiesPool)
        self.__invalidatedCookies = self.__initArray(self.size)

    @staticmethod
    def __initArray(length):
        arr = []
        for i in range(0, length):
            arr.append(0)
        return arr

    def getCookies(self):
        """getCookies()
        获取缓存池中的有效cookies
        1. 如果存在没有失效的缓存，则缓存第一个遍历到的未失效的缓存
        2. 如果缓存都已失效，则判断force属性：
            a)如果 force 为true 则sleep一段时间后随机返回一个cookies
            b)如果 force 为false 则直接返回一个cookies

        :return: cookies
        """
        print(self.__invalidatedCookies)
        self.__last = self.__current
        index = -1
        for i in range(0, len(self.__invalidatedCookies)):
            if self.__invalidatedCookies[i] == 0:  # 未被休眠
                if i == self.__last:  # 如果于上一次使用的为同一个cookies
                    self.__continuousUseCount += 1
                    # self.invalidateCurrent()
                    print('连续使用次数:%s : ' % self.__continuousUseCount, self.__continuous)
                    if self.__continuousUseCount >= self.__continuous:  # 如果连续使用的次数大于40，则继续选择下一个
                        index = i
                        self.invalidateCurrent()
                        continue

                else:
                    self.__current = i
                    self.__continuousUseCount = 0
                self.logger.info("use pool index : %s" % i)
                self.__invalidateReduce()
                return self.__cookiesPool[i]

        # 如果可以执行到这里，代表所有的资源都已失效
        if self.force:
            from time import sleep
            self.logger.warning('cookiesPool中的所有资源都已失效。请等待%s秒' % self.__sleepSecs)
            sleep(self.__sleepSecs)
        if index == -1:
            import random
            index = random.randint(0, self.size - 1)
        self.logger.info("use pool index : %s" % index)
        self.__invalidateReduce()
        return self.__cookiesPool[index]

    def __invalidateReduce(self):
        """
        减少每个失效缓存的死亡时间
        :return:
        """
        for i in range(self.size):
            if self.__invalidatedCookies[i] != 0:
                self.__invalidatedCookies[i] -= 1

    def invalidateCurrent(self):
        """ invalidateCurrent
        使当前缓存失效
        :return:
        """
        if self.size > 10:  # 如果有10个以上的cookies 则不需要中途休眠
            self.__invalidatedCookies[self.__current] = self.__continuous * (self.size - 1)
        else:
            self.__invalidatedCookies[self.__current] = (self.__continuous + 1) * (self.size - 1)

    # TODO :缓存缓存连接池的持久化，待完成。完成该功能后 -> V0.699
    @staticmethod
    def __isPersistCookies():
        import os
        cachadir = 'cache/persistcookies/'
        fns = os.listdir(cachadir)
        return len(fns) != 0

    def __recCookies(self):
        import os
        cachadir = 'cache/persistcookies/'
        fns = os.listdir(cachadir)
        for fn in fns:
            f = open(cachadir + fn, 'r')
            cookiesDict = dict()
            lines = f.readlines()
            for line in lines:
                if ':' in line:
                    k, v = line.split(':')
                    k = str(k).rstrip().lstrip()
                    v = str(v).rstrip().lstrip()
                    cookiesDict[k] = v
            self.__cookiesPool.append(cookiesDict)
        self.logger.info('发现%d个缓存数据，并已成功使用' % len(self.__cookiesPool))

    def persistCookies(self):
        """
        持久化 cookies
        :return:
        """
        from datetime import datetime
        cachadir = 'cache/persistcookies/'
        for cookies in self.__cookiesPool:
            filename = cachadir + 'cache-' + str(datetime.now())
            f = open(filename, 'w')
            for k, v in cookies.items():
                f.writelines(k + ":" + v + "\n")
            f.close()


class WeiboInfoFetcher(object):
    def __init__(self, failedTryNum=-1):
        self.fansBaseUrl = 'http://weibo.cn/%s/fans?page=%s'
        self.blogsBaseUrl = 'http://weibo.cn/%s?page=%s'
        self.infoBaseUrl = 'http://weibo.cn/%s/info'
        self.failedTryNum = failedTryNum
        self.failedTryCounter = 0
        self.cookiesPool = CookiesPool(sleepSecs=3, continuous=50)
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
            if self.failedTryNum < self.failedTryCounter:
                self.failedTryCounter += 1
                self.fetchPageWithNum(baseUrl, userId, pageNum)
                self.logger.info('%s获取失败，继续尝试,已经尝试次数%s'
                                 % baseUrl, self.failedTryCounter)

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
                self.logger.info('%s获取失败，继续尝试,已经尝试次数%s'
                                 % baseUrl, self.failedTryCounter)

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
        # print(cookies)
        resp = requests.get(url, headers=cookies)
        # print(resp.text)
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
