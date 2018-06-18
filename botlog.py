class bcolors:
    HEADER = '\033[95m'
    WHITE = '\033[37m'
    BLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class BotLog(object):
    def __init__(self):
        pass

    def log(self, message):
        print(bcolors.WHITE + message + bcolors.ENDC)

    def info(self, message):
        print(bcolors.BLUE + message + bcolors.ENDC)

    def success(self, message):
        print(bcolors.OKGREEN + message + bcolors.ENDC)

    def fail(self, message):
        print(bcolors.FAIL + message + bcolors.ENDC)

    def warning(self, message):
        print(bcolors.WARNING + message + bcolors.ENDC)
