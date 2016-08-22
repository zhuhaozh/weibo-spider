def printObj(obj):
    print(', '.join(['%s:%s' % item for item in obj.__dict__.items()]))


def objToString(obj):
    return ', '.join(['%s:%s' % item for item in obj.__dict__.items()])
