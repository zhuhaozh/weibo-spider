import logging
import logging.config
import re
from datetime import datetime
from datetime import timedelta

from bs4 import BeautifulSoup

from weibo_spider.WeiboForwardBlog import WeiboForwardBlog
from weibo_spider.WeiboUser import WeiboUser


class WeiboParser(object):
    def __init__(self):
        CONF_LOG = "configs/logging.conf"
        logging.config.fileConfig(CONF_LOG)  # 采用配置文件
        self.logger = logging.getLogger()

    def parseUserFansPage(self, content):
        logging.debug(content)
        if content is None:
            return
        soup = BeautifulSoup(content, "html.parser")
        fans = soup.findAll('table')
        retList = []

        for fan in fans:
            try:
                [portraitTd, nicknameTd] = fan.find('tr').findAll('td')
                wbid = str(nicknameTd.find('a').get('href')).split('u/')[1]
                nickname = nicknameTd.find('a').get_text()
                portraitUrl = portraitTd.find('img').get('src')
                self.logger.debug(portraitUrl)
                self.logger.debug(nickname)
                self.logger.debug(wbid)
                retList.append(wbid)
            except Exception:
                self.logger.error('parse the fans page error ')
        return retList

    def parseUserBlog(self, content):
        if content is None:
            return
        retForwardBolgs = []
        retOriginalBolgs = []

        soup = BeautifulSoup(content, "html.parser")
        # here can be error
        numberList = None
        try:
            numberListSoup = soup.find('div', class_='tip2').get_text()
            numberList = re.findall('\d+', numberListSoup)
            numberList.pop()

            verifiedInfoUrlSoup = soup.find('div', class_='ut') \
                .find('span', class_='ctt') \
                .find('img')

            if verifiedInfoUrlSoup is not None:

                verifiedInfoUrl = verifiedInfoUrlSoup.get('src')
                if '5338.gif' in verifiedInfoUrl:  # 黄V
                    numberList.append('1')
                elif '5337.gif' in verifiedInfoUrl:  # 蓝V
                    numberList.append('2')
                else:
                    numberList.append('0')
            else:
                numberList.append('0')
        except AttributeError:
            self.logger.warning('numberListSoup not found')

        try:
            owner = soup.find("span", class_="ctt").get_text().split(" ")[0]
        except AttributeError:
            self.logger.warning('not found the blog owner .')

        blogs = soup.findAll("div", class_='c')
        for blog in blogs:
            forwardBlog = blog.findAll('span', class_='cmt')
            originalBlog = blog.find('span', class_='ctt')
            if len(forwardBlog) is not 0:
                b1 = self.generateForwardBlog(blog, forwardBlog)
                b1.forwardOwner = owner
                retForwardBolgs.append(b1)
            else:
                if originalBlog is not None:  # 原创
                    b2 = self.generateOriginalBlog(blog, originalBlog)
                    b2.owner = owner
                    retOriginalBolgs.append(b2)
                else:
                    continue

        return retOriginalBolgs, retForwardBolgs, numberList

    def parseDateAndVia(self, davStr):
        if "前" in davStr:
            try:
                [day, via] = str(davStr).split(" ")
            except ValueError:
                day = davStr
                via = '空'

        else:
            # print(davStr)
            try:
                [day, time, via] = re.split(" |\xa0", davStr, 2)
                day = day + "|" + time
            except ValueError:
                [day, time] = re.split(" |\xa0", davStr, 2)
                day = day + "|" + time
                via = '空'

        return day, via

    def generateDate(self, dayStr):
        self.logger.debug(dayStr)
        today = datetime.today()
        d = today
        if "|" in dayStr:
            [day, time] = dayStr.split("|")

            # [hh, mm] = str(time).split(":")
            if '今天' in day:
                [hh, mm] = str(time).split(":")
                d = datetime(today.year, today.month, today.day, int(hh), int(mm))
            elif "月" in day:
                [MM, dd] = re.findall("\d+", day)
                [hh, mm] = str(time).split(":")
                d = datetime(today.year, int(MM), int(dd), int(hh), int(mm))
            else:
                [yy, MM, dd] = str(day).split("-")
                [hh, mm, ss] = str(time).split(":")
                d = datetime(int(yy), int(MM), int(dd), int(hh), int(mm))

        elif "秒" in dayStr:
            d = today
        elif "分钟前" in dayStr:
            [mm] = re.findall("\d+", dayStr)
            d = today + timedelta(minutes=-int(mm))

        return d

    def generateOriginalBlog(self, blog, originalBlog):
        numPatten = re.compile('\d+')
        # print(originalBlog.get_text())
        from weibo_spider.WeiboOriginalBlog import WeiboOriginalBlog
        retOBlog = WeiboOriginalBlog()
        retOBlog.content = originalBlog.get_text().replace("\'", "\'\'")

        divs = blog.findAll('div')

        if len(divs) >= 2:  # contains the pics
            picsAndInfoDiv = divs[1]

            linkas = picsAndInfoDiv.findAll("a")
            length = len(linkas)

            try:
                picUrl = linkas[length - 6].find('img').get('src')
            except AttributeError as e:
                picUrl = None

            likeNum = linkas[length - 4].get_text()
            forwardNum = linkas[length - 3].get_text()
            commentNum = linkas[length - 2].get_text()

        else:
            picsAndInfoDiv = divs[0]

            linkas = picsAndInfoDiv.findAll("a")
            length = len(linkas)

            likeNum = linkas[length - 4].get_text()
            forwardNum = linkas[length - 3].get_text()
            commentNum = linkas[length - 2].get_text()

        try:
            retOBlog.likeNum = numPatten.findall(likeNum)[0]
        except IndexError:
            self.logger.warning('IndexError : retOBlog.likeNum not exists ')
        try:
            retOBlog.forwardNum = numPatten.findall(forwardNum)[0]
        except IndexError:
            self.logger.warning('IndexError : retOBlog.forwardNum not exists ')
        try:
            retOBlog.commentNum = numPatten.findall(commentNum)[0]
        except IndexError:
            self.logger.warning('IndexError : retOBlog.commentNum not exists ')

        [dayStr, via] = self.parseDateAndVia(blog.find('span', class_='ct').get_text())
        # [day, time, via] = re.split(" |\xa0", blog.find('span', class_='ct').get_text(), 2)
        retOBlog.via = via
        retOBlog.createTime = self.generateDate(dayStr)

        retOBlog.uniCode = \
            str(retOBlog.createTime).__hash__() \
            + str(retOBlog.owner).__hash__()

        return retOBlog

    def generateForwardBlog(self, blog, forwardBlog):
        numPatten = re.compile('\d+')
        retFBlog = WeiboForwardBlog()
        forwardBlogText = forwardBlog[0].get_text()
        self.logger.debug(forwardBlogText)
        try:
            retFBlog.originalOwner = forwardBlogText.split("\xa0")[1]
        except IndexError as e:
            self.logger.warning('#generateForwardBlog: retFBlog.originalOwner IndexError')
            retFBlog.originalOwner = None
        oc = blog.find('span', class_='ctt').get_text()
        oc = str(oc).replace('\'', '\'\'')
        retFBlog.originalContent = oc
        # print("forwardCommentBlog" + forwardCommentBlog)

        # retFBlog.originalOwner = forwardBlogText.split(" ")[1]

        # numPatten.findall(forwardBlog[])
        try:
            retFBlog.originalLikeNum = numPatten.findall(forwardBlog[1].get_text())[0]
            retFBlog.originalForwardNum = numPatten.findall(forwardBlog[2].get_text())[0]
        except IndexError:
            logging.warning('cannot find the [retFBlog.originalLikeNum]')

        # for b in forwardBlog:
        #     print(b.get_text())
        # print(forwardBlog)
        # if forwardCommentBlog is not None:
        #     print(forwardCommentBlog)

        divs = blog.findAll('div')

        if len(divs) >= 3:  # contains the pics
            picsAndInfoDiv = divs[2]

            linkas = picsAndInfoDiv.findAll("a")
            length = len(linkas)

            # picUrl = linkas[length - 6].find('img').get('src')
            likeNum = linkas[length - 4].get_text()
            forwardNum = linkas[length - 3].get_text()
            commentNum = linkas[length - 2].get_text()

        else:
            try:
                picsAndInfoDiv = divs[1]

                linkas = picsAndInfoDiv.findAll("a")
                length = len(linkas)

                likeNum = linkas[length - 4].get_text()
                forwardNum = linkas[length - 3].get_text()
                commentNum = linkas[length - 2].get_text()
                try:
                    retFBlog.likeNum = numPatten.findall(likeNum)[0]
                except IndexError:
                    self.logger.warning('IndexError : retFBlog.likeNum not exists ')
                try:
                    retFBlog.forwardNum = numPatten.findall(forwardNum)[0]
                except IndexError:
                    self.logger.warning('IndexError : retFBlog.forwardNum not exists ')
                try:
                    retFBlog.commentNum = numPatten.findall(commentNum)[0]
                except IndexError:
                    self.logger.warning('IndexError : retFBlog.commentNum not exists ')

            except IndexError:
                self.logger.warning('IndexError : 微博信息获取失败')

        [dayStr, via] = self.parseDateAndVia(blog.find('span', class_='ct').get_text())
        # [day, time, via] = re.split(" |\xa0", blog.find('span', class_='ct').get_text(), 2)
        retFBlog.via = via
        retFBlog.createTime = self.generateDate(dayStr)

        retFBlog.uniCode = \
            str(retFBlog.createTime).__hash__() \
            + str(retFBlog.forwardOwner).__hash__()

        return retFBlog

    def parseUserInfo(self, content, userId):
        if content is None:
            return
        soup = BeautifulSoup(content, 'html.parser')

        classc = soup.findAll('div', class_='c')  # class='c'

        wu = WeiboUser()
        try:
            wu.portraitUrl = classc[0].find('img').get('src')  # 头像链接
        except AttributeError as e:
            logging.warning(e)
            wu.portraitUrl = None

        try:
            viplevel = re.split("：| ", classc[1].get_text(), 2)[1]  # vip 等级， 0未开通
            # print(viplevel)
            if '未开通' in viplevel:
                viplevel = 0
            else:
                viplevel = int(re.search("\d+", viplevel).group()[0])
            wu.vip = viplevel
        except IndexError:
            self.logger.warning('#parseUserInfo : IndexError viplevel error')

        try:
            infoSoup = classc[2]

            wu.wbid = userId  # id
            tags = infoSoup.findAll('a')
            infoList = str(infoSoup).split('<br/>')
            for info in infoList:
                if ':' in info:
                    # print("info", info)
                    try:
                        [k, v] = info.split(":")

                        if '生日' in k:
                            wu.birthday = v
                        elif '性别' in k:
                            wu.gender = v
                        elif '地区' in k:
                            wu.address = v
                        elif '昵称' in k:
                            wu.nickname = v
                        elif '感情状况' in k:
                            wu.relationshipStatus = k
                    except Exception:
                        self.logger.warning('#parseUserInfo :info parse error ')

            atags = []
            for tag in tags:
                tagtext = tag.get_text()
                if '更多' not in tagtext:
                    atags.append(tagtext)

            wu.tags = atags
        except IndexError:
            self.logger.warning('user info not exist .')

        # self.logger.info(wu)
        return wu


if __name__ == '__main__':
    ss = '2134'
    print(ss.__hash__())
