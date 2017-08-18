""" Python implementation of mTango rc3 API """

from time import time
from sanic import Blueprint
from sanic.response import json

from tango import Database, CmdArgType, DevFailed

import conf
from utils import buildurl
from cache import getDeviceProxy, getAttributeProxy
from exceptions import HTTP501_NotImplemented


api_rc3 = Blueprint("rc3")
db = Database()
tango_host = (db.get_db_host(), db.get_db_port())


@api_rc3.exception(DevFailed)
async def tango_error(request, exception):
	""" Tango exceptions handler """
	errors = []
	for err in exception.args:
		errors.append({
			"reason": err.reason,
			"description": err.desc,
			"severity": str(err.severity),
			"origin": err.origin
		})
	return json(
		{
			"errors": errors,
			"quality": "FAILURE",
			"timestamp": int(time())
		}
	)


@api_rc3.route(
	"/",
	methods=["GET", "OPTIONS"]
)
async def api_root(rq):
	""" rc3 API entry point """
	return json(
		{
			"hosts": buildurl(rq, "rc3.hosts"),
			"x-auth-method": "none"
		}
	)


@api_rc3.route(
	"/hosts",
	methods=["GET", "OPTIONS"]
)
async def hosts(rq):
	""" List available TANGO_HOSTs
		Actually, it returns only the system configured TANGO_HOST
	"""
	return json(
		{
			"%s:%s" % tango_host: buildurl(rq, "rc3.db_info", tango_host)
		}
	)


@api_rc3.route(
	"/hosts/<host>/<port:int>",
	methods=["GET", "OPTIONS"]
)
async def db_info(rq, host, port):
	""" Database information """
	info = db.get_info()
	return json(
		{
			"name": info.split()[2],
			"host": db.get_db_host(),
			"port": db.get_db_port_num(),
			"info": info.split("\n"),
			"devices": buildurl(rq, "rc3.devices", tango_host)
		}
	)


@api_rc3.route(
	"/hosts/<host>/<port:int>/devices",
	methods=["GET", "OPTIONS"]
)
async def devices(rq, host, port):
	""" Device list """
	devs = []
	domains = db.get_device_domain("*")
	for d in domains:
		families = db.get_device_family("%s/*" % d)
		for f in families:
			members = db.get_device_member("%s/%s/*" % (d, f))
			for m in members:
				devs.append('/'.join((d, f, m)))
	return json(
		[{
			"name": dev,
			"href": buildurl(rq, "rc3.device", tango_host, dev)
		} for dev in devs]
	)


@api_rc3.route(
	"/hosts/<host>/<port:int>/devices/<domain>/<family>/<member>",
	methods=["GET", "OPTIONS"]
)
async def device(rq, host, port, domain, family, member):
	""" Device info """
	device = "/".join((domain, family, member))
	proxy = await getDeviceProxy(device)
	import_info = proxy.import_info()
	info = proxy.info()

	return json(
		{
			"name": import_info.name,
			"info": {
				"last_exported": "---",
				"last_unexported": "---",
				"name": import_info.name,
				"ior": import_info.ior,
				"version": import_info.version,
				"exported": bool(import_info.exported),
				"pid": "---",
				"server": info.server_id,
				"hostname": info.server_host,
				"classname": info.dev_class,
				"is_taco": "---"
			},
			"attributes": buildurl(rq, "rc3.attributes", tango_host, device),
			"commands": buildurl(rq, "rc3.commands", tango_host, device),
			"pipes": buildurl(rq, "rc3.pipes", tango_host, device),
			"properties": buildurl(rq, "rc3.properties", tango_host, device),
			"state": buildurl(rq, "rc3.device_state", tango_host, device),
			"_links": {
				"_self": buildurl(rq, "rc3.device", tango_host, device),
				"_parent": buildurl(rq, "rc3.devices", tango_host)
			}
		}
	)


@api_rc3.route(
	"/hosts/<host>/<port:int>/devices/<domain>/<family>/<member>/state",
	methods=["GET", "OPTIONS"]
)
async def device_state(rq, host, port, domain, family, member):
	""" Device state """
	device = "/".join((domain, family, member))
	proxy = await getDeviceProxy(device)
	state = await proxy.State()
	status = await proxy.Status()
	return json(
		{
			"state": str(state),
			"status": status,
			"_links": {
				"_state": buildurl(rq, "rc3.attribute", tango_host, device, attr="State"),
				"_status": buildurl(rq, "rc3.attribute", tango_host, device, attr="Status"),
				"_parent": buildurl(rq, "rc3.device", tango_host, device),
				"_self": buildurl(rq, "rc3.device_state", tango_host, device)
			}
		}
	)


@api_rc3.route(
	"/hosts/<host>/<port:int>/devices/<domain>/<family>/<member>/attributes",
	methods=["GET", "OPTIONS"]
)
async def attributes(rq, host, port, domain, family, member):
	""" Device attributes list """
	device = "/".join((domain, family, member))
	proxy = await getDeviceProxy(device)
	attrs = proxy.get_attribute_list()
	return json(
		[{
			"name": attr,
			"value": buildurl(rq, "rc3.attribute_value", tango_host, device, attr=attr),
			"info": buildurl(rq, "rc3.attribute_info", tango_host, device, attr=attr),
			"properties": buildurl(rq, "rc3.attribute_properties", tango_host, device, attr=attr),
			"history": buildurl(rq, "rc3.attribute_history", tango_host, device, attr=attr),
			"_links": {
				"_self": buildurl(rq, "rc3.attributes", tango_host, device)
			}
		} for attr in attrs]
	)


# THIS NEEDS TO BE DEFINED BEFORE 'attribute' !!!
@api_rc3.route(
	"/hosts/<host>/<port:int>/devices/<domain>/<family>/<member>/attributes/value",
	methods=["GET", "OPTIONS", "PUT"]
)
async def alt_attribute_value(rq, host, port, domain, family, member):
	""" /Alternative/ method for getting attribute(s) value """
	if rq.method == "PUT":
		raise HTTP501_NotImplemented
	data = []
	if "attr" in rq.args:
		for attr in rq.args["attr"]:
			data.append(await attribute_value(rq, host, port, domain, family, member, attr, from_alt=True))
	return json(data)


# THIS NEEDS TO BE DEFINED BEFORE 'attribute' !!!
@api_rc3.route(
	"/hosts/<host>/<port:int>/devices/<domain>/<family>/<member>/attributes/info",
	methods=["GET", "OPTIONS"]
)
async def alt_attribute_info(rq, host, port, domain, family, member):
	""" /Alternative/ method for getting attribute(s) info """
	data = []
	if "attr" in rq.args:
		for attr in rq.args["attr"]:
			data.append(await attribute_info(rq, host, port, domain, family, member, attr, from_alt=True))
	return json(data)


@api_rc3.route(
	"/hosts/<host>/<port:int>/devices/<domain>/<family>/<member>/attributes/<attr>",
	methods=["GET", "OPTIONS"]
)
async def attribute(rq, host, port, domain, family, member, attr):
	""" Links for different things for device attribute """
	device = "/".join((domain, family, member))
	return json(
		{
			"name": attr,
			"value": buildurl(rq, "rc3.attribute_value", tango_host, device, attr=attr),
			"info": buildurl(rq, "rc3.attribute_info", tango_host, device, attr=attr),
			"properties": buildurl(rq, "rc3.attribute_properties", tango_host, device, attr=attr),
			"history": buildurl(rq, "rc3.attribute_history", tango_host, device, attr=attr),
			"_links": {
				"_self": buildurl(rq, "rc3.attribute", tango_host, device, attr=attr)
			}
		}
	)


@api_rc3.route(
	"/hosts/<host>/<port:int>/devices/<domain>/<family>/<member>/attributes/<attr>/value",
	methods=["GET", "OPTIONS", "PUT"]
)
async def attribute_value(rq, host, port, domain, family, member, attr, from_alt=False):
	""" Get attribute value """
	if rq.method == "PUT":
		raise HTTP501_NotImplemented
	device = "/".join((domain, family, member))
	proxy = await getDeviceProxy(device)
	attr_value = await proxy.read_attribute(attr)

	if attr_value.type in (CmdArgType.DevState,):
		value = str(attr_value.value)
	else:
		value = attr_value.value

	data = {
		"name": attr_value.name,
		"value": value,
		"quality": str(attr_value.quality),
		"timestamp": attr_value.time.tv_sec
	}

	return data if from_alt else json(data)


@api_rc3.route(
	"/hosts/<host>/<port:int>/devices/<domain>/<family>/<member>/attributes/<attr>/info",
	methods=["GET", "OPTIONS", "PUT"]
)
async def attribute_info(rq, host, port, domain, family, member, attr, from_alt=False):
	""" Get attribute info """
	if rq.method == "PUT":
		raise HTTP501_NotImplemented
	device = "/".join((domain, family, member))
	proxy = await getDeviceProxy(device)
	attr_info = proxy.get_attribute_config_ex(attr)[0]
	data = {
		"name": attr_info.name,
		"writable": str(attr_info.writable),
		"data_format": str(attr_info.data_format),
		"data_type": str(attr_info.data_type),
		"max_dim_x": attr_info.max_dim_x,
		"max_dim_y": attr_info.max_dim_y,
		"description": attr_info.description,
		"label": attr_info.label,
		"unit": attr_info.unit,
		"standard_unit": attr_info.standard_unit,
		"display_unit": attr_info.display_unit,
		"format": attr_info.format,
		"min_value": attr_info.min_value,
		"max_value": attr_info.max_value,
		"min_alarm": attr_info.min_alarm,
		"max_alarm": attr_info.max_alarm,
		"writable_attr_name": attr_info.writable_attr_name,
		"level": str(attr_info.disp_level),
		"extensions": attr_info.extensions,
		"alarms": attr_info.alarms,
		"events": attr_info.events,
		"sys_extensions": attr_info.sys_extensions,
		"isMemorized": "---",
		"isSetAtInit": "---",
		"memorized": str(attr_info.memorized),
		"root_attr_name": attr_info.root_attr_name,
		"enum_label": attr_info.enum_labels
	}
	return data if from_alt else json(data)


@api_rc3.route(
	"/hosts/<host>/<port:int>/devices/<domain>/<family>/<member>/attributes/<attr>/history",
	methods=["GET", "OPTIONS"]
)
async def attribute_history(rq, host, port, domain, family, member, attr):
	""" Get attribute history """
	attribute = "/".join((domain, family, member, attr))
	proxy = await getAttributeProxy(attribute)
	hist = proxy.history(10)
	return json(
		[{
			"name": h.name,
			"value": h.value,
			"quality": str(h.quality),
			"timestamp": h.time.tv_sec,
		} for h in hist]
	)


@api_rc3.route(
	"/hosts/<host>/<port:int>/devices/<domain>/<family>/<member>/attributes/<attr>/properties",
	methods=["GET", "OPTIONS"]
)
async def attribute_properties(rq, host, port, domain, family, member, attr):
	""" Get attribute properties """
	device = "/".join((domain, family, member))
	props = db.get_device_attribute_property(device, attr)[attr]
	if conf.rc3_mode == "strict":
		data = props
	else:
		data = [{
			"name": k,
			"_empty": not bool(len(v))		# don't ask me, mTango stuff...
		} for k, v in props.items()]
	return json(data)


@api_rc3.route(
	"/hosts/<host>/<port:int>/devices/<domain>/<family>/<member>/attributes/<attr>/properties/<prop>",
	methods=["GET", "OPTIONS", "PUT", "DELETE"]
)
async def attribute_property(rq, host, port, domain, family, member, attr, prop):
	""" Display single attribute property """
	if rq.method in ("PUT", "DELETE"):
		raise HTTP501_NotImplemented
	device = "/".join((domain, family, member))
	props = db.get_device_attribute_property(device, attr)[attr]
	return json(
		{
			prop: props[prop]
		}
	)


@api_rc3.route(
	"/hosts/<host>/<port:int>/devices/<domain>/<family>/<member>/commands",
	methods=["GET", "OPTIONS"]
)
async def commands(rq, host, port, domain, family, member):
	""" List of device commands """
	device = "/".join((domain, family, member))
	proxy = await getDeviceProxy(device)
	cmds = proxy.get_command_list()
	cmds_w_info = []
	for cmd in cmds:
		info = proxy.get_command_config(cmd)
		cmds_w_info.append({
			"name": cmd,
			"info": {
				"cmd_name": info.cmd_name,
				"cmd_tag": info.cmd_tag,
				"level": str(info.disp_level),
				"in_type": str(info.in_type),
				"out_type": str(info.out_type),
				"in_type_desc": info.in_type_desc,
				"out_type_desc": info.out_type_desc
			},
			"history": buildurl(rq, "rc3.command_history", tango_host, device, cmd=cmd),
			"_links": {
				"_self": buildurl(rq, "rc3.commands", tango_host, device)
			}
		})
	return json(cmds_w_info)


@api_rc3.route(
	"/hosts/<host>/<port:int>/devices/<domain>/<family>/<member>/commands/<cmd>",
	methods=["GET", "OPTIONS", "PUT"]
)
async def command(rq, host, port, domain, family, member, cmd):
	""" Display device command info """
	if rq.method == "PUT":
		raise HTTP501_NotImplemented
	device = "/".join((domain, family, member))
	proxy = await getDeviceProxy(device)
	info = proxy.get_command_config(cmd)
	return json(
		{
			"name": cmd,
			"info": {
				"cmd_name": info.cmd_name,
				"cmd_tag": info.cmd_tag,
				"level": str(info.disp_level),
				"in_type": str(info.in_type),
				"out_type": str(info.out_type),
				"in_type_desc": info.in_type_desc,
				"out_type_desc": info.out_type_desc
			},
			"history": buildurl(rq, "rc3.command_history", tango_host, device, cmd=cmd),
			"_links": {
				"_self": buildurl(rq, "rc3.command", tango_host, device, cmd=cmd)
			}
		}
	)


@api_rc3.route(
	"/hosts/<host>/<port:int>/devices/<domain>/<family>/<member>/commands/<cmd>/history",
	methods=["GET", "OPTIONS"]
)
async def command_history(rq, host, port, domain, family, member, cmd):
	""" Display device command history """
	device = "/".join((domain, family, member))
	proxy = await getDeviceProxy(device)
	hist = proxy.command_history(cmd, 10)
	return json(
		[{
			"name": cmd,
			"output": h.extract()
		} for h in hist]
	)


@api_rc3.route(
	"/hosts/<host>/<port:int>/devices/<domain>/<family>/<member>/properties",
	methods=["GET", "OPTIONS", "PUT", "POST"]
)
async def properties(rq, host, port, domain, family, member):
	""" Device property list """
	if rq.method in ("PUT", "POST"):
		raise HTTP501_NotImplemented
	device = "/".join((domain, family, member))
	proxy = await getDeviceProxy(device)
	props = proxy.get_property_list("*")
	return json(
		[{
			"name": prop,
			"values": proxy.get_property(prop)[prop],
		} for prop in props]
	)


@api_rc3.route(
	"/hosts/<host>/<port:int>/devices/<domain>/<family>/<member>/properties/<prop>",
	methods=["GET", "OPTIONS", "PUT", "POST", "DELETE"]
)
async def property(rq, host, port, domain, family, member, prop):
	""" Display device property value """
	if rq.method in ("PUT", "POST", "DELETE"):
		raise HTTP501_NotImplemented
	device = "/".join((domain, family, member))
	proxy = await getDeviceProxy(device)
	values = proxy.get_property(prop)[prop]
	return json(
		{
			"name": prop,
			"values": values,
		}
	)


@api_rc3.route(
	"/hosts/<host>/<port:int>/devices/<domain>/<family>/<member>/pipes",
	methods=["GET", "OPTIONS"]
)
async def pipes(rq, host, port, domain, family, member):
	""" Device pipes list """
	device = "/".join((domain, family, member))
	proxy = await getDeviceProxy(device)
	pipes = proxy.get_pipe_list()
	return json(
		[{
			"name": pipe,
			"href": buildurl(rq, "rc3.pipe", tango_host, device, pipe=pipe)
		} for pipe in pipes]
	)


@api_rc3.route(
	"/hosts/<host>/<port:int>/devices/<domain>/<family>/<member>/pipes/<pipe>",
	methods=["GET", "OPTIONS", "PUT"]
)
async def pipe(rq, host, port, domain, family, member, pipe):
	""" Display pipe info and contents """
	if rq.method == "PUT":
		raise HTTP501_NotImplemented
	device = "/".join((domain, family, member))
	proxy = await getDeviceProxy(device)
	value = await proxy.read_pipe(pipe)
	data = []
	for v in value[1]:
		data.append({
			"name": v["name"],
			"value": [v["value"]]
		})
	return json(
		{
			"name": pipe,
			"size": len(value),
			"timestamp": int(time()),
			"data": data,
			"_links": {
				"_self": buildurl(rq, "rc3.pipe", tango_host, device, pipe=pipe)
			}
		}
	)


@api_rc3.route(
	"/hosts/<host>/<port:int>/devices/<domain>/<family>/<member>/attributes/<attr>/change",
	methods=["GET", "OPTIONS"]
)
async def change_event(rq, host, port, domain, family, member, attr):
	raise HTTP501_NotImplemented


@api_rc3.route(
	"/hosts/<host>/<port:int>/devices/<domain>/<family>/<member>/attributes/<attr>/periodic",
	methods=["GET", "OPTIONS"]
)
async def periodic_event(rq, host, port, domain, family, member, attr):
	raise HTTP501_NotImplemented


@api_rc3.route(
	"/hosts/<host>/<port:int>/devices/<domain>/<family>/<member>/attributes/<attr>/user",
	methods=["GET", "OPTIONS"]
)
async def user_event(rq, host, port, domain, family, member, attr):
	raise HTTP501_NotImplemented
