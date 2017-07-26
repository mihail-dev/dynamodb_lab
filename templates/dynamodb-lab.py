from troposphere import Template, Join, GetAtt
from troposphere.dynamodb import (KeySchema, AttributeDefinition,
                                  ProvisionedThroughput, StreamSpecification)
from troposphere.dynamodb import Table
from troposphere.sqs import Queue
from troposphere.awslambda import Function, Code, EventSourceMapping
from troposphere.iam import Role, Policy

class Dynamo_db(object):
    def __init__(self, sceptre_user_data):
        self.template = Template()
        self.sceptre_user_data = sceptre_user_data
        self.add_dynamo_db()
        self.add_sqs()
        self.add_lambda_db_entry_to_sqs()

    def add_dynamo_db(self):
        self.dynamo_db = self.template.add_resource(Table(
            "dynamoDBTable",
            AttributeDefinitions=[
                AttributeDefinition(
                    AttributeName=self.sceptre_user_data["HashKeyElementName"],
                    AttributeType=self.sceptre_user_data["HashKeyElementType"]
                )
            ],
            KeySchema=[
                KeySchema(
                    AttributeName=self.sceptre_user_data["HashKeyElementName"],
                    KeyType="HASH"
                )
            ],
            ProvisionedThroughput=ProvisionedThroughput(
                ReadCapacityUnits=self.sceptre_user_data["ReadCapacityUnits"],
                WriteCapacityUnits=self.sceptre_user_data["WriteCapacityUnits"]
            ),
            StreamSpecification=StreamSpecification(
                StreamViewType="NEW_AND_OLD_IMAGES"
            )
        ))

    def add_sqs(self):
    	self.sqs = self.template.add_resource(Queue(
    		"queue",
    		QueueName=self.sceptre_user_data["queue"]
		))

    def add_lambda_db_entry_to_sqs(self):
        self.DBEntryToSQSRole = self.template.add_resource(Role(
            "DBEntryToSQSRole",
            RoleName="DBEntryToSQSRole",
            Policies=[Policy(
                PolicyName="SQSRole",
                PolicyDocument={
                    "Version": "2012-10-17",
                    "Statement": [{
                        "Action": [
                            "sqs:*",
                            "dynamodb:*",
                            "logs:*"
                        ],
                        "Resource": "*",
                        "Effect": "Allow"
                    }]
                })],
            AssumeRolePolicyDocument={
                "Version": "2012-10-17",
                "Statement": [{
                    "Action": ["sts:AssumeRole"],
                    "Effect": "Allow",
                    "Principal": {
                        "Service": ["lambda.amazonaws.com"]
                    }
                }]
            },
        ))

        self.DBEntryToSQSFunction = self.template.add_resource(Function(
            "DBEntryToSQSFunction",
            FunctionName="DBEntryToSQSFunction",
            Code=Code(
                ZipFile=Join("\n", [
                    "import cfnresponse, json",
                    "// TODO implement",
                ])
            ),
            Handler="index.handler",
            Role=GetAtt("DBEntryToSQSRole", "Arn"),
            Runtime="python3.6",
            MemorySize=self.sceptre_user_data["lambda_db_entry_to_sqs"]["MemorySize"],
            Timeout=self.sceptre_user_data["lambda_db_entry_to_sqs"]["Timeout"]
        ))

        self.LambdaDDBTrigger = self.template.add_resource(EventSourceMapping(
            "LambdaDDBTrigger",
            DependsOn='DBEntryToSQSFunction',
            EventSourceArn=GetAtt("dynamoDBTable", "StreamArn"),
            FunctionName="DBEntryToSQSFunction",
            StartingPosition="TRIM_HORIZON"
        ))

def sceptre_handler(sceptre_user_data):
    dynamo_db = Dynamo_db(sceptre_user_data)
    return dynamo_db.template.to_json()