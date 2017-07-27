from sanic import Sanic
from sanic.response import json
from sanic_cors import CORS

import conf
from utils import buildurl

from api.rc3 import api_rc3
from api.sys import api_sys


app = Sanic(__name__)
app.blueprint(api_rc3, url_prefix="%s/rc3" % conf.app_base)
app.blueprint(api_sys, url_prefix="%s/sys" % conf.app_base)
CORS(app, supports_credentials=True)


# Middleware functions
@app.middleware('response')
async def add_headers(request, response):
	response.headers["x-mtango"] = "mtango-py %s" % str(conf.version)
	response.headers["x-clacks-overhead"] = "GNU Terry Pratchett"


# Application routes
@app.route(conf.app_base, methods=["GET", "OPTIONS"])
async def list_api_versions(rq):
	return json(
		{
			"rc3": buildurl(rq, "rc3.api_root"),			# mTango rc3 API
			"sys": buildurl(rq, "sys.api_root")				# server system API
		}
	)


# Start server
app.run(
	host=conf.host,
	port=conf.port,
	workers=conf.workers,
	debug=conf.debug
)
