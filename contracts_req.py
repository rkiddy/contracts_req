
import sys

from dotenv import dotenv_values
from flask import Flask
from jinja2 import Environment, PackageLoader

cfg = dotenv_values(".env")

sys.path.append(f"{cfg['APP_HOME']}")
import data

contracts_req = Flask(__name__)
application = contracts_req
env = Environment(loader=PackageLoader('contracts_req'))


@contracts_req.route(f"/{cfg['WWW']}")
@contracts_req.route(f"/{cfg['WWW']}/")
def app_main():
    main = env.get_template('req_main.html')
    context = data.contracts_req_main()
    return main.render(**context)


if __name__ == '__main__':
    contracts_req.run()

