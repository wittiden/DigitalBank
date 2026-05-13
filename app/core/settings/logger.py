import sys

from loguru import logger


def add_logger() -> None:
    logger.remove()

    logger.level(name='TRANSACTION', no=22, color='<yellow>')

    logger.add(sys.stdout, level='DEBUG')

    logger.add('logs/user_logs.log', filter=lambda record: record['level'].no != 22, level='INFO', rotation='10 MB', encoding='UTF-8', enqueue=True)
    logger.add('logs/trns.log', filter=lambda record: record['level'].no == 22, level='TRANSACTION', rotation='100 MB', encoding='UTF-8', enqueue=True)
