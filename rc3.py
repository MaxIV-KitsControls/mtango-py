from sanic import Blueprint
from sanic.response import json

from tango import Database

from utils import buildurl
from cache import getDeviceProxy


api_rc3 = Blueprint("rc3")
db = Database()
tango_host = (db.get_db_host(), db.get_db_port())


@api_rc3.route("/")
async def api_root(rq):
	return json({
		"hosts": buildurl(rq, "rc3.hosts"),
		"x-auth-method": "none"
	})


@api_rc3.route("/hosts")
async def hosts(rq):
	return json({
		"%s:%s" % tango_host: buildurl(rq, "rc3.db_info", tango_host)
	})


@api_rc3.route("/hosts/<host>/<port:int>")
async def db_info(rq, host, port):
	info = db.get_info()
	return json({
		"name": info.split()[2],
		"host": db.get_db_host(),
		"port": db.get_db_port_num(),
		"info": info.split("\n"),
		"devices": buildurl(rq, "rc3.devices", tango_host)
	})


@api_rc3.route("/hosts/<host>/<port:int>/devices")
async def devices(rq, host, port):
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
			"href": buildurl(rq, "rc3.device_info", tango_host, dev)
		} for dev in devs]
	)


@api_rc3.route("/hosts/<host>/<port:int>/devices/<domain>/<family>/<member>")
async def device_info(rq, host, port, domain, family, member):
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
			"commands": "---",
			"pipes": "---",
			"properties": "---",
			"state": "---",
			"_links": {
				"_self": buildurl(rq, "rc3.device_info", tango_host, device),
				"_parent": buildurl(rq, "rc3.devices", tango_host)
			}
		}
	)


@api_rc3.route("/hosts/<host>/<port:int>/devices/<domain>/<family>/<member>/state")
async def attribute_value(rq, host, port, domain, family, member):
	device = "/".join((domain, family, member))
	proxy = await getDeviceProxy(device)
	state = await proxy.State()
	status = await proxy.Status()
	return json(
		{
			"state": str(state),
			"status": status,
			"_links": {
				"_state":
				"_status":
				"_parent":
				"_self":
			}
		}
	)


@api_rc3.route("/hosts/<host>/<port:int>/devices/<domain>/<family>/<member>/attributes")
async def attributes(rq, host, port, domain, family, member):
	device = "/".join((domain, family, member))
	proxy = await getDeviceProxy(device)
	attrs = proxy.get_attribute_list()
	return json(
		[{
			"name": attr,
			"value": buildurl(rq, "rc3.attribute_value", tango_host, device, attr=attr),
			"info": buildurl(rq, "rc3.attribute_info", tango_host, device, attr=attr),
			"properties": "---",
			"history": "---",
			"_links": {
				"_self": buildurl(rq, "rc3.attributes", tango_host, device)
			}
		} for attr in attrs]
	)


@api_rc3.route("/hosts/<host>/<port:int>/devices/<domain>/<family>/<member>/attributes/<attr>")
async def attribute(rq, host, port, domain, family, member, attr):
	device = "/".join((domain, family, member))
	proxy = await getDeviceProxy(device)
	return json(
		{
			"name": attr,
			"value": buildurl(rq, "rc3.attribute_value", tango_host, device, attr=attr),
			"info": buildurl(rq, "rc3.attribute_info", tango_host, device, attr=attr),
			"properties": "---",
			"history": "---",
			"_links": {
				"_self": buildurl(rq, "rc3.attribute", tango_host, device, attr=attr)
			}
		}
	)


@api_rc3.route("/hosts/<host>/<port:int>/devices/<domain>/<family>/<member>/attributes/<attr>/value")
async def attribute_value(rq, host, port, domain, family, member, attr):
	device = "/".join((domain, family, member))
	proxy = await getDeviceProxy(device)
	attr_value = await proxy.read_attribute(attr)
	return json(
		{
			"name": attr_value.name,
			"value": attr_value.value,
			"quality": str(attr_value.quality),
			"timestamp": attr_value.time.tv_sec
		}
	)


@api_rc3.route("/hosts/<host>/<port:int>/devices/<domain>/<family>/<member>/attributes/<attr>/info")
async def attribute_info(rq, host, port, domain, family, member, attr):
	device = "/".join((domain, family, member))
	proxy = await getDeviceProxy(device)
	attr_info = proxy.get_attribute_config(attr)
	return json(
		{
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
	)
