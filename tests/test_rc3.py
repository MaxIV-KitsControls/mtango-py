import sys
sys.path.insert(0, ".")

from conf import app_base
from main import app

from testconf import tango_host
from testutils import *


urltuple = (app_base,) + tango_host


def test_api_root():
	rq, rsp = app.test_client.get("%s/rc3" % app_base)
	b = mtango_object(rsp)
	assert "hosts" in b
	assert "x-auth-method" in b


def test_hosts():
	rq, rsp = app.test_client.get("%s/rc3/hosts" % app_base)
	b = mtango_object(rsp)
	assert b.keys()


def test_db_info():
	rq, rsp = app.test_client.get("%s/rc3/hosts/%s/%s" % urltuple)
	b = mtango_object(rsp)
	assert "name" in b
	assert "host" in b
	assert "port" in b
	assert "info" in b
	assert "devices" in b


def test_devices():
	rq, rsp = app.test_client.get("%s/rc3/hosts/%s/%s/devices" % urltuple)
	b = mtango_list(rsp)
	for dev in b:
		assert type(dev) == dict
		assert "name" in dev
		assert "href" in dev


def test_device():
	rq, rsp = app.test_client.get("%s/rc3/hosts/%s/%s/devices/sys/tg_test/1" % urltuple)
	b = mtango_object(rsp)
	assert "name" in b
	assert "info" in b
	assert "attributes" in b
	assert "commands" in b
	assert "pipes" in b
	assert "properties" in b
	assert "state" in b
	assert "_links" in b


def test_device_state():
	rq, rsp = app.test_client.get("%s/rc3/hosts/%s/%s/devices/sys/tg_test/1/state" % urltuple)
	b = mtango_object(rsp)
	assert "state" in b
	assert "status" in b
	assert "_links" in b


def test_attributes():
	rq, rsp = app.test_client.get("%s/rc3/hosts/%s/%s/devices/sys/tg_test/1/attributes" % urltuple)
	b = mtango_list(rsp)
	for attr in b:
		assert type(attr) == dict
		assert "name" in attr
		assert "value" in attr
		assert "info" in attr
		assert "properties" in attr
		assert "history" in attr
		assert "_links" in attr


def test_alt_attribute_value():
	rq, rsp = app.test_client.get("%s/rc3/hosts/%s/%s/devices/sys/tg_test/1/attributes/value?attr=double_scalar" % urltuple)
	b = mtango_list(rsp)
	for attr in b:
		assert type(attr) == dict
		assert "name" in attr
		assert "value" in attr
		assert "quality" in attr
		assert "timestamp" in attr


def test_alt_attribute_value_multi():
	rq, rsp = app.test_client.get("%s/rc3/hosts/%s/%s/devices/sys/tg_test/1/attributes/value?attr=double_scalar&attr=long_scalar" % urltuple)
	b = mtango_list(rsp)
	for attr in b:
		assert type(attr) == dict
		assert "name" in attr
		assert "value" in attr
		assert "quality" in attr
		assert "timestamp" in attr


def test_alt_attribute_info():
	rq, rsp = app.test_client.get("%s/rc3/hosts/%s/%s/devices/sys/tg_test/1/attributes/info?attr=double_scalar" % urltuple)
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
	rq, rsp = app.test_client.get("%s/rc3/hosts/%s/%s/devices/sys/tg_test/1/attributes/info?attr=double_scalar&attr=long_scalar" % urltuple)
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


def test_attribute():
	rq, rsp = app.test_client.get("%s/rc3/hosts/%s/%s/devices/sys/tg_test/1/attributes/double_scalar" % urltuple)
	b = mtango_object(rsp)
	assert "name" in b
	assert "value" in b
	assert "info" in b
	assert "properties" in b
	assert "history" in b
	assert "_links" in b


def test_attribute_value():
	rq, rsp = app.test_client.get("%s/rc3/hosts/%s/%s/devices/sys/tg_test/1/attributes/double_scalar/value" % urltuple)
	b = mtango_object(rsp)
	assert "name" in b
	assert "value" in b
	assert "quality" in b
	assert "timestamp" in b


def test_attribute_info():
	rq, rsp = app.test_client.get("%s/rc3/hosts/%s/%s/devices/sys/tg_test/1/attributes/double_scalar/info" % urltuple)
	b = mtango_object(rsp)
	assert "name" in b
	assert "writable" in b
	assert "data_format" in b
	assert "data_type" in b
	assert "max_dim_x" in b
	assert "max_dim_y" in b
	assert "description" in b
	assert "label" in b
	assert "unit" in b
	assert "standard_unit" in b
	assert "display_unit" in b
	assert "format" in b
	assert "min_value" in b
	assert "max_value" in b
	assert "min_alarm" in b
	assert "max_alarm" in b
	assert "writable_attr_name" in b
	assert "level" in b
	assert "extensions" in b
	assert "alarms" in b
	assert "events" in b
	assert "sys_extensions" in b
	assert "isMemorized" in b
	assert "isSetAtInit" in b
	assert "memorized" in b
	assert "root_attr_name" in b
	assert "enum_label" in b


def test_attribute_history():
	rq, rsp = app.test_client.get("%s/rc3/hosts/%s/%s/devices/sys/tg_test/1/attributes/double_scalar/history" % urltuple)
	b = mtango_list(rsp)
	for hi in b:
		assert type(hi) == dict
		assert "name" in hi
		assert "value" in hi
		assert "quality" in hi
		assert "timestamp" in hi


def test_attribute_properties():
	rq, rsp = app.test_client.get("%s/rc3/hosts/%s/%s/devices/sys/tg_test/1/attributes/double_scalar/properties" % urltuple)
	mtango_object(rsp)


def test_attribute_property():
	rq, rsp = app.test_client.get("%s/rc3/hosts/%s/%s/devices/sys/tg_test/1/attributes/double_scalar/properties/abs_change" % urltuple)
	mtango_object(rsp)


def test_commands():
	rq, rsp = app.test_client.get("%s/rc3/hosts/%s/%s/devices/sys/tg_test/1/commands" % urltuple)
	b = mtango_list(rsp)
	for cmd in b:
		assert type(cmd) == dict
		assert "name" in cmd
		assert "info" in cmd
		assert "history" in cmd
		assert "_links" in cmd


def test_command():
	rq, rsp = app.test_client.get("%s/rc3/hosts/%s/%s/devices/sys/tg_test/1/commands/State" % urltuple)
	b = mtango_object(rsp)
	assert "name" in b
	assert "info" in b
	assert "history" in b
	assert "_links" in b


def test_command_history():
	rq, rsp = app.test_client.get("%s/rc3/hosts/%s/%s/devices/sys/tg_test/1/commands/State/history" % urltuple)
	b = mtango_list(rsp)
	for hi in b:
		assert type(hi) == dict
		assert "name" in hi
		assert "output" in hi


def test_properties():
	rq, rsp = app.test_client.get("%s/rc3/hosts/%s/%s/devices/sys/tg_test/1/properties" % urltuple)
	b = mtango_list(rsp)
	for prop in b:
		assert type(prop) == dict
		assert "name" in prop
		assert "values" in prop


def test_property():
	rq, rsp = app.test_client.get("%s/rc3/hosts/%s/%s/devices/sys/tg_test/1/properties/polled_attr" % urltuple)
	b = mtango_object(rsp)
	assert "name" in b
	assert "values" in b


def test_pipes():
	rq, rsp = app.test_client.get("%s/rc3/hosts/%s/%s/devices/sys/tg_test/1/pipes" % urltuple)
	b = mtango_list(rsp)
	for pipe in b:
		assert type(pipe) == dict
		assert "name" in pipe
		assert "href" in pipe


def test_pipe():
	rq, rsp = app.test_client.get("%s/rc3/hosts/%s/%s/devices/sys/tg_test/1/pipes/string_long_short_ro" % urltuple)
	b = mtango_object(rsp)
	assert "name" in b
	assert "size" in b
	assert "timestamp" in b
	assert "data" in b
	assert "_links" in b
