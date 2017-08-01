import sys
sys.path.insert(0, ".")

from conf import app_base
from main import app

from testutils import *


def test_app_base_get():
	rq, rsp = app.test_client.get(app_base)
	b = mtango_object(rsp)			# this performs standard checks
	assert "rc3" in b
	assert "sys" in b				# the response should have at least rc3 and sys APIs
