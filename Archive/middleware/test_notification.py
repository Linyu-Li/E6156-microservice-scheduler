from notification import NotificationMiddlewareHandler
import json

def t_sns_1():
    sns = NotificationMiddlewareHandler.get_sns_client()
    print("Got SNS Client!")
    tps = NotificationMiddlewareHandler.get_sns_topics()
    print("SNS Topics = \n", json.dumps(tps, indent=2))

    message = {"cool": "beans"}
    NotificationMiddlewareHandler.send_sns_message(
        "arn:aws:sns:us-east-1:971820320916:6156project",
        message
    )
t_sns_1()