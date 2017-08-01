import sys
sys.path.insert(0, ".")

from conf import app_base, version
from main import app

from testconf import tango_host
from testutils import *


def test_api_root():
	rq, rsp = app.test_client.get("%s/sys" % app_base)
	b = mtango_object(rsp)
	assert "stats" in b
	assert "gc" in b
	assert "active" in b
	assert "config" in b
	assert "version" in b
	assert b["version"] == "mtango-py %s" % str(version)


def test_stats():
	rq, rsp = app.test_client.get("%s/sys/stats" % app_base)
	b = mtango_object(rsp)
	assert "proxies" in b
	assert "time" in b
	assert "running_since" in b
	assert "resource" in b
	assert "requests" in b
	assert "responses" in b


def test_clean_devs():
	rq, rsp = app.test_client.get("%s/sys/clean/devices" % app_base)
	b = mtango_object(rsp)
	assert "parameters" in b


def test_clean_attrs():
	rq, rsp = app.test_client.get("%s/sys/clean/attributes" % app_base)
	b = mtango_object(rsp)
	assert "parameters" in b


def test_clean_devs_w_param():
	rq, rsp = app.test_client.get("%s/sys/clean/devices?max_age=100" % app_base)
	b = mtango_object(rsp)
	assert "removed_idle" in b
	assert "removed_age" in b


def test_clean_attrs_w_param():
	rq, rsp = app.test_client.get("%s/sys/clean/attributes?max_idle=100" % app_base)
	b = mtango_object(rsp)
	assert "removed_idle" in b
	assert "removed_age" in b


def test_active_devs():
	# first create DeviceProxy
	app.test_client.get("%s/rc3/hosts/%s/%s/devices/sys/tg_test/1" % ((app_base,) + tango_host))

	rq, rsp = app.test_client.get("%s/sys/active/devices" % app_base)
	b = mtango_list(rsp)
	for dev in b:
		assert "device" in dev
		assert "created" in dev
		assert "accessed" in dev


def test_active_attrs():
	# first create AttributeProxy
	app.test_client.get("%s/rc3/hosts/%s/%s/devices/sys/tg_test/1/double_scalar/history" % ((app_base,) + tango_host))

	rq, rsp = app.test_client.get("%s/sys/active/attributes" % app_base)
	b = mtango_list(rsp)
	for attr in b:
		assert "attribute" in attr
		assert "created" in attr
		assert "accessed" in attr


def test_config():
	rq, rsp = app.test_client.get("%s/sys/config" % app_base)
	b = mtango_object(rsp)
	assert "version" in b
	assert b["version"] == str(version)
