from troposphere import Template
from troposphere.dynamodb import (KeySchema, AttributeDefinition,
                                  ProvisionedThroughput)
from troposphere.dynamodb import Table

class Dynamo_db(object):
    def __init__(self, sceptre_user_data):
        self.template = Template()
        self.sceptre_user_data = sceptre_user_data
        self.add_dynamo_db()

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
            )
        ))

def sceptre_handler(sceptre_user_data):
    dynamo_db = Dynamo_db(sceptre_user_data)
    return dynamo_db.template.to_json()