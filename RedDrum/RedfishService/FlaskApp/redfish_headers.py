
# Copyright Notice:
# Copyright 2016 Distributed Management Task Force, Inc. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Profile-Simulator/LICENSE.md


from functools import wraps
from flask import request, Response, make_response

#
def error_no_host():
    return Response('400-Bad Request', 400)

# Function used to check if header['Accept'] contains 'application/xml' or not
# Output : 406-Not Acceptable
def error_metadata_handler():
    return Response('406-Not Acceptable',  406, {'Accept': "application/xml"})

# Function used to check if header['Content-Tpe'] contains 'charset=utf-8,application/json' or not
# Output : 415-Unsupported Media Type
def content_type_error_handler():
    return Response('415-Unsupported Media Type' , 415, {'Content-Type': "charset=utf-8;application/json"})

# Function used to check if header['OData-Version'] contains '4.0' or not
# Output : 412-Precondition Failed
def odata_error_handler():
    return Response('412-Precondition Failed', 412, {'OData-Version': '4.0'})

def rfcheckHeaders(*o_args, **o_kwargs):
    
    def header_processor(fn):
        '''
            Decorator that checks that requests
            headers and validates them accordingly to 
            DMRF standards.

            Usage:
            @app.route("/")
            @header_processor
            def func():
                pass
        '''
        @wraps(fn)
        def decorated(*args, **kwargs):
            
            if 'Host' not in request.headers:
                return error_no_host()

            # Checks for metadata URI contains 'application/xml' in 'Accept' header or not
            if 'metadata' in o_kwargs:
                if o_kwargs['metadata'] and 'Accept' in request.headers:
                    #print (request.headers)
                    if 'application/xml' not in request.headers['Accept'].lower():
                        return error_metadata_handler()
            # Checks for rest of URI contains 'application/json' in 'Accept' header or not 
            if ('metadata' not in o_kwargs):
                if ('Accept' in request.headers and ('application/json' not in request.headers['Accept'].lower() ) ):
                    return error_metadata_handler()

            # Checks for methods of PATCH and POST if "Content-Type" in header contains 'charset=utf-8', 'application/json' 
            # or not
            if any(x in request.method for x in ('PATCH', 'POST'))  and ('Content-Type' in request.headers):
                if not ( any(x in request.headers['Content-Type']  for x in ('charset=utf-8', 'application/json') ) ) :
                    return content_type_error_handler()

            # Checks for OData-Version if present is 4.0 or not
            if not ('OData-Version' in request.headers and request.headers['OData-Version'] ==  '4.0'):
                return odata_error_handler()                    

            return (fn(*args, **kwargs))    
        return (decorated)
    return header_processor



def rfaddHeaders(*o_args, **o_kwargs):
    
    def add_header_processor(fn):
        '''
            Decorator that adds required appropriate
            headers to the returning reponse accordingly to 
            DMRF standards.

            Usage:
            @app.route("/")
            @rfaddHeaders
            def func():
                pass
        '''
        @wraps(fn)
        def decorated(*args, **kwargs):
            response = make_response(fn(*args, **kwargs))
            if 'schemafile' in o_kwargs and o_kwargs['schemafile']:
                response.headers['Content-Type'] = "applcation/json; charset=utf-8"
            else:            
                response.headers['OData-Version'] = '4.0'
                response.headers['HttpHeaderServer'] = o_args[0].HttpHeaderServer
                response.headers['HttpHeaderCacheControl'] = o_args[0].HttpHeaderCacheControl
                response.headers['Allow'] = request.method
                if 'Origin' in request.headers:
                    response.headers['Access-Control-Allow-Origin'] = request.headers['Origin']
                if 'metadata' in o_kwargs and o_kwargs['metadata']: 
                    response.headers['Content-Type'] = "application/xml; charset=utf-8"
                else:
                    response.headers['Content-Type'] = "applcation/json; charset=utf-8"
            return (response)    
        return (decorated)
    return add_header_processor
