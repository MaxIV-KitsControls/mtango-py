""" mtango-py system API """

import resource
from time import time

import tango
from sanic import Blueprint
from sanic.response import json

import conf
import stats as stats_module
from utils import buildurl
from cache import deviceCache, attributeCache


api_sys = Blueprint("sys")


@api_sys.route(
	"/",
	methods=["GET", "OPTIONS"]
)
async def api_root(rq):
	""" System API entry point: links to other functions """
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
	""" Server statistics """
	usage = resource.getrusage(resource.RUSAGE_SELF)
	return json(
		{
			"proxies": {
				"device": len(deviceCache),
				"attribute": len(attributeCache)
			},
			"time": time(),
			"running_since": stats_module.start_time,
			"resource": {
				"user_time": usage.ru_utime,
				"system_time": usage.ru_stime,
				"max_resident_mem": usage.ru_maxrss,
				"shared_mem": usage.ru_ixrss,
				"unshared_mem": usage.ru_idrss,
				"unshared_stack_mem": usage.ru_isrss,
				"sent_msgs": usage.ru_msgsnd,
				"recv_msgs": usage.ru_msgrcv,
				"page_faults": {
					"major": usage.ru_majflt,
					"minor": usage.ru_minflt
				},
				"swap_out": usage.ru_nswap,
				"block": {
					"input": usage.ru_inblock,
					"output": usage.ru_oublock
				},
				"signals": usage.ru_nsignals,
				"context_switch": {
					"voluntary": usage.ru_nvcsw,
					"involuntary": usage.ru_nivcsw
				}
			},
			"requests": stats_module.total_rq,
			"responses": stats_module.total_resp
		}
	)


@api_sys.route(
	"/clean/devices",
	methods=["GET", "OPTIONS"]
)
async def clean_devs(rq):
	""" DeviceProxy cache cleanup """
	return await clean(rq, deviceCache)


@api_sys.route(
	"/clean/attributes",
	methods=["GET", "OPTIONS"]
)
async def clean_attrs(rq):
	""" AttributeProxy cache cleanup """
	return await clean(rq, attributeCache)


async def clean(rq, cache):
	""" Generic cache cleanup """
	max_age = None
	max_idle = None
	removed_age = []
	removed_idle = []
	now = time()
	if "max_age" in rq.args:
		max_age = float(rq.args["max_age"][0])
		for k, v in cache.items():
			if now - v["created"] > max_age:
				removed_age.append(k)
		for k in removed_age:
			del cache[k]
	if "max_idle" in rq.args:
		max_idle = float(rq.args["max_idle"][0])
		for k, v in cache.items():
			if now - v["accessed"] > max_idle:
				removed_idle.append(k)
		for k in removed_idle:
			del cache[k]
	if not (max_age or max_idle):
		return json(
			{
				"parameters": {
					"max_idle": "Remove proxies not used for at least <value> seconds.",
					"max_age": "Remove proxies older than <value> seconds, regardless when they were last used."
				}
			}
		)
	else:
		return json(
			{
				"removed_idle": removed_idle,
				"removed_age": removed_age
			}
		)


@api_sys.route(
	"/active/devices",
	methods=["GET", "OPTIONS"]
)
async def active_devs(rq):
	""" List cached DeviceProxies """
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
	""" List cached AttributeProxies """
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
	""" Display server configuration """
	conf_keys = [k for k in conf.__dict__.keys() if not k.startswith("__") and k.lower() != "version"]
	clean_conf = {k: getattr(conf, k) for k in conf_keys}
	tango_host = tango.ApiUtil.get_env_var("TANGO_HOST")
	clean_conf.update(
		{
			"version": str(conf.version),		# version must be first converted to string
			"TANGO_HOST": tango_host
		}
	)
	return json(clean_conf)
