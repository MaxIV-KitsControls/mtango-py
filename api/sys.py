""" mtango-py system API """

from time import time
from sanic import Blueprint
from sanic.response import json

import conf
from utils import buildurl
from cache import deviceCache, attributeCache


api_sys = Blueprint("sys")


@api_sys.route(
	"/",
	methods=["GET", "OPTIONS"]
)
async def api_root(rq):
	return json(
		{
			"stats": buildurl(rq, "sys.stats"),
			"gc": [buildurl(rq, "sys.clean_devs"), buildurl(rq, "sys.clean_attrs")],
			"active": [buildurl(rq, "sys.active_devs"), buildurl(rq, "sys.active_attrs")],
			"config": buildurl(rq, "sys.config"),
			"version": "mtango-py %s" % str(conf.version)
		}
	)


@api_sys.route(
	"/stats",
	methods=["GET", "OPTIONS"]
)
async def stats(rq):
	return json("not implemented yet")


@api_sys.route(
	"/clean/devices",
	methods=["GET", "OPTIONS"]
)
async def clean_devs(rq):
	return json("not implemented yet")


@api_sys.route(
	"/clean/attributes",
	methods=["GET", "OPTIONS"]
)
async def clean_attrs(rq):
	return json("not implemented yet")


@api_sys.route(
	"/active/devices",
	methods=["GET", "OPTIONS"]
)
async def active_devs(rq):
	return json(
		[{
			"device": k,
			"created": v["created"],
			"accessed": v["accessed"]
		} for k, v in deviceCache.items()]
	)


@api_sys.route(
	"/active/attributes",
	methods=["GET", "OPTIONS"]
)
async def active_attrs(rq):
	return json(
		[{
			"attribute": k,
			"created": v["created"],
			"accessed": v["accessed"]
		} for k, v in attributeCache.items()]
	)


@api_sys.route(
	"/config",
	methods=["GET", "OPTIONS"]
)
async def config(rq):
	conf_keys = [k for k in conf.__dict__.keys() if not k.startswith("__") and k.lower() != "version"]
	clean_conf = {k: getattr(conf, k) for k in conf_keys}
	clean_conf.update({"version": str(conf.version)})		# version must be first converted to string
	return json(clean_conf)
