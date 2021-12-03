import json

secured_path = ["/test-secure"]

def check_path(request, OAuth, blueprint):
    result_pass = False
    if request.path not in secured_path:
        result_pass = True
    else:
        if OAuth.authorized:
            info = 'oauth2/v2/userinfo'
            data = OAuth.get(info).json()
            print(json.dumps(data, indent = 2))
            token = blueprint.session.token
            print(json.dumps(token, indent=2))

            result_pass = True
    return result_pass
