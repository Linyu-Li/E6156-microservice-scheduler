from flask import Flask, Response, request
from flask_cors import CORS
import json
from typing import *
import requests

app = Flask(__name__)
CORS(app)

# TODO change apis below to AWS ones in deployment
USR_ADDR_PROPS = {
    'microservice': 'User/address microservice',
    'api': 'http://localhost:5001/users',
    'fields': ('nameLast', 'nameFirst', 'email', 'addressID', 'password', 'gender')
}
USR_PREF_PROPS = {
    'microservice': 'User profile microservice',
    'api': 'http://localhost:5002/profile',
    'fields': ('movie', 'hobby', 'book', 'music', 'sport', 'major', 'orientation')
}
SCHEDULE_PROPS = {
    'microservice': 'Scheduler microservice',
    'api': 'http://localhost:5003/availability/users',
    'fields': ('Year', 'Month', 'Day', 'StartTime', 'EndTime')
}
PROPS = (USR_ADDR_PROPS, USR_PREF_PROPS, SCHEDULE_PROPS)


def project_req_data(req_data: dict, props: tuple) -> dict:
    res = dict()
    for prop in props:
        if prop not in req_data:
            return None
        res[prop] = req_data[prop]
    return res


def sync_request_microservices(req_data: dict,
                                headers: Dict) -> (int, str):
    futures = []

    # register users
    register_data = project_req_data(req_data, USR_ADDR_PROPS['fields'])
    if register_data is None:
        return 400, f"Missing data field(s) for {USR_ADDR_PROPS['microservice']}"
    futures.append(
        requests.post(USR_ADDR_PROPS['api'],
                      data=json.dumps(req_data),
                      headers=headers)
    )


    # get the uid
    uid = ''

    # create preference and timeslot
    prop = USR_PREF_PROPS
    data = project_req_data(req_data, prop['fields'])
    if data is None:
        return 400, f"Missing data field(s) for {prop['microservice']}"
    futures.append(
        requests.post(prop['api'] + f"/{uid}",
                  data=json.dumps(data),
                  headers=headers))


    prop = SCHEDULE_PROPS
    for time_slot in req_data['timeSlots']:
        tid = time_slot['Id']
        t_data = project_req_data(time_slot, prop['fields'])
        if t_data is None:
            return 400, f"Missing field(s) in one of the request data for {prop['microservice']}"
        futures.append(
            requests.post(prop['api'] + f"/{uid}/{tid}",
                      data=json.dumps(data),
                      headers=headers))


    for i, future in enumerate(futures):
        microservice = PROPS[min(i, 2)]['microservice']
        res = future.result()
        if res is None:
            return 408, f"{microservice} did not response."
        elif not res.ok:
            return res.status_code, \
                   f"Response from the {microservice} is not OK."
    return 200, "User info created successfully!"


@app.route('/api/create', methods=['POST'])
def update_info():
    if request.method != 'POST':
        status_code = 405
        return Response(f"{status_code} - wrong method!", status=status_code, mimetype="application/json")
    req_data = request.get_json()
    status_code, message = sync_request_microservices(req_data, request.headers)
    return Response(f"{status_code} - {message}", status=status_code, mimetype="application/json")
    """
        Request JSON format:
        {
            "nameLast": string,
            "nameFirst": string,
            "email": string,
            "addressID": string/int,
            "password": string,
            "gender": string,
            "movie": string,
            "hobby": string,
            "book": string,
            "music": string,
            "sport": string,
            "major": string,
            "orientation": string,
            "timeSlots": [
                {
                    "Id": string/int,
                    "Year": string,
                    "Month": string,
                    "Day": string,
                    "StartTime": string,
                    "EndTime": string
                },
                {
                    "Id": string/int,
                    "Year": string,
                    "Month": string,
                    "Day": string,
                    "StartTime": string,
                    "EndTime": string
                },
                ...
            ]
        }
    """


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5004)