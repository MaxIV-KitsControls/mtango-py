from functools import lru_cache
from tango.asyncio import DeviceProxy, AttributeProxy

from conf import cache_size


@lru_cache(maxsize=cache_size)
async def getDeviceProxy(device):
	""" Get or create DeviceProxy """
	return await DeviceProxy(device)


@lru_cache(maxsize=cache_size)
async def getAttributeProxy(attr):
	""" Get or create AttributeProxy """
	return await AttributeProxy(attr)
