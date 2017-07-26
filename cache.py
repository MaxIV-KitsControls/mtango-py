from time import time
from tango.asyncio import DeviceProxy

deviceCache = {}


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