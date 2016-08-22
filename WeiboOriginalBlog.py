class WeiboOriginalBlog(object):
    def __init__(self):
        self.createTime = None
        self.likeNum = -1
        self.commentNum = -1
        self.forwardNum = -1
        self.picNum = -1
        self.via = None
        self.owner = None  # 原作者
        self.content = None

    def print(self):
        print(', '.join(['%s:%s' % item for item in self.__dict__.items()]))
