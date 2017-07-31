import sys
sys.path.insert(0, ".")

from conf import app_base
from main import app

from testutils import *


tango_host = None
urltuple = None


def create_url_tuple():
	global urltuple
	urltuple = (app_base,) + tuple(tango_host)


def test_api_root():
	rq, rsp = app.test_client.get("%s/rc3" % app_base)
	b = mtango_object(rsp)
	assert "hosts" in b
	assert "x-auth-method" in b


def test_hosts():
	global tango_host
	rq, rsp = app.test_client.get("%s/rc3/hosts" % app_base)
	b = mtango_object(rsp)
	try:
		tango_host = list(b.keys())[0].split(":")
	except:
		assert False

	create_url_tuple()		# create url tuple with discovered tango_host


def test_db_info():
	rq, rsp = app.test_client.get("%s/rc3/hosts/%s/%s" % urltuple)
	b = mtango_object(rsp)
	assert "name" in b
	assert "host" in b
	assert "port" in b
	assert "info" in b
	assert "devices" in b


def test_devices():
	global urltuple
	rq, rsp = app.test_client.get("%s/rc3/hosts/%s/%s/devices" % urltuple)
	b = mtango_list(rsp)
	for dev in b:
		assert type(dev) == dict
		assert "name" in dev
		assert "href" in dev

	urltuple = urltuple + ("sys/tg_test/1",)		# update urltuple for further tests


def test_device():
	rq, rsp = app.test_client.get("%s/rc3/hosts/%s/%s/devices/%s" % urltuple)
	b = mtango_object(rsp)
	assert "name" in b
	assert "info" in b
	assert "attributes" in b
	assert "commands" in b
	assert "pipes" in b
	assert "properties" in b
	assert "state" in b
	assert "_links" in b


# def test_device_state():
# 	rq, rsp = app.test_client.get("%s/rc3/hosts/%s/%s/devices/%s/state" % urltuple)
# 	b = mtango_object(rsp)
# 	assert "state" in b
# 	assert "status" in b
# 	assert "_links" in b


def test_attributes():
	rq, rsp = app.test_client.get("%s/rc3/hosts/%s/%s/devices/%s/attributes" % urltuple)
	b = mtango_list(rsp)
	for attr in b:
		assert type(attr) == dict
		assert "name" in attr
		assert "value" in attr
		assert "info" in attr
		assert "properties" in attr
		assert "history" in attr
		assert "_links" in attr


# def test_alt_attribute_value():
# 	rq, rsp = app.test_client.get("%s/rc3/hosts/%s/%s/devices/%s/attributes/value?attr=double_scalar" % urltuple)
# 	b = mtango_list(rsp)
# 	for attr in b:
# 		assert type(attr) == dict
# 		assert "name" in attr
# 		assert "value" in attr
# 		assert "quality" in attr
# 		assert "timestamp" in attr


# def test_alt_attribute_value_multi():
# 	rq, rsp = app.test_client.get("%s/rc3/hosts/%s/%s/devices/%s/attributes/value?attr=double_scalar&attr=long_scalar" % urltuple)
# 	b = mtango_list(rsp)
# 	for attr in b:
# 		assert type(attr) == dict
# 		assert "name" in attr
# 		assert "value" in attr
# 		assert "quality" in attr
# 		assert "timestamp" in attr


def test_alt_attribute_info():
	rq, rsp = app.test_client.get("%s/rc3/hosts/%s/%s/devices/%s/attributes/info?attr=double_scalar" % urltuple)
	b = mtango_list(rsp)
	for attr in b:
		assert type(attr) == dict
		assert "name" in attr
		assert "writable" in attr
		assert "data_format" in attr
		assert "data_type" in attr
		assert "max_dim_x" in attr
		assert "max_dim_y" in attr
		assert "description" in attr
		assert "label" in attr
		assert "unit" in attr
		assert "standard_unit" in attr
		assert "display_unit" in attr
		assert "format" in attr
		assert "min_value" in attr
		assert "max_value" in attr
		assert "min_alarm" in attr
		assert "max_alarm" in attr
		assert "writable_attr_name" in attr
		assert "level" in attr
		assert "extensions" in attr
		assert "alarms" in attr
		assert "events" in attr
		assert "sys_extensions" in attr
		assert "isMemorized" in attr
		assert "isSetAtInit" in attr
		assert "memorized" in attr
		assert "root_attr_name" in attr
		assert "enum_label" in attr


def test_alt_attribute_info_multi():
	rq, rsp = app.test_client.get("%s/rc3/hosts/%s/%s/devices/%s/attributes/info?attr=double_scalar&attr=long_scalar" % urltuple)
	b = mtango_list(rsp)
	for attr in b:
		assert type(attr) == dict
		assert "name" in attr
		assert "writable" in attr
		assert "data_format" in attr
		assert "data_type" in attr
		assert "max_dim_x" in attr
		assert "max_dim_y" in attr
		assert "description" in attr
		assert "label" in attr
		assert "unit" in attr
		assert "standard_unit" in attr
		assert "display_unit" in attr
		assert "format" in attr
		assert "min_value" in attr
		assert "max_value" in attr
		assert "min_alarm" in attr
		assert "max_alarm" in attr
		assert "writable_attr_name" in attr
		assert "level" in attr
		assert "extensions" in attr
		assert "alarms" in attr
		assert "events" in attr
		assert "sys_extensions" in attr
		assert "isMemorized" in attr
		assert "isSetAtInit" in attr
		assert "memorized" in attr
		assert "root_attr_name" in attr
		assert "enum_label" in attr
