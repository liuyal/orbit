# models/project.py

### GET /api/projects responses

RESPONSE_500 = {
    "description": "Internal Server Error",
    "content":
        {
            "application/json": {
                "example":
                    {"detail": "Internal Server Error"}
            }
        }
}
