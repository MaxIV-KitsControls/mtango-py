from time import time

from sanic import Sanic
from sanic.response import json
from sanic.exceptions import SanicException
from sanic_cors import CORS

import conf
import stats
from utils import buildurl

from api.rc3 import api_rc3
from api.sys import api_sys

stats.start_time = time()

app = Sanic(__name__)
app.blueprint(api_rc3, url_prefix="%s/rc3" % conf.app_base)
app.blueprint(api_sys, url_prefix="%s/sys" % conf.app_base)
CORS(app, supports_credentials=True)


# Middleware functions
@app.middleware("response")
async def add_headers(request, response):
	""" Add custom server headers """
	response.headers["x-mtango"] = "mtango-py %s" % str(conf.version)
	response.headers["x-clacks-overhead"] = "GNU Terry Pratchett"


@app.middleware("request")
async def request_counter(request):
	""" Count requests """
	stats.total_rq += 1


@app.middleware("response")
async def response_counter(request, response):
	""" Count responses """
	stats.total_resp += 1


# Error handlers
@app.exception(SanicException)
async def server_error(request, exception):
	""" General exception handler """
	return json(
		{
			"errors": exception.args,
			"quality": "FAILURE",
			"http_status": exception.status_code,
			"timestamp": time()
		},
		status=exception.status_code
	)


# Static files - Swagger definitions
app.static("/swagger/main.yml", "doc/swagger_main.yml")
app.static("/swagger/rc3.yml", "doc/swagger_rc3.yml")
app.static("/swagger/sys.yml", "doc/swagger_sys.yml")


# Application routes
@app.route(conf.app_base, methods=["GET", "OPTIONS"])
async def list_api_versions(rq):
	""" Application entry point: list available APIs """
	return json(
		{
			"rc3": buildurl(rq, "rc3.api_root"),			# mTango rc3 API
			"sys": buildurl(rq, "sys.api_root")				# server system API
		}
	)


# Start server
if __name__ == "__main__":
	app.run(
		host=conf.host,
		port=conf.port,
		workers=conf.workers,
		debug=conf.debug
	)
