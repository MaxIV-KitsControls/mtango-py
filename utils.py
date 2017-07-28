def buildurl(rq, handler, tango_host=None, device=None, **kwargs):
	""" Build URL for specific endpoint """
	if tango_host:
		kwargs.update({"host": tango_host[0], "port": tango_host[1]})
	if device:
		devs = device.split("/")
		kwargs.update({"domain": devs[0], "family": devs[1], "member": devs[2]})
	return "%s://%s%s" % (rq.scheme, rq.host, rq.app.url_for(handler, **kwargs))


class Version(tuple):
	""" Strigifiable and URLable version """
	def _as_str_tuple(self):
		return tuple(str(x) for x in self)

	def __str__(self):
		base_version = ".".join(self._as_str_tuple()[:-1])
		if len(self) <= 3:
			return base_version
		else:
			return "-".join(
				(
					base_version,
					self._as_str_tuple()[-1]
				)
			)

	def url(self):
		return "/".join(self._as_str_tuple())
