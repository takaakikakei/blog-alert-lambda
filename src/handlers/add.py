import logging
from typing import Dict

import src.use_cases.add

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context) -> Dict:
    """
    add のエンドポイント
    """

    try:
        return src.use_cases.add.exec()
    except Exception as e:
        logger.error(e)
        raise e
