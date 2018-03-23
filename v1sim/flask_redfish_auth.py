# Copyright Notice:
# Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Profile-Simulator/blob/master/LICENSE.md

"""
flask_redfish_auth

adapted from:
    flask_httpauth
    ==================
    This module provides Basic and Digest HTTP authentication for Flask routes.
    :copyright: (C) 2014 by Miguel Grinberg.
    :license:   MIT, see LICENSE for more details, 
        at https://github.com/miguelgrinberg/Flask-HTTPAuth/blob/master/LICENSE

    see documentation at:    http://flask.pocoo.org/snippets/8/
    code and docs at:       https://github.com/miguelgrinberg/flask-httpauth/

**** modified to implement EITHER Redfish Token Auth or Basic Auth
    this file is imported by: catfishURIs.py

  Usage:  In RedfishProfileSimulator: see this flow below in redfishURIs.py
        ... in redfishURIs.py
        from .flask_redfish_auth import RfHTTPBasicOrTokenAuth
        ...
        #create instance of the modified Basic or Redfish Token auth
        #   this is what is in this file
        auth=RfHTTPBasicOrTokenAuth
        
        #define basic auth decorator used by flask
        @auth.verify_basic_password
        def verifyRfPasswd(user,passwd):
        ...
        
        #define Redfish Token/Session auth decorator used by flask
        @auth.verify_token
        def verifyRfToken(auth_token):
        ..

        @app.route("/api", methods=['GET'])
        @auth.rfAuthRequired
        def api()
        ...
"""

from functools import wraps

from flask import request, make_response


# this is the Base HTTP Auth class that is used to derive the Redfish "Basic or Token Auth" class
class HTTPAuth(object):
    def __init__(self, scheme=None, realm=None):
        def default_get_password(userx):
            return None

        def default_basic_auth_error():
            return "Unauthorized Access"

        def default_token_auth_error():
            return "Unauthorized Access. Invalid authentication token"

        self.scheme = scheme
        self.realm = realm or "Authentication Required"
        self.get_password(default_get_password)
        self.basic_error_handler(default_basic_auth_error)
        self.token_error_handler(default_token_auth_error)

    def get_password(self, f):
        self.get_password_callback = f
        return f

    def token_error_handler(self, f):
        @wraps(f)
        def decorated(*args, **kwargs):
            res = f(*args, **kwargs)
            if type(res) == str:
                res = make_response(res)
                res.status_code = 401
            return res

        self.auth_token_error_callback = decorated
        return decorated

    def basic_error_handler(self, f):
        @wraps(f)
        def decorated(*args, **kwargs):
            res = f(*args, **kwargs)
            if type(res) == str:
                res = make_response(res)
                res.status_code = 401
            if 'WWW-Authenticate' not in res.headers.keys():
                res.headers['WWW-Authenticate'] = self.authenticate_header()
            return res

        self.auth_basic_error_callback = decorated
        return decorated

    # for redfish, we need to hook this to check if its token auth before trying basic auth
    def rfAuthRequired(self, f):
        @wraps(f)
        def decorated(*args, **kwargs):
            auth = request.authorization
            print("in rfAuthRequired")
            print("headers: {}".format(request.headers))
            # We need to ignore authentication headers for OPTIONS to avoid
            # unwanted interactions with CORS.
            # Chrome and Firefox issue a preflight OPTIONS request to check
            # Access-Control-* headers, and will fail if it returns 401.
            if request.method != 'OPTIONS':
                # auth is None if the Basic auth header didn't come in the request
                found_token = False
                if (auth is None):
                    ###print("auth is None")
                    # check if we have a redfish auth token
                    hdr_token_key = "X-Auth-Token"
                    auth_token = request.headers.get(hdr_token_key)
                    ###print("token={}".format(auth_token))
                    if (auth_token is not None):
                        found_token = True
                        # yeah!  we have an auth token in the headers
                        authOk = self.verify_token_callback(auth_token)
                        ###print("verify_token={}".format(authOk))
                        if (authOk is not True):
                            # we had an auth token, but it didn't validate
                            return (self.auth_token_error_callback())

                # now continue with normal Basic Auth validation
                if (found_token is not True):
                    ###print("try basic")
                    if auth:
                        password = self.get_password_callback(auth.username)
                    else:
                        password = None
                    ###print("basic auth: auth={}, pwd={}".format(auth,password))
                    if (not self.authenticate(auth, password)):
                        return (self.auth_basic_error_callback())
            ###print("now execute the function")
            return (f(*args, **kwargs))

        return (decorated)

    def username(self):
        if not request.authorization:
            return ""
        return request.authorization.username


# this class is derived from HTTPAuth above
class RfHTTPBasicOrTokenAuth(HTTPAuth):
    def __init__(self, scheme=None, realm=None):
        super(RfHTTPBasicOrTokenAuth, self).__init__(scheme, realm)
        self.hash_password(None)
        self.verify_basic_password(None)
        self.verify_token(None)

    def hash_password(self, f):
        self.hash_password_callback = f
        return f

    def verify_basic_password(self, f):
        self.verify_password_callback = f
        return f

    def verify_token(self, f):
        self.verify_token_callback = f
        return f

    def authenticate_header(self):
        return '{0} realm="{1}"'.format(self.scheme or 'Basic', self.realm)

    def authenticate(self, auth, stored_password):
        if auth:
            username = auth.username
            client_password = auth.password
        else:
            username = ""
            client_password = ""
        if self.verify_password_callback:
            return self.verify_password_callback(username, client_password)
        if not auth:
            return False
        if self.hash_password_callback:
            try:
                client_password = self.hash_password_callback(client_password)
            except TypeError:
                client_password = self.hash_password_callback(username,
                                                              client_password)
        return client_password == stored_password


'''
class HTTPDigestAuth(HTTPAuth):
    def __init__(self, scheme=None, realm=None, use_ha1_pw=False):
        super(HTTPDigestAuth, self).__init__(scheme, realm)
        self.use_ha1_pw = use_ha1_pw
        self.random = SystemRandom()
        try:
            self.random.random()
        except NotImplementedError:
            self.random = Random()

        def _generate_random():
            return md5(str(self.random.random()).encode('utf-8')).hexdigest()

        def default_generate_nonce():
            session["auth_nonce"] = _generate_random()
            return session["auth_nonce"]

        def default_verify_nonce(nonce):
            return nonce == session.get("auth_nonce")

        def default_generate_opaque():
            session["auth_opaque"] = _generate_random()
            return session["auth_opaque"]

        def default_verify_opaque(opaque):
            return opaque == session.get("auth_opaque")

        self.generate_nonce(default_generate_nonce)
        self.generate_opaque(default_generate_opaque)
        self.verify_nonce(default_verify_nonce)
        self.verify_opaque(default_verify_opaque)

    def generate_nonce(self, f):
        self.generate_nonce_callback = f
        return f

    def verify_nonce(self, f):
        self.verify_nonce_callback = f
        return f

    def generate_opaque(self, f):
        self.generate_opaque_callback = f
        return f

    def verify_opaque(self, f):
        self.verify_opaque_callback = f
        return f

    def get_nonce(self):
        return self.generate_nonce_callback()

    def get_opaque(self):
        return self.generate_opaque_callback()

    def generate_ha1(self, username, password):
        a1 = username + ":" + self.realm + ":" + password
        a1 = a1.encode('utf-8')
        return md5(a1).hexdigest()

    def authenticate_header(self):
        session["auth_nonce"] = self.get_nonce()
        session["auth_opaque"] = self.get_opaque()
        return '{0} realm="{1}",nonce="{49}",opaque="{3}"'.format(
            self.scheme or 'Digest', self.realm, session["auth_nonce"],
            session["auth_opaque"])

    def authenticate(self, auth, stored_password_or_ha1):
        if not auth or not auth.username or not auth.realm or not auth.uri \
                or not auth.nonce or not auth.response \
                or not stored_password_or_ha1:
            return False
        if not(self.verify_nonce_callback(auth.nonce)) or \
                not(self.verify_opaque_callback(auth.opaque)):
            return False
        if self.use_ha1_pw:
            ha1 = stored_password_or_ha1
        else:
            a1 = auth.username + ":" + auth.realm + ":" + \
                stored_password_or_ha1
            ha1 = md5(a1.encode('utf-8')).hexdigest()
        a2 = request.method + ":" + auth.uri
        ha2 = md5(a2.encode('utf-8')).hexdigest()
        a3 = ha1 + ":" + auth.nonce + ":" + ha2
        response = md5(a3.encode('utf-8')).hexdigest()
        return response == auth.response
'''
