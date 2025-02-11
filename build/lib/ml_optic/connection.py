import requests
from requests.auth import HTTPDigestAuth
from requests.exceptions import HTTPError
from requests_toolbelt.multipart import decoder
import pandas as pd
import json
from io import StringIO
import csv
# ----------------------------------------------------------------------

class ConfigStruct:
    def __init__(self, **entries):
        self.__dict__.update(entries)


# ----------------------------------------------------------------------

class MLRESTConnection(object):

    def __init__(self):
        self.cfg = ConfigStruct(host='localhost', port='8000', user='admin', password='admin', scheme='xquery', action='eval', param=None)
        self.search = ConfigStruct(start='1', page='10')

    def call_rest(self, args, code):
        df = None
        optic = None
        self.cfg.scheme = args.parser
        result = self._eval_code(code,args)
        if result is not None:
            try:
                optic = json.dumps(result[0]['data'])
            except Exception as err:
                print("Failed to compile {} query".format(args.parser))

            if optic is not None:
                df = self._eval_optic(optic)
                print("Returned {} results in {}".format(len(df),args.variable))
        else:
            print("Failed to compile {} query".format(self.cfg.scheme))
        return df

    def _eval_code(self, code,args):
        session = requests.session()
        session.auth = HTTPDigestAuth(self.cfg.user, self.cfg.password)
        # replace result with export

        scheme = args.parser
        # replace result with export
        if scheme == 'xquery':
            code = code.replace('result()','export()')
            code = "xquery version '1.0-ml';\nimport module namespace op='http://marklogic.com/optic' at '/MarkLogic/optic.xqy';\n\n" + code
        if scheme == 'javascript':
            code = code.replace('result()','export()')
            code =  "'use strict'\nconst op = require('/MarkLogic/optic');\n\n" + code

        #(code)
        payload = {scheme: code}

        #logging.info(code)

        uri = 'http://%s:%s/v1/eval' % (self.cfg.host, self.cfg.port)
        data = None
        try:
            result = session.post(uri, data=payload)
            # If the response was successful, no Exception will be raised
            result.raise_for_status()
        except HTTPError as http_err:
            error = result.json()["errorResponse"]["message"]
            print(error)
        except Exception as err:
            print(f'Other error occurred: {err}')  # Python 3.6
        else:
                data = self._get_multi_result(result)
        return data

    def _eval_optic(self, optic):
        session = requests.session()
        session.auth = HTTPDigestAuth(self.cfg.user, self.cfg.password)
        params = {'output': 'object','column-types' : 'header'}
        plan = optic
        headers = {'Accept': 'text/csv','Content-type': 'application/json'}

        uri = 'http://%s:%s/v1/rows' % (self.cfg.host, self.cfg.port)
        data = None
        #print(code)
        try:
            result = session.post(uri, data=plan, headers=headers,params=params)

            # If the response was successful, no Exception will be raised
            result.raise_for_status()
        except HTTPError as http_err:
            error = result.json()["errorResponse"]["message"]
            print(error)
        except Exception as err:
            print(f'Other error occurred: {err}')  # Python 3.6
        else:
            #Comment out these rows just to get Json
            #data= pd.DataFrame.from_dict(result.json(), orient='columns')
            data= pd.read_csv(StringIO(result.text),skipinitialspace = True, quotechar = '"')
            #logging.info(code)

        return data

    def _get_multi_result(self,result):
        out = []
        multipart_data = decoder.MultipartDecoder.from_response(result)
        for part in multipart_data.parts:
            ctype = part.headers[b'Content-Type'].decode('utf-8')
            raw = part.content
            data = json.loads(raw) if (ctype == 'application/json') else raw
            out.append({'data' : data, 'type' : ctype})
        return out

    def endpoint(self,line):
        try:
            r = requests.utils.urlparse(line)
            self.cfg = ConfigStruct( host=r.hostname, port=r.port, user=r.username, password=r.password, scheme=r.scheme, action='eval', param=None)
        except:
            print('malformed connection' + line)
        return None
