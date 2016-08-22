class WeiboUser(object):
    def __init__(self):
        self.wbid = None
        self.nickname = None
        self.gender = None
        self.birthday = None
        self.address = None
        self.portraitUrl = None
        self.weiboNum = -1
        self.fansNum = -1
        self.followNum = -1
        self.verified = -1
        self.vip = -1
        self.tags = []
        self.originalBlog = []
        self.forwardBlog = []
        self.relationshipStatus = None

    def toString(self):
        string = self.wbid + " " + self.nickname + " " + self.gender + " " + self.birthday \
                 + " " + self.address
        string += '\n'
        string += " ".join(self.tags)
        string += '\n'
        # string += " ".join(self.originalBlog)
        # string += '\n'
        # string += " ".join(self.forwardBlog)

    def print(self):
        print(', '.join(['%s:%s' % item for item in self.__dict__.items()]))
