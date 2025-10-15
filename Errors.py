from collections import namedtuple

#Errors
class CommandError(Exception):
    pass
class DisconnectError(Exception):
    pass

Error = namedtuple('Error', ('message', 'code'))
