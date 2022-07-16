import logging
import os

import boto3

from src.services.cloudwatch import CloudWatchService

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class DeleteUseCase:
    def __init__(self, cloudwatch_service: CloudWatchService):
        self.cloudwatch_service = cloudwatch_service

    def exec(self) -> None:
        """
        本ツールで作成したCloudWatchアラームをリスト
        """
        try:
            alarm_name_prefix = "AlertLambda"
            alarms = self.cloudwatch_service.describe_alarm(alarm_name_prefix)
        except Exception as e:
            raise e
        else:
            logger.info(f"alarms:\n {alarms}")

        """
        本ツールで作成したCloudWatchアラームを一括削除
        """
        alarm_names = alarms["alarm_names"]
        logger.info(f"len(alarm_names):\n{len(alarm_names)}")

        if len(alarm_names) == 0:
            logger.info("No Delete")
            return

        try:
            self.cloudwatch_service.delete_alarms(alarm_names)
        except Exception as e:
            raise e

        return


def _init_use_case() -> DeleteUseCase:
    # 環境変数
    sns_topic_arn = os.environ["SNS_TOPIC_ARN"]
    region_name = os.environ["AWS_REGION"]

    # refs: https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudwatch/
    cloudwatch_client = boto3.client("cloudwatch", region_name=region_name)
    cloudwatch_service = CloudWatchService(cloudwatch_client, sns_topic_arn)

    return DeleteUseCase(cloudwatch_service=cloudwatch_service)


def exec() -> None:
    use_case = _init_use_case()
    return use_case.exec()
