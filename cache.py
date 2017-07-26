from time import time
from tango.asyncio import DeviceProxy, AttributeProxy

deviceCache = {}
attributeCache = {}


async def getDeviceProxy(device):
	if hasattr(deviceCache, device):
		proxy = deviceCache[device]["proxy"]
		deviceCache[device]["accessed"] = time()
	else:
		proxy = await DeviceProxy(device)
		deviceCache[device] = {
			"proxy": proxy,
			"created": time(),
			"accessed": time()
		}
	return proxy


async def getAttributeProxy(attr):
	if hasattr(attributeCache, attr):
		proxy = attributeCache[attr]["proxy"]
		attributeCache[attr]["accessed"] = time()
	else:
		proxy = await AttributeProxy(attr)
		attributeCache[attr] = {
			"proxy": proxy,
			"created": time(),
			"accessed": time()
		}
	return proxy
