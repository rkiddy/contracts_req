
import sys

from dotenv import dotenv_values
from flask import Flask, redirect, request
from jinja2 import Environment, PackageLoader

import data

cfg = dotenv_values(".env")

sys.path.append(f"{cfg['APP_HOME']}")

contracts_req = Flask(__name__)
application = contracts_req
env = Environment(loader=PackageLoader('contracts_req'))


@contracts_req.route(f"/{cfg['WWW']}contracts_req")
@contracts_req.route(f"/{cfg['WWW']}contracts_req/")
def req_main():
    main = env.get_template('req_main.html')
    context = data.contracts_req_main()
    return main.render(**context)


@contracts_req.route(f"/{cfg['WWW']}contracts_req/add")
def req_add_form():
    main = env.get_template('req_add.html')
    context = data.contracts_add_form()
    return main.render(**context)


@contracts_req.route(f"/{cfg['WWW']}contracts_req/req_add", methods=['POST'])
def req_add():
    data.contracts_req_add(request.form)
    return redirect(f"/contracts_req/add")


@contracts_req.route(f"/{cfg['WWW']}contracts_req/doc_add", methods=['POST'])
def doc_add():
    data.contracts_doc_add(request.form)
    return redirect(f"/contracts_req/")


if __name__ == '__main__':
    contracts_req.run(port=8080)
