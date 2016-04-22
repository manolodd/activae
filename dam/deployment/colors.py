ESC   = chr(27) + '['
RESET = '%s0m' % (ESC)

def green (s):
    return ESC + '0;32m' + s + RESET

def red (s):
    return ESC + '0;31m' + s + RESET

def yellow (s):
    return ESC + '1;33m' + s + RESET
    
def blue (s):
    return ESC + '0;34m' + s + RESET
