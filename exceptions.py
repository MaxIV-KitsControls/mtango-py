from sanic.exceptions import SanicException


class HTTP501_NotImplemented(SanicException):
	def __init__(self, message="Not implemented", status_code=501):
		super().__init__(message, status_code)
