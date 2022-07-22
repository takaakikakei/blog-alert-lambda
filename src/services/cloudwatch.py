import logging
import os
from typing import Dict, List

from mypy_boto3_cloudwatch.client import CloudWatchClient

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class CloudWatchService:
    def __init__(self, cloudwatch: CloudWatchClient, sns_topic_arn: str):
        self._cloudwatch = cloudwatch
        self.sns_topic_arn = sns_topic_arn

    def describe_alarm(self, alarm_name_prefix="AlertLambda") -> Dict:
        """
        下記条件で、CloudWatch アラーム設定済みの Lambda 関数の名前リストを取得
        - AlarmTypes が MetricAlarms
        - ActionPrefix に通知用の SNS Topic を指定
        - Namespace が AWS/Lambda
        - 引数の指定がなければ、AlarmNamePrefix が AlertLambda
        """
        # refs: refs: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudwatch.html#CloudWatch.Paginator.DescribeAlarms
        paginator = self._cloudwatch.get_paginator("describe_alarms")
        lambda_names = []
        alarm_names = []
        for page in paginator.paginate(
            AlarmTypes=["MetricAlarm"],
            ActionPrefix=self.sns_topic_arn,
            AlarmNamePrefix=alarm_name_prefix,
        ):
            for metric_alarm in page["MetricAlarms"]:
                if metric_alarm["Namespace"] != "AWS/Lambda":
                    break
                for dimension in metric_alarm["Dimensions"]:
                    if dimension["Name"] == "FunctionName":
                        lambda_names.append(dimension["Value"])
                        alarm_names.append(metric_alarm["AlarmName"])
                        break
        return {"lambda_names": lambda_names, "alarm_names": alarm_names}

    def put_metric_alarm(self, add_lambda_name: str, metric_name: str) -> None:
        # refs: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudwatch.html#CloudWatch.Client.put_metric_alarm
        self._cloudwatch.put_metric_alarm(
            AlarmName=f"AlertLambda-{metric_name}-{add_lambda_name}",
            AlarmDescription="Lambdaのアラーム",
            ActionsEnabled=True,
            OKActions=[],
            AlarmActions=[self.sns_topic_arn],
            InsufficientDataActions=[],
            MetricName=metric_name,
            Namespace="AWS/Lambda",
            Statistic="Sum",
            Dimensions=[
                {
                    "Name": "FunctionName",
                    "Value": add_lambda_name,
                },
                {
                    "Name": "Resource",
                    "Value": add_lambda_name,
                },
            ],
            Period=60,
            EvaluationPeriods=5,
            DatapointsToAlarm=1,
            Threshold=1.0,
            ComparisonOperator="GreaterThanOrEqualToThreshold",
            TreatMissingData="missing",
            Tags=[
                {"Key": "Service", "Value": "AlertLambda"},
            ],
        )
        return

    def delete_alarms(self, alarm_names: List) -> None:
        """
        1回の操作で最大100個のアラームを削除可能なため、リストを100個ずつに分割して削除
        """
        # refs: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudwatch.html#CloudWatch.Client.delete_alarms
        blocks = []
        n = 100
        for i in range(0, len(alarm_names), n):
            blocks.append(alarm_names[i : i + n])  # noqa: E203

        logger.info(f"blocks:\n{blocks}")
        for block in blocks:
            self._cloudwatch.delete_alarms(AlarmNames=block)
        return
