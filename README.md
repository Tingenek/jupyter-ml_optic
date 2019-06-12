# ml optic

This is a Jupyter Magic to run Optic statements against a MarkLogic endpoint.

### Installation

1. Download the code and run pip -install . from the directory
2. Start Jupyter and create a notebook.
3. Run %load_ext ml_optic. The notebook should reply:
  marklogic optic magic loaded.
4. You can use %%ml_optic? to get the docs
5. Open tests.ipynb for the test notebook

### Usage

The magic needs a connection string to a working MarkLogic endpoint along with user credentials. Internally, we use /v1/eval and /v1/rows so you need the following Privileges for the connecting user:

- http://marklogic.com/xdmp/privileges/xdmp-eval
- http://marklogic.com/xdmp/privileges/xdmp-eval-in
- http://marklogic.com/xdmp/privileges/xdbc-eval
- http://marklogic.com/xdmp/privileges/xdbc-eval-in
- http://marklogic.com/xdmp/privileges/rest-reader

In a cell as the first line put the magic, for example:
%%ml_optic op://admin:admin@localhost:8000  
The rest of the cell contains the Optic query, exactly as it would look in Query Console. Note it must finish with op:result()

#### Connections and Output

Once a connection is made it's persisted, so subsequent cells only need to have %%ml_optic in them. Output is to a named variable or ml_optic if not set. Results are returned as a Pandas DataFrame by default.

#### Substitution

Python variables can be substituted into the Optic query in the usual way {VAR}, i.e if there is a python var ROWS=10 then => op:limit({ROWS}) will be substituted before evaluation.

In the case of XQuery and Javascript, the optic library import will get inserted automatically into the first line of the cell..



#### Example

List all TDEs using the standard port using xquery as parser and default var.
```
%%ml_optic op://admin:admin@localhost:8000 -p xquery
op:from-view("sys", "sys_tables",'')
  => op:result()
```
