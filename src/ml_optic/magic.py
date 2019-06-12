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
        self.variable = 'ml_optic'
        self.parser = 'javascript'

    @magic_arguments()
    @cell_magic
    @argument(
        '-v', '--variable',default=None,
        help='output to a var, default is ml_optic'
    )
    @argument(
        '-p', '--parser',default=None,
        help='parser, xquery or javascript. default is javascript'
    )
    @argument(
        'connection', default=None,nargs='?',
        help='connection string; can be empty if set previously.'
    )
    def ml_optic(self, line=None, cell=None,local_ns={}):
        user_ns = self.shell.user_ns.copy()
        user_ns.update(local_ns)
        args = parse_argstring(self.ml_optic, line)
        if args.parser is not None:
            self.parser = args.parser
        else:
            args.parser = self.parser

        if args.variable is not None:
            self.variable = args.variable
        else:
            args.variable = self.variable


        df = None
        result = None
        if cell is None:
            print("No contents")
        else:
            #reset connection if given
            if args.connection is not None:
                self.connection.endpoint(args.connection)
            #expand out {var} in cell body
            try:
                cell = cell.format(**user_ns)
                result = self.connection.call_rest(args, cell)
            except Exception as err:
                print(f'Other error: {err}')  # Python 3.6

            if result is not None:
                df = result
                print(args.variable + '.head() returns:')
                display(result.head())
            else:
                print('No results')
            self.shell.user_ns.update({args.variable: df})



def load_ipython_extension(ipython, *args):
    ipython.register_magics(MarkLogicOpticMagic)
    print("marklogic optic magic loaded.")


def unload_ipython_extension(ipython):
    print("marklogic optic magic unloaded.")
