from werkzeug.exceptions import HTTPException


class NotFound(HTTPException):
    """Data not found"""

    code = 404
    description = "Not found"


class InvalidException(HTTPException):
    """Custom base exception"""

    code = 400
    description = "Invalid request"


class InvalidJson(InvalidException):
    """Cat't parse json from requests"""

    description = "Invalid json request"


class InvalidId(InvalidException):
    """Invalid id"""

    description = "Invalid ID"
