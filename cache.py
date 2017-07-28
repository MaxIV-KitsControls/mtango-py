from time import time
from tango.asyncio import DeviceProxy, AttributeProxy

deviceCache = {}
attributeCache = {}


async def getDeviceProxy(device):
	""" Get or create DeviceProxy """
	global deviceCache
	if device in deviceCache:
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
	""" Get or create AttributeProxy """
	global attributeCache
	if attr in attributeCache:
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
