import logging
import colorlog

log_colors_config = {
    'DEBUG': 'cyan',
    'INFO': 'green',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'red,bold'
}


def get_logger(level=logging.INFO):
    logger = logging.getLogger()
    logger.setLevel(level)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    colored_fmt = colorlog.ColoredFormatter(
        fmt='%(log_color)s%(asctime)s [%(name)s:%(funcName)s] [%(levelname)s]: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors=log_colors_config
    )
    console_handler.setFormatter(colored_fmt)

    for handler in logger.handlers:
        logger.removeHandler(handler)
    logger.addHandler(console_handler)
    return logger


if __name__ == '__main__':
    logger = get_logger(logging.DEBUG)
    logger.debug('debug msg')
    logger.info('info msg')
    logger.warning('warning msg')
    logger.error('error msg')
    logger.critical('critical msg')
