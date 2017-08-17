import functools
from collections import OrderedDict

def clear_all(cache):
	cache.clear()
	cache.hits = 0
	cache.misses = 0

def async_lru(maxsize=128):
	""" Asynchronous LRU cache
		Based on https://gist.github.com/jaredlunde/7a118c03c3e9b925f2bf
	"""
	cache = OrderedDict()
	cache.hits = 0
	cache.misses = 0

	def decorator(fn):
		@functools.wraps(fn)
		async def memoizer(*args, **kwargs):
			key = str((args, kwargs))
			try:
				cache[key] = cache.pop(key)
				cache.hits += 1
			except KeyError:
				cache.misses += 1
				if maxsize is not None:
					if len(cache) >= maxsize:
						cache.popitem(last=False)
				cache[key] = await fn(*args, **kwargs)
			return cache[key]

		memoizer.cache_info = lambda: {"hits": cache.hits, "misses": cache.misses, "currsize": len(cache), "maxsize": maxsize}
		memoizer.cache_clear = lambda: clear_all(cache)

		return memoizer

	return decorator
