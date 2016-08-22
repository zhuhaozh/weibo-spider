import logging
import logging.config

import pymysql


class WeiBoMysqlSaver(object):
    @staticmethod
    def getInstanceByConf(confFile):
        file = open(confFile, 'r')
        confDict = {}
        for i in range(5):
            line = file.readline()
            line = line.replace(' ', '')
            line = line.replace('\n', '')
            try:
                [k, v] = line.split(":")
                confDict[k] = v

            except Exception:
                logging.error(confFile, 'configure file properties error ')

        try:
            host = confDict['host']
            port = int(confDict['port'])
            user = confDict['user']
            passwd = confDict['passwd']
            db = confDict['db']
            return WeiBoMysqlSaver(host=host, port=port, user=user, passwd=passwd, db=db)

        except KeyError as e:
            logging.error(e)

    def __init__(self, host, port, user, passwd, db):
        CONF_LOG = "configs/logging.conf"
        logging.config.fileConfig(CONF_LOG)  # 采用配置文件
        self.logger = logging.getLogger()
        self.conn = None

        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.db = db

    def closeConn(self):
        if self.conn is not None:
            self.conn.close()

    def __getConnect(self):
        conn = pymysql.connect(host=self.host, port=self.port,
                               user=self.user, passwd=self.passwd, db=self.db)
        conn.set_charset('utf8')
        return conn

    def __cursorUtf8Wrapper(self, cursor):
        cursor.execute('SET NAMES utf8mb4;')
        cursor.execute('SET CHARACTER SET utf8mb4;')
        cursor.execute('SET character_set_connection=utf8mb4;')
        return cursor

    def test(self):

        sql = '''INSERT INTO weibo_original_blog(
        create_time, like_num, comment_num, forward_num,
        via, owner_id, content, pic_num)
    VALUES('2016-08-18 18:111:00', '0', '0', '0', '来自iPhone 6', '张铭恩最好的宝宝',
           '#张铭恩_##张铭恩张副官# 在雷克赛得坐蒸汽小火车，看到山洞宝宝直接串戏到老九门@张铭恩_ 233🌚🌚🌚有幸看到换车头的过程还喷着气，本来很高兴的拍照然后被呼了一脸⋯⋯呛死我了 英国·雷克赛得', '-100')
           '''

        conn = self.__getConnect()
        cursor = conn.cursor()
        cursor.execute('SET NAMES utf8mb4;')
        cursor.execute('SET CHARACTER SET utf8mb4;')
        cursor.execute('SET character_set_connection=utf8mb4;')

        cursor.execute(sql)
        conn.commit()
        res = cursor.fetchall()

        return res

    def generateWeiboUserAsDict(self, weiboUserInfo):
        forwardBlogs = list()
        originalBlogs = list()
        """
        self.wbid = None
        self.nickname = None
        self.gender = None
        self.birthday = None
        self.address = None
        self.portraitUrl = None
        self.weiBoNum = 0
        self.fansNum = 0
        self.followNum = 0
        self.verified = 0
        self.vip = 0
        self.tags = []
        self.originalBlog = []
        self.forwardBlog = []
        self.relationshipStatus = None
          """
        userInfoDict = {
            'wbid': weiboUserInfo.wbid,
            'nickname': weiboUserInfo.nickname,
            'portraitUrl': weiboUserInfo.portraitUrl,
            'gender': weiboUserInfo.gender,
            'birthday': weiboUserInfo.birthday,
            'address': weiboUserInfo.address,
            'verified': weiboUserInfo.verified,
            'weiboNum': weiboUserInfo.weiboNum,
            'fansNum': weiboUserInfo.fansNum,
            'followNum': weiboUserInfo.followNum,
            'vip': weiboUserInfo.vip,
            'relationshipStatus': weiboUserInfo.relationshipStatus,
            'tags': ','.join(weiboUserInfo.tags)
        }

        """
        self.createTime = None
        self.likeNum = 0
        self.commentNum = 0
        self.forwardNum = 0
        self.originalLikeNum = 0
        self.originalCommentNum = 0
        self.originalForwardNum = 0
        self.via = None
        self.originalOwner = None  # 原作者
        self.originalContent = None
        self.forwardOwner = None
        self.forwardContent = None

        """

        for forwardBlog in weiboUserInfo.forwardBlog:
            tmp = {'createTime': forwardBlog.createTime,
                   'likeNum': forwardBlog.likeNum,
                   'commentNum': forwardBlog.commentNum,
                   'forwardNum': forwardBlog.forwardNum,
                   'picNum': forwardBlog.picNum,
                   'originalLikeNum': forwardBlog.originalLikeNum,
                   'originalCommentNum': forwardBlog.originalCommentNum,
                   'originalForwardNum': forwardBlog.originalForwardNum,
                   'originalPicNum': forwardBlog.originalPicNum,
                   'via': forwardBlog.via,
                   'originalOwner': forwardBlog.originalOwner,
                   'originalContent': forwardBlog.originalContent,
                   'forwardOwner': forwardBlog.forwardOwner,
                   'forwardContent': forwardBlog.forwardContent,
                   'uniCode': forwardBlog.uniCode
                   }
            forwardBlogs.append(tmp)

        for originalBlog in weiboUserInfo.originalBlog:
            tmp = {'createTime': originalBlog.createTime,
                   'likeNum': originalBlog.likeNum,
                   'commentNum': originalBlog.commentNum,
                   'forwardNum': originalBlog.forwardNum,
                   'via': originalBlog.via,
                   'owner': originalBlog.owner,
                   'content': originalBlog.content,
                   'picNum': originalBlog.picNum,
                   'uniCode': originalBlog.uniCode

                   }
            originalBlogs.append(tmp)

        self.logger.debug(userInfoDict)
        self.logger.debug(originalBlogs)
        self.logger.debug(forwardBlogs)

        return userInfoDict, originalBlogs, forwardBlogs

    def saveWeiboUser(self, weiboUserDict):
        # insert weibo user

        sql = '''insert into weibo_user_info (
                      wuid,nickname,portrait_url,gender,birthday,
                      weibo_num,fans_num,follow_num,verified,vip,
                      relationship_state,address,tags)
                      values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')
                      ''' % (
            weiboUserDict['wbid'], weiboUserDict['nickname'], weiboUserDict['portraitUrl'],
            weiboUserDict['gender'],
            weiboUserDict['birthday'], weiboUserDict['weiboNum'], weiboUserDict['fansNum'],
            weiboUserDict['followNum'],
            weiboUserDict['verified'], weiboUserDict['vip'], weiboUserDict['relationshipStatus'],
            weiboUserDict['address'], weiboUserDict['tags'])
        '''
            'wbid': weiboUserInfo.wbid,
            'nickname': weiboUserInfo.wbid,
            'portraitUrl': weiboUserInfo.portraitUrl,
            'gender': weiboUserInfo.gender,
            'birthday': weiboUserInfo.birthday,
            'address': weiboUserInfo.address,
            'verified': weiboUserInfo.verified,
            'weiboNum': weiboUserInfo.weiboNum,
            'fansNum': weiboUserInfo.fansNum,
            'followNum': weiboUserInfo.followNum,
            'vip': weiboUserInfo.vip,
            'relationshipStatus': weiboUserInfo.relationshipStatus,
            'tags': ','.join(weiboUserInfo.tags)
        '''
        '''
        (
            weiboUserDict['wbid'], weiboUserDict['nickname'], weiboUserDict['portraitUrl'], weiboUserDict['gender'],
            weiboUserDict['birthday'], weiboUserDict['weiboNum'], weiboUserDict['fansNum'], weiboUserDict['followNum'],
            weiboUserDict['verified'], weiboUserDict['vip'], weiboUserDict['relationshipStatus'],
            weiboUserDict['address'], weiboUserDict['tags'])
        '''

        print(sql)
        conn = self.__getConnect()
        cursor = self.__cursorUtf8Wrapper(conn.cursor())
        cursor.execute(sql)
        conn.commit()
        conn.close()

    def saveOriginalWeibo(self, originalBlog):
        '''
                    'createTime': originalBlog.createTime,
                   'likeNum': originalBlog.likeNum,
                   'commentNum': originalBlog.commentNum,
                   'forwardNum': originalBlog.forwardNum,
                   'via': originalBlog.via,
                   'owner': originalBlog.owner,
                   'content': originalBlog.content,
                   'picNum': originalBlog.picNum
        '''
        sql = '''insert into weibo_original_blog (
                              create_time,like_num,comment_num,forward_num,
                              via,owner_id,content,pic_num,uni_code)
                              values('%s','%s','%s','%s','%s','%s','%s','%s','%s')
                              ''' % (
            originalBlog['createTime'], originalBlog['likeNum'], originalBlog['commentNum'],
            originalBlog['forwardNum'], originalBlog['via'], originalBlog['owner'],
            originalBlog['content'], originalBlog['picNum'], originalBlog['uniCode'])

        # print(sql)

        conn = self.__getConnect()
        cursor = self.__cursorUtf8Wrapper(conn.cursor())
        cursor.execute(sql)
        conn.commit()
        conn.close()

    def saveOriginalWeiboList(self, originalBlogs):
        for ob in originalBlogs:
            self.saveOriginalWeibo(ob)

    def saveForwardWeiboList(self, forwardBlogs):
        for fb in forwardBlogs:
            self.saveForwardWeibo(fb)

    def saveForwardWeibo(self, forwardBlog):
        '''
            self.createTime = None
            self.likeNum = 0
            self.commentNum = 0
            self.forwardNum = 0
            self.originalLikeNum = 0
            self.originalCommentNum = 0
            self.originalForwardNum = 0
            self.via = None
            self.originalOwner = None  # 原作者
            self.originalContent = None
            self.forwardOwner = None
            self.forwardContent = None

                tmp = {'createTime': forwardBlog.createTime,
                   'likeNum': forwardBlog.likeNum,
                   'commentNum': forwardBlog.commentNum,
                   'forwardNum': forwardBlog.forwardNum,
                   'originalLikeNum': forwardBlog.originalLikeNum,
                   'originalCommentNum': forwardBlog.originalCommentNum,
                   'originalForwardNum': forwardBlog.originalForwardNum,
                   'via': forwardBlog.via,
                   'originalOwner': forwardBlog.originalOwner,
                   # 'originalContent': forwardBlog.originalContent,
                   'forwardOwner': forwardBlog.forwardOwner,
                   # 'forwardContent': forwardBlog.forwardContent
                   }
        '''
        # 14 params
        sql = '''insert into weibo_forward_blog (
                              create_time,like_num,comment_num,forward_num,pic_num,
                              original_like_num,original_comment_num,original_forward_num,
                              original_pic_num,via,original_owner_id,original_content,
                              forward_owner_id,forward_content,uni_code)
                              values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')
                              ''' % (
            forwardBlog['createTime'], forwardBlog['likeNum'], forwardBlog['commentNum'],
            forwardBlog['forwardNum'], forwardBlog['picNum'], forwardBlog['originalLikeNum'],
            forwardBlog['originalCommentNum'], forwardBlog['originalForwardNum'], forwardBlog['originalPicNum'],
            forwardBlog['via'], forwardBlog['originalOwner'], forwardBlog['originalContent'],
            forwardBlog['forwardOwner'], forwardBlog['forwardContent'], forwardBlog['uniCode'])

        # print(sql)
        conn = self.__getConnect()
        cursor = self.__cursorUtf8Wrapper(conn.cursor())
        cursor.execute(sql)
        conn.commit()
        conn.close()


if __name__ == '__main__':
    saver = WeiBoMysqlSaver.getInstanceByConf('configs/db.conf')

    print(saver.test())
    # saver = WeiBoMysqlSaver()
    # print(saver.test())
