def buildurl(rq, handler, tango_host=None, device=None, **kwargs):
	if tango_host:
		kwargs.update({"host": tango_host[0], "port": tango_host[1]})
	if device:
		devs = device.split("/")
		kwargs.update({"domain": devs[0], "family": devs[1], "member": devs[2]})
	return "%s://%s%s" % (rq.scheme, rq.host, rq.app.url_for(handler, **kwargs))
