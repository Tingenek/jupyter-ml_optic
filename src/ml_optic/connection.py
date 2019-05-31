import requests
from requests.auth import HTTPDigestAuth
from requests.exceptions import HTTPError
from requests_toolbelt.multipart import decoder
import pandas as pd
from pandas.io.json import json_normalize
import json
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
        result = self._eval_code(code)
        optic = json.dumps(result[0]['data'])
        df = self._eval_optic(optic)
        return df

    def _eval_code(self, code):
        session = requests.session()
        session.auth = HTTPDigestAuth(self.cfg.user, self.cfg.password)
        # replace result with export
        code = code.replace('op:result','op:export')
        payload = {'xquery': code}

        #logging.info(code)

        uri = 'http://%s:%s/v1/eval' % (self.cfg.host, self.cfg.port)
        data = None
        #print(code)
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
        params = {'output': 'array','column-types' : 'header'}
        plan = optic
        headers = {'Accept': 'application/json','Content-type': 'application/json'}

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
            data= pd.DataFrame.from_dict(result.json(), orient='columns')
            #logging.info(code)

        return data

    def _get_multi_result(self,result):
        out = []
        multipart_data = decoder.MultipartDecoder.from_response(result)
        print("Returned {} results".format(len(multipart_data.parts)))
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
