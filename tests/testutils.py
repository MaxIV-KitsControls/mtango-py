import json


def body(rsp):
	return json.loads(rsp.body.decode())


def status(rsp, status):
	return rsp.status == status


def xmtango(rsp):
	return "x-mtango" in rsp.headers


def is_valid_json(rsp):
	try:
		body(rsp)
	except:
		return False
	else:
		return True


def is_list(rsp):
	r = body(rsp)
	return type(r) == list


def is_object(rsp):
	r = body(rsp)
	return type(r) == dict


def mtango_list(rsp):
	assert status(rsp, 200)
	assert xmtango(rsp)
	assert is_valid_json(rsp)
	assert is_list(rsp)
	return body(rsp)


def mtango_object(rsp):
	assert status(rsp, 200)
	assert xmtango(rsp)
	assert is_valid_json(rsp)
	assert is_object(rsp)
	return body(rsp)

def mtango_empty(rsp):
	assert status(rsp, 204)
	assert xmtango(rsp)
