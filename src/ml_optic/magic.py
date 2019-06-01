from __future__ import print_function

from IPython.core.magic import (Magics, magics_class, line_magic,
                                cell_magic, line_cell_magic, needs_local_scope)
from IPython.core.magic_arguments import argument, magic_arguments, parse_argstring

import requests
from requests.auth import HTTPDigestAuth
from requests_toolbelt.multipart import decoder
from IPython.core.display import display

from .connection import MLRESTConnection

# The class MUST call this class decorator at creation time
# print("Full access to the main IPython object:", self.shell)
# print("Variables in the user namespace:", list(self.shell.user_ns.keys()))

@magics_class
class MarkLogicOpticMagic(Magics):

    def __init__(self,shell):
        # You must call the parent constructor
        super(MarkLogicOpticMagic, self).__init__(shell)
        self.connection = MLRESTConnection()
        self.ret_var = 'result_var'

    @magic_arguments()
    @cell_magic
    @argument(
        '-v', '--variable',default='ml_optic',
        help='output to a var, default is ml_optic'
    )
    @argument(
        '-o', '--output',default='ml_optic',
        help='output format, default is pandas DataFrame'
        )
    @argument(
        'connection', default=None,nargs='?',
        help='connection string; can be empty if set previously.'
    )
    def ml_optic(self, line=None, cell=None,local_ns={}):
        user_ns = self.shell.user_ns.copy()
        user_ns.update(local_ns)
        args = parse_argstring(self.ml_optic, line)
        args.mode='fetch'
        df = None
        if cell is None:
            print("No contents")
        else:
            #reset connection if given
            if args.connection is not None:
                self.connection.endpoint(args.connection)
            #expand out {var} in cell body
            cell = cell.format(**user_ns)
            result = self.connection.call_rest(args, cell)
            if result is not None:
                df = result
                print(args.output + '.head() returns:')
                display(result.head())
            else:
                print('No results')
            self.shell.user_ns.update({args.output: df})



def load_ipython_extension(ipython, *args):
    ipython.register_magics(MarkLogicOpticMagic)
    print("marklogic optic magic loaded.")


def unload_ipython_extension(ipython):
    print("marklogic optic magic unloaded.")
