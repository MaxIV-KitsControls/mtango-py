""" mtango-py system API """

import resource
from time import time

import tango
from sanic import Blueprint
from sanic.response import json, raw

import conf
import stats as stats_module
from utils import buildurl
from cache import getDeviceProxy, getAttributeProxy


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
			"active": [buildurl(rq, "sys.cache_devs"), buildurl(rq, "sys.cache_attrs")],
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
				"device": getDeviceProxy.cache_info()["currsize"],
				"attribute": getAttributeProxy.cache_info()["currsize"]
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
	getDeviceProxy.cache_clear()
	return raw(b"", status=204)		# No Content


@api_sys.route(
	"/clean/attributes",
	methods=["GET", "OPTIONS"]
)
async def clean_attrs(rq):
	""" AttributeProxy cache cleanup """
	getAttributeProxy.cache_clear()
	return raw(b"", status=204)		# No Content


@api_sys.route(
	"/cache/devices",
	methods=["GET", "OPTIONS"]
)
async def cache_devs(rq):
	""" DeviceProxies cache info """
	return json(getDeviceProxy.cache_info())


@api_sys.route(
	"/cache/attributes",
	methods=["GET", "OPTIONS"]
)
async def cache_attrs(rq):
	""" AttributeProxies cache info """
	return json(getAttributeProxy.cache_info())


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
