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
	mtango_empty(rsp)


def test_clean_attrs():
	rq, rsp = app.test_client.get("%s/sys/clean/attributes" % app_base)
	mtango_empty(rsp)


def test_cache_devs():
	rq, rsp = app.test_client.get("%s/sys/cache/devices" % app_base)
	b = mtango_object(rsp)
	assert "hits" in b
	assert "misses" in b
	assert "currsize" in b
	assert "maxsize" in b


def test_cache_attrs():
	rq, rsp = app.test_client.get("%s/sys/cache/attributes" % app_base)
	b = mtango_object(rsp)
	assert "hits" in b
	assert "misses" in b
	assert "currsize" in b
	assert "maxsize" in b


def test_config():
	rq, rsp = app.test_client.get("%s/sys/config" % app_base)
	b = mtango_object(rsp)
	assert "version" in b
	assert b["version"] == str(version)
