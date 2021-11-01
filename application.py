import os

from flask import Flask, Response, request, redirect, url_for
from flask_cors import CORS
import json
import utils.rest_utils as rest_utils
import logging
from flask_dance.contrib.google import make_google_blueprint, google

from application_services.AvailabilityResource.availability_service import AvailabilityResource
from application_services.TimeSlotResource.time_slot_service import TimeSlotResource
from middleware import security, notification

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

application = Flask(__name__)
CORS(application)

client_id = "1093327178993-kbj68ghvsopafunmdk8rt1r6upt0oqdo.apps.googleusercontent.com"
client_secret = "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"
application.secret_key = "supersekrit"

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
blueprint = make_google_blueprint(
    client_id=client_id,
    client_secret=client_secret,
    reprompt_consent=True,
    scope=["profile", "email"]
)
application.register_blueprint(blueprint, url_prefix="/login")
google_blueprint = application.blueprints.get("google")


@application.before_request
def before_request():
    print("checking before request")
    result_pass = security.check_path(request, google, google_blueprint)
    if not result_pass:
        return redirect(url_for('google.login'))


trigger_SNS = {"path": "/timeSlot", "method": "GET"}


@application.after_request
def after_request(response):
    print("checking after request")
    if request.path == trigger_SNS["path"] and request.method==trigger_SNS["method"]:
        sns = notification.NotificationMiddlewareHandler.get_sns_client()
        print("Got SNS Client!")
        tps = notification.NotificationMiddlewareHandler.get_sns_topics()
        print("SNS Topics = \n", json.dumps(tps, indent=2))

        message = {"test": "event created"}
        notification.NotificationMiddlewareHandler.send_sns_message(
        #     #"arn:aws:sns:us-east-1:971820320916:6156project",

        "arn:aws:sns:us-east-1:697047102781:new-user-topic",

        message
        )
    return response


@application.route('/')
def hello_world():
    return '<u>Hello World!</u>'


@application.route('/test-secure')
def test_path_secured():
    return "This is a secured path. You have successfully logged in."


@application.route('/test')
def test_path_not_secured():
    return "This path is not secured. You are not required to log in."


@application.route('/availability', methods=['GET', 'POST'])
def all_availability():
    req = rest_utils.RESTContext(request)
    if req.method == "GET":
        res = AvailabilityResource.get_by_template({})
        rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
    else:
        AvailabilityResource.create(req.data)
        rsp = Response("CREATED", status=201, content_type="text/plain")
    return rsp


@application.route('/timeSlot', methods=['GET', 'POST'])
def all_time_slot():
    req = rest_utils.RESTContext(request)
    if req.method == "GET":
        res = TimeSlotResource.get_by_template({})
        rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
    else:
        TimeSlotResource.create(req.data)
        rsp = Response("CREATED", status=201, content_type="text/plain")
    return rsp


@application.route('/availability/<aid>', methods=['GET', 'PUT', 'DELETE'])
def availability_id(aid):
    req = rest_utils.RESTContext(request)
    if req.method == "GET":
        res = AvailabilityResource.get_by_template({"Id": aid})
        rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
    elif req.method == "PUT":
        AvailabilityResource.update(req.data, aid)
        rsp = Response("UPDATED", status=200, content_type="text/plain")
    else:
        AvailabilityResource.delete_by_template({"Id": aid})
        rsp = Response("DELETED", status=200, content_type="text/plain")
    return rsp


@application.route('/timeSlot/<tid>', methods=['GET', 'PUT', 'DELETE'])
def time_slot_id(tid):
    req = rest_utils.RESTContext(request)
    if req.method == "GET":
        res = TimeSlotResource.get_by_template({"Id": tid})
        rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
    elif req.method == "PUT":
        TimeSlotResource.update(req.data, tid)
        rsp = Response("UPDATED", status=200, content_type="text/plain")
    else:
        TimeSlotResource.delete_by_template({"Id": tid})
        rsp = Response("DELETED", status=200, content_type="text/plain")
    return rsp


if __name__ == '__main__':
    application.run()
