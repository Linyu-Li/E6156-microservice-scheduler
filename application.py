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
import random


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

application = Flask(__name__)
CORS(application)

client_id = "1093327178993-kbj68ghvsopafunmdk8rt1r6upt0oqdo.apps.googleusercontent.com"
client_secret = "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"
application.secret_key = "supersekrit"

# os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
# os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
# blueprint = make_google_blueprint(
#     client_id=client_id,
#     client_secret=client_secret,
#     reprompt_consent=True,
#     scope=["profile", "email"]
# )
# application.register_blueprint(blueprint, url_prefix="/login")
# google_blueprint = application.blueprints.get("google")
#
# @application.before_request
# def before_request():
#     print("checking before request")
#     result_pass = security.check_path(request, google, google_blueprint)
#     if not result_pass:
#         return redirect(url_for('google.login'))


trigger_SNS = {"path": "/timeSlot", "method": "GET"}


# @application.after_request
# def after_request(response):
#     print("checking after request")
#     if request.path == trigger_SNS["path"] and request.method==trigger_SNS["method"]:
#         sns = notification.NotificationMiddlewareHandler.get_sns_client()
#         print("Got SNS Client!")
#         tps = notification.NotificationMiddlewareHandler.get_sns_topics()
#         print("SNS Topics = \n", json.dumps(tps, indent=2))
#
#         message = {"test": "event created"}
#         notification.NotificationMiddlewareHandler.send_sns_message(
#         #     #"arn:aws:sns:us-east-1:971820320916:6156project",
#
#         "arn:aws:sns:us-east-1:697047102781:new-user-topic",
#
#         message
#         )
#     return response


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


# modified the POST method. If a post request to add a new timeSlot is received, first need to check if it
# exits in the database.
@application.route('/api/timeSlot', methods=['GET', 'POST'])
def all_time_slot():
    req = rest_utils.RESTContext(request)
    temp = req.data
    if req.method == "GET":
        res = TimeSlotResource.get_by_template({})
        rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
    else:
        res = TimeSlotResource.get_by_template(req.data)
        if not res:
            TimeSlotResource.create(req.data)
        rsp = Response("CREATED", status=201, content_type="text/plain")
    return rsp


# add a new path
# GET: display all available time slots for certain user
# POST: add a new timeSlot for the certain user
@application.route('/api/availability/users/<uid>', methods=['GET', 'POST'])
def availability_users(uid):
    req = rest_utils.RESTContext(request)
    if req.method == "GET":
        res = AvailabilityResource.get_by_template({"userId": uid})
        if res:
            temp = []
            for r in res:
                tid = r["timeId"]
                timeSlot = TimeSlotResource.get_by_template({"Id": tid})
                if timeSlot:
                    temp = temp + timeSlot
            res = temp
        rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
    elif req.method == "POST":
        startTime = int(req.data["StartTime"][:2])
        endTime = int(req.data["EndTime"][:2])
        interval = endTime - startTime
        list = []
        for i in range(interval):
            list.append({
                "Year": req.data["Year"],
                "Month": req.data["Month"],
                "Day": req.data["Day"],
                "StartTime": str(startTime) + ":00:00",
                "EndTime": str(startTime + 1) + ":00:00"
            })
            startTime += 1
        for i in range(len(list)):
            res = TimeSlotResource.get_by_template(list[i])

            if not res:
                TimeSlotResource.create(list[i])
            time = TimeSlotResource.get_by_template(list[i])
            timeId = time[0]["Id"]

            AvailabilityResource.create({
                "userId": uid,
                "timeId": timeId
            })
        rsp = Response("CREATED", status=201, content_type="text/plain")
    # else:
    #     AvailabilityResource.delete_by_template({"Id": aid})
    #     rsp = Response("DELETED", status=200, content_type="text/plain")
    return rsp


# add a new path
# PUT: If a user want to update a time slot, first check if the updated time slot is in the timeSlot table.
#      If not, add the new time slot into timeSlot table.
#      If exists, associate the time slot with the user.
# DELETE: delete (the userID, timeID) pair in the Availability table. Do not delete the time slot in the TimeSlot table
#         because other users might be associated with this time slot.
@application.route('/api/availability/users/<uid>/<tid>', methods=['PUT', 'DELETE'])
def availability_users_one(uid, tid):
    req = rest_utils.RESTContext(request)
    if req.method == "PUT":
        AvailabilityResource.delete_by_template({"userId": uid, "timeId": tid})
        startTime = int(req.data["StartTime"][:2])
        endTime = int(req.data["EndTime"][:2])
        interval = endTime - startTime
        list = []
        for i in range(interval):
            list.append({
                "Year": req.data["Year"],
                "Month": req.data["Month"],
                "Day": req.data["Day"],
                "StartTime": str(startTime) + ":00:00",
                "EndTime": str(startTime + 1) + ":00:00"
            })
            startTime += 1
        for i in range(len(list)):
            res = TimeSlotResource.get_by_template(list[i])

            if not res:
                TimeSlotResource.create(list[i])
            time = TimeSlotResource.get_by_template(list[i])
            timeId = time[0]["Id"]

            template = {
                "userId": uid,
                "timeId": timeId
            }
            output = AvailabilityResource.get_by_template(template)

            if not output:
                AvailabilityResource.create(template)
        rsp = Response("UPDATED", status=200, content_type="application/json")
    elif req.method == "DELETE":
        AvailabilityResource.delete_by_template({"userId": uid, "timeId": tid})
        rsp = Response("DELETED", status=200, content_type="text/plain")

    return rsp


# add a new path
# display all users for a certain time slot
@application.route('/api/timeSlot/<tid>/users', methods=['GET'])
def time_slot_users(tid):
    req = rest_utils.RESTContext(request)
    if req.method == "GET":
        res = AvailabilityResource.get_by_template({"timeId": tid})
        rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
    return rsp


# add a new path
# to display all available time slot time slots for a matched user
@application.route('/api/matchAvail', methods=['GET'])
def match_time_slots():
    req = rest_utils.RESTContext(request)
    uid = req.args["uid"]
    if req.method == "GET":
        res = AvailabilityResource.get_by_template({"userId": uid}, req.limit, req.offset)
        if res:
            temp = []
            for r in res:
                tid = r["timeId"]
                timeSlot = TimeSlotResource.get_by_template({"Id": tid})
                if timeSlot:
                    temp = temp + timeSlot
            res = temp
        rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
    return rsp


@application.route('/api/matchUser/<uid>', methods=['GET'])
def match(uid):
    req = rest_utils.RESTContext(request)
    if req.method == "GET":
        all_matches = []
        all_avail_time = json.loads(availability_users(uid).data.decode("utf-8"))
        for t in all_avail_time:
            tid = t["Id"]
            users = AvailabilityResource.get_by_template({"timeId": tid})
            for user in users:
                if user["userId"] == int(uid):
                    continue
                all_matches.append(user["userId"])
        if all_matches:
            res = random.choice(all_matches)
        else:
            res = -1

        rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
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


@application.route('/avail/<aid>', methods=['PUT'])
def edit_avail_time_slot(aid):
    if request.method != 'PUT':
        return Response("Wrong method", status=405, content_type="text/plain")
    res = AvailabilityResource.get_by_template({"Id": aid})
    if res:
        tid = res[0]['Id']
        TimeSlotResource.update(request.get_json(), tid)
        return Response("UPDATED", status=200, content_type="text/plain")
    return Response(f"Availability {aid} not found!", status=404, content_type="text/plain")


if __name__ == '__main__':
    application.run(host="0.0.0.0", port=5003)
    # application.run()
