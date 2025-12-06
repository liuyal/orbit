# models/project.py

from .generic import RESPONSE_500

GET_RESPONSES = {
    404: {
        "description": "Not found",
        "content":
            {
                "application/json": {
                    "example":
                        {"detail": "Project not found"}
                }
            }
    },
    500: RESPONSE_500
}

POST_RESPONSES = {
    401: {
        "description": "Invalid Parameters",
        "content":
            {
                "application/json": {
                    "example":
                        {"detail": "Invalid Parameters"}
                }
            }
    },
    500: RESPONSE_500
}

PUT_RESPONSES = {
    401: {
        "description": "Invalid Parameters",
        "content":
            {
                "application/json": {
                    "example":
                        {"detail": "Invalid Parameters"}
                }
            }
    },
    500: RESPONSE_500
}

DELETE_RESPONSES = {
    204: {
        "description": "Successful Response"},
    401: {
        "description": "Invalid Parameters",
        "content":
            {
                "application/json": {
                    "example":
                        {"detail": "Invalid Parameters"}
                }
            }
    },
    500: RESPONSE_500
}
