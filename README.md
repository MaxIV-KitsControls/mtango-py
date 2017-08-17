# mtango-py

Python implementation of mTango API

---
## Description
This project aims to be a drop-in replacement for mTango (mtangorest.server).  
Currently it supports a subset of `rc3` mTango API, mostly functions related to reading data from Tango. Supported HTTP methods are `GET` and `OPTIONS`, the latter is used only for CORS support.

### API Documentation
mtango-py server uses two APIs:
* mTango rc3 API
* internal system API

#### mTango API rc3
The documentation for `rc3` API can be found [-> here <-](http://tango-rest-api.readthedocs.io/en/rc3/).

##### Differences between original and Python implementation
mtango-py supports only reading data from Tango. That means that only `GET` and `OPTIONS` HTTP methods are implemented.  
For all endpoints and methods described in the API documentation but not implemented in mtango-py the server will return HTTP `501 Not Implemented` response.  
There is no support for authorization in the current version, all auth details provided will just be ignored.  
The `TANGO_HOST` part of the URL is only for the compability, regardless of the values passed there, the server will always use system-wide `TANGO_HOST` for database connection.  
Currently, there is no support for filters and ranges.  
There is also no support for events.  
Also, the HTTP status code returned by the server is always `200 OK` in case of successful request. HTTP errors are handled properly, but Tango errors also return `200 OK`. The general rule of thumb for the current version is that if you get `200 OK` then you should receive a proper JSON response, regardless if it contains the actual result or error description.  
There are also differences caused by using "implementation mode", you can read more in the [Configuration](#configuration) section.

If your client uses any of features described here, you  may want to implement the detection of which server implementation is used. For this, mtango-py adds a custom HTTP header: `x-mtango: mtango-py <version>`.


#### System API
System API is used to gather statistics about running server instance, as well as to schedule garbage collection.  
This description uses `<base>` as the application base address, which is usually `http://<server>:<port>/tango/rest`.

Available endpoints:
* `<base>/sys` _API entry point, links to other functions_
  ```
  {
    "version": "mtango-py 0.0.4-testing",
    "config": "http://localhost:8000/tango/rest/sys/config",
    "active": [
      "http://localhost:8000/tango/rest/sys/active/devices",
      "http://localhost:8000/tango/rest/sys/active/attributes"
    ],
    "stats": "http://localhost:8000/tango/rest/sys/stats",
    "gc": [
      "http://localhost:8000/tango/rest/sys/clean/devices",
      "http://localhost:8000/tango/rest/sys/clean/attributes"
    ]
  }
  ```
* `<base>/sys/config` _Lists server configuration_
  ```
  {
    "version": "0.0.4-testing",
    "app_base": "/tango/rest",
    "debug": true,
    "port": 8000,
    "host": "0.0.0.0",
    "TANGO_HOST": "10.81.0.101:10000",
    "rc3_mode": "strict",
    "workers": 4
  }
  ```
* `<base>/sys/cache/devices` _DeviceProxies cache info_
  ```
  {
    "currsize": 6,
    "maxsize": 64,
    "misses": 6,
    "hits": 2
  }
  ```
* `<base>/sys/cache/attributes` _AttributeProxies cache info_
  ```
  {
    "currsize": 1,
    "maxsize": 64,
    "misses": 1,
    "hits": 0
  }
  ```
* `<base>/sys/stats` _Server process statistics_
  ```
  {
    "responses": 8,
    "running_since": 1501580659.3465743,
    "time": 1501581691.0546196,
    "resource": {
      "context_switch": {
        "voluntary": 1166,
        "involuntary": 25
      },
      "system_time": 0.024,
      "shared_mem": 0,
      "unshared_stack_mem": 0,
      "page_faults": {
        "minor": 1925,
        "major": 27
      },
      "recv_msgs": 0,
      "max_resident_mem": 46872,
      "sent_msgs": 0,
      "swap_out": 0,
      "user_time": 0.352,
      "signals": 0,
      "block": {
        "output": 0,
        "input": 4488
      },
      "unshared_mem": 0
    },
    "requests": 9,
    "proxies": {
      "device": 2,
      "attribute": 2
    }
  }
  ```
* `<base>/sys/clean/devices` _Invalidate DeviceProxy cache_  
  This function does not return any content, only a `204 No Content` HTTP response.
* `<base>/sys/clean/attributes` _Invalidate AttributeProxy cache_  
  This function does not return any content, only a `204 No Content` HTTP response.

> **IMPORTANT NOTE !**
> Functions related to process statistics and proxy caches (`sys/stats`, `sys/cache/*` and `sys/clean/*`) 
> have known problems when using more than 1 worker process. Data returned and actions performed are tied
> to worker process that happens to handle your request.
> This is considered a work in progress feature.

### Swagger
The application provides three Swagger description files:
* `/swagger/main.yml` - description of application entry point
* `/swagger/rc3.yml` - mTango rc3 API
* `/swagger/sys.yml` - mtango-py system API

Keep in mind, that if you change `app_base` in the configuration, you should also change `basePath`s in Swagger files for them to work.

## Configuration
The configuration is stored in `conf.py` file in the repository main directory.  
The available options are:
* `app_base` - defines base URL for the application (default: `/tango/rest`)
* `version` - the object describing the server version; you shouldn't really change this
* `workers` - number of Sanic worker processes
* `debug` - Sanic's debug mode
* `host` - server host name or IP address
* `port` - server port
* `rc3_mode` - can be one of two:
	* `strict` - responses are returned exactly as described in the API documentation
	* `implementation` - mimics the behaviour of the original mTango implementation  
	In current version, this option affects only the attribute properties call.  
    In `strict` mode these are returned as an object, with keys being properties names, and values - property values.  
    In `implementation` mode these are returned as list of objects containing `name` and `_empty` attributes.

## Requirements
* Python 3.5
* PyTango 9.2
* sanic
* sanic-cors

## Running
The fastest and easiest way to get started with mtango-py is using `conda`.

1. Download and install `miniconda` (https://conda.io/miniconda.html).
2. Enable conda environment by running `. $CONDA_ROOT/bin/activate`.
3. Create environment with Python 3.5: `conda create -n mtango-py python=3.5`
4. Activate your new environment: `. activate mtango-py`
5. Install PyTango with all dependencies: `conda install -c tango-controls pytango`
6. Install Sanic: `pip install sanic sanic-cors`

To start the server run `python main.py` in the main directory.

## Testing

### Requirements

Tests require `pytest` and `pytest-xdist` packages.  
For all tests to pass you have to have several things configured in Tango database:
* `TangoTest` device named `sys/tg_test/1`
* `double_scalar` attribute is polled
* `State` command is polled
* `abs_change` property is set for `double_scalar` attribute
* Tango 9 (for pipes)
* `string_long_short_ro` pipe should be defined

Most of these things are automatically defined by default `TangoTest` instance.  
You should populate `tests/testconf.py` file with the `TANGO_HOST` that your system is using (this is not really important for current version of the project).

### Running tests
To run tests use `pytest` command with `--boxed` option. This ensures that each test is executed in separate environment, and allows each test to use `uvloop` instead of standard `asyncio` event loop with Tango.  
```
$ pytest --boxed
====== test session starts ======
platform linux -- Python 3.5.3, pytest-3.1.3, py-1.4.34, pluggy-0.4.0
rootdir: /home/daneos/src/maxiv/mtango-py, inifile:
plugins: xdist-1.18.2
collected 34 items 

tests/test_main.py .
tests/test_rc3.py ........................
tests/test_sys.py .........

====== 34 passed in 5.44 seconds ======
```

## End notes
This project is distributed under GNU GPL 3.0 license. Full text of the license can be found in `LICENSE` file in the repository main directory.

Application server was tested only on GNU/Linux operating system, but should work also under other OSes.

The original mTango project can be found [-> here <-](https://github.com/tango-controls/rest-api).