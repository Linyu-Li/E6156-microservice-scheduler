from flask import Flask, Response, request
from flask_cors import CORS
import json
import utils.rest_utils as rest_utils
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

from application_services.AvailabilityResource.availability_service import AvailabilityResource
from application_services.TimeSlotResource.time_slot_service import TimeSlotResource


application = Flask(__name__)
CORS(application)

@application.route('/')
def hello_world():
    return '<u>Hello World!</u>'


@application.route('/availability', methods=['GET', 'POST'])
def all_availability():
    req = rest_utils.RESTContext(request)
    if req.method == "GET":
        res = AvailabilityResource.get_by_template({})
        if len(res):
            status_code = 200
        else:
            res = 'Resource not found!'
            status_code = 404
        rsp = Response(json.dumps(res, default=str), status=status_code, content_type="application/json")
    else:
        if req.data:
            try:
                AvailabilityResource.create(req.data)
                status_code = 201
                res = "Created"
            except Exception as e:
                res = 'Database error: {}'.format(str(e))
                status_code = 422
        else:
            res = 'New profile cannot be empty!'
            status_code = 400
        rsp = Response(f"{status_code} - {res}", status=status_code, content_type="text/plain")
    return rsp


@application.route('/timeSlot', methods=['GET', 'POST'])
def all_time_slot():
    req = rest_utils.RESTContext(request)
    if req.method == "GET":
        res = TimeSlotResource.get_by_template({})
        if len(res):
            status_code = 200
        else:
            res = 'Resource not found!'
            status_code = 404
        rsp = Response(json.dumps(res, default=str), status=status_code, content_type="application/json")
    else:
        if req.data:
            try:
                TimeSlotResource.create(req.data)
                status_code = 201
                res = "Created"
            except Exception as e:
                res = 'Database error: {}'.format(str(e))
                status_code = 422
        else:
            res = 'New profile cannot be empty!'
            status_code = 400
        rsp = Response(f"{status_code} - {res}", status=status_code, content_type="text/plain")
    return rsp


@application.route('/availability/<aid>', methods=['GET', 'PUT', 'DELETE'])
def availability_id(aid):
    req = rest_utils.RESTContext(request)
    if req.method == "GET":
        res = AvailabilityResource.get_by_template({"Id": aid})
        if len(res):
            status_code = 200
        else:
            res = 'Resource not found!'
            status_code = 404
        rsp = Response(json.dumps(res, default=str), status=status_code, content_type="application/json")
    elif req.method == "PUT":
        if req.data:
            AvailabilityResource.update(req.data, aid)
            status_code = 200
            res = "Updated"
        else:
            res = 'New availability cannot be empty!'
            status_code = 400
        rsp = Response(f"{status_code} - {res}", status=status_code, content_type="text/plain")
    else:
        AvailabilityResource.delete_by_template({"Id": aid})
        status_code = 204
        res = "Deleted"
        rsp = Response(f"{status_code} - {res}", status=status_code, content_type="text/plain")
    return rsp


@application.route('/timeSlot/<tid>', methods=['GET', 'PUT', 'DELETE'])
def time_slot_id(tid):
    req = rest_utils.RESTContext(request)
    if req.method == "GET":
        res = TimeSlotResource.get_by_template({"Id": tid})
        if len(res):
            status_code = 200
        else:
            res = 'Resource not found!'
            status_code = 404
        rsp = Response(json.dumps(res, default=str), status=status_code, content_type="application/json")
    elif req.method == "PUT":
        if req.data:
            TimeSlotResource.update(req.data, tid)
            status_code = 200
            res = "Updated"
        else:
            res = 'New timeslot cannot be empty!'
            status_code = 400
        rsp = Response(f"{status_code} - {res}", status=status_code, content_type="text/plain")
    else:
        TimeSlotResource.delete_by_template({"Id": tid})
        status_code = 204
        res = "Deleted"
        rsp = Response(f"{status_code} - {res}", status=status_code, content_type="text/plain")
    return rsp


if __name__ == '__main__':
    application.run()
