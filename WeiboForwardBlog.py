class WeiboForwardBlog(object):
    def __init__(self):
        self.createTime = None
        self.likeNum = -1
        self.commentNum = -1
        self.forwardNum = -1
        self.picNum = -1
        self.originalLikeNum = -1
        self.originalCommentNum = -1
        self.originalForwardNum = -1
        self.originalPicNum = -1
        self.via = None
        self.originalOwner = None  # 原作者
        self.originalContent = None
        self.forwardOwner = None
        self.forwardContent = None
        self.uniCode = None

    @staticmethod
    def generateWeiboBlog():
        pass

    def print(self):
        print(', '.join(['%s:%s' % item for item in self.__dict__.items()]))
