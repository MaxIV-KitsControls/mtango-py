from sanic import Sanic
from sanic.response import json
from sanic_cors import CORS

from conf import app_base
from utils import buildurl
from rc3 import api_rc3


app = Sanic(__name__)
app.blueprint(api_rc3, url_prefix="%s/rc3" % app_base)
CORS(app, supports_credentials=True)


@app.route(app_base, methods=["GET", "OPTIONS"])
async def list_api_versions(rq):
	return json(
		{
			"rc3": buildurl(rq, "rc3.api_root")
		}
	)

app.run(host="0.0.0.0", port=8000, debug=True)
