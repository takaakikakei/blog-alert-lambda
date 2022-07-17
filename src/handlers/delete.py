import logging

import src.use_cases.delete

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context) -> None:
    """
    delete のエントリポイント
    """

    try:
        return src.use_cases.delete.exec()
    except Exception as e:
        logger.error(e)
        raise e
