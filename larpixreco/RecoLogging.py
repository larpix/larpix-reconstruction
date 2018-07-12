import logging
import sys

log_level_lookup = {
    'debug' : logging.DEBUG,
    'info' : logging.INFO,
    'warning' : logging.WARNING,
    'error' : logging.ERROR,
    'critical' : logging.CRITICAL
    }
log_format = '%(asctime)s %(name)s %(levelname)s: %(message)s'

def initializeLogger(level='debug', filename=None, stdout=True, stderr=False):
    logger = getLogger()
    handlers = []
    if not filename is None:
        filehandler = logging.FileHandler(filename)
        handlers += [filehandler]
    if stdout:
        handlers += [logging.StreamHandler(sys.stdout)]
    if stderr:
        handlers += [logging.StreamHandler(sys.stderr)]
    formatter = logging.Formatter(log_format)
    for handler in handlers:
        handler.setLevel(log_level_lookup[level])
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(log_level_lookup[level])
    logger.info('logger initialized')
    return logger

def getLogger(name=None):
    if name is None or name == '':
        name = 'larpixreco'
    return logging.getLogger(name)
