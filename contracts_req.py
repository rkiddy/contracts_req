
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


def auth(digest):
    if digest is None or digest != cfg['KEY']:
        raise Exception("Application must be accessed with key.")
    pass


@contracts_req.route(f"/{cfg['WWW']}<digest>")
@contracts_req.route(f"/{cfg['WWW']}<digest>/")
def req_main(digest):
    auth(digest)
    main = env.get_template('req_main.html')
    context = data.contracts_req_main(digest)
    return main.render(**context)


@contracts_req.route(f"/{cfg['WWW']}<digest>/add")
def req_add_form(digest):
    auth(digest)
    main = env.get_template('req_add.html')
    context = data.contracts_add_form(digest)
    context['digest'] = digest
    return main.render(**context)


@contracts_req.route(f"/{cfg['WWW']}<digest>/req_add", methods=['POST'])
def req_add(digest):
    auth(digest)
    data.contracts_req_add(request.form)
    return redirect(f"/contracts_req/{digest}/add")


@contracts_req.route(f"/{cfg['WWW']}<digest>/doc_add", methods=['POST'])
def doc_add(digest):
    auth(digest)
    data.contracts_doc_add(request.form)
    return redirect(f"/contracts_req/{digest}")


if __name__ == '__main__':
    contracts_req.run(port=8080)
