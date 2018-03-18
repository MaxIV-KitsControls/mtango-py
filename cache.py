from tango.asyncio import DeviceProxy, AttributeProxy
from tango import CmdArgType

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

@async_lru(maxsize=cache_size)
async def getDeviceAttributeConfig(device_proxy, attribute):
	""" Get or create AttributeProxy """
	return device_proxy.get_attribute_config(attribute)

@async_lru(maxsize=cache_size)
async def getAttributeConfig(attribute_proxy):
	""" Get or create AttributeProxy """
	return await attribute_proxy.get_config()

def convertAttributeValue(config, text):
    """ Convert a text to the correct type"""
    if config.data_type != CmdArgType.DevString:
        #try:
            return float(text)
        #except ValueError:
        #    return text
    else:
        return text
