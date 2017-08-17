from tango.asyncio import DeviceProxy, AttributeProxy

from conf import cache_size
from async_lru import async_lru


@async_lru(maxsize=cache_size)
async def getDeviceProxy(device):
	""" Get or create DeviceProxy """
	return await DeviceProxy(device)


@async_lru(maxsize=cache_size)
async def getAttributeProxy(attr):
	""" Get or create AttributeProxy """
	return await AttributeProxy(attr)
