import logging
import os
from typing import Dict

import boto3

from src.services.cloudwatch import CloudWatchService
from src.services.lambda_client import LambdaService

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class AddUseCase:
    def __init__(
        self, cloudwatch_service: CloudWatchService, lambda_service: LambdaService
    ):
        self.cloudwatch_service = cloudwatch_service
        self.lambda_service = lambda_service

    def add(self, alarm_lambda_name: str, deployed_lambda_name: str, metric_name: str):
        """
        CloudWatch で アラーム未設定の Lambda 関数へのアラーム追加
        """
        logger.info(f"Start adding {metric_name} alarm")
        diff_list = set(alarm_lambda_name) ^ set(deployed_lambda_name)
        logger.info(f"{metric_name} diff_list:\n{list(diff_list)}")
        logger.info(f"{metric_name} len(diff_list):\n{len(list(diff_list))}")

        if len(diff_list) == 0:
            logger.info(f"No Add {metric_name} alarm")
            return []

        try:
            for add_lambda_name in diff_list:
                self.cloudwatch_service.put_metric_alarm(add_lambda_name, metric_name)
        except Exception as e:
            logger.error(f"Failed Add at:\n{add_lambda_name}")
            raise e

        logger.info(f"Add {metric_name} alarm:\n{list(diff_list)}")
        return {"add_lambda_names": list(diff_list)}

    def exec(self) -> Dict:
        """
        CloudWatch で Errors アラームを設定済みの Lambda の情報を取得
        """
        try:
            alarm_errors = self.cloudwatch_service.describe_alarm("AlertLambda-Errors")
        except Exception as e:
            raise e
        else:
            logger.info(f"alarm_errors:\n {alarm_errors}")

        """
        CloudWatch で Throttles アラームを設定済みの Lambda の情報を取得
        """
        try:
            alarm_throttles = self.cloudwatch_service.describe_alarm(
                "AlertLambda-Throttles"
            )
        except Exception as e:
            raise e
        else:
            logger.info(f"alarm_throttles:\n {alarm_throttles}")

        """
        デプロイ済の Lambda 関数の名前リストを取得
        """
        try:
            deployed_lambda = self.lambda_service.describe_deployed_lambda()
        except Exception as e:
            raise e
        else:
            logger.info(f"deployed_lambda:\n{deployed_lambda}")

        """
        CloudWatch で Errors アラーム未設定の Lambda 関数へのアラーム追加
        """
        add_alarm_errors_lambda_names = self.add(
            alarm_lambda_name=alarm_errors["lambda_names"],
            deployed_lambda_name=deployed_lambda["lambda_names"],
            metric_name="Errors",
        )

        """
        CloudWatch で Throttles アラーム未設定の Lambda 関数へのアラーム追加
        """
        add_alarm_throttles_lambda_names = self.add(
            alarm_lambda_name=alarm_throttles["lambda_names"],
            deployed_lambda_name=deployed_lambda["lambda_names"],
            metric_name="Throttles",
        )

        return {
            "add_alarm_errors_lambda_names": add_alarm_errors_lambda_names,
            "add_alarm_throttles_lambda_names": add_alarm_throttles_lambda_names,
        }


def _init_use_case() -> AddUseCase:
    # 環境変数
    sns_topic_arn = os.environ["SNS_TOPIC_ARN"]
    region_name = os.environ["AWS_REGION"]

    # refs: https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cloudwatch/
    cloudwatch_client = boto3.client("cloudwatch", region_name=region_name)
    cloudwatch_service = CloudWatchService(cloudwatch_client, sns_topic_arn)

    # refs: https://youtype.github.io/boto3_stubs_docs/mypy_boto3_lambda/
    lambda_client = boto3.client("lambda", region_name=region_name)
    lambda_service = LambdaService(lambda_client)

    return AddUseCase(
        cloudwatch_service=cloudwatch_service,
        lambda_service=lambda_service,
    )


def exec() -> Dict:
    use_case = _init_use_case()
    return use_case.exec()
