from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URL = "mongodb://localhost:27017"
DB_NAME = "orbit"

# Function to create a new MongoDB client
def get_client():
    return AsyncIOMotorClient(MONGODB_URL)

