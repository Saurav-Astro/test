import pymongo
import sys

uri = "mongodb+srv://manya_anand:MANYA%402609!@cluster0.napq8lk.mongodb.net/proxm?retryWrites=true&w=majority"
try:
    print(f"Connecting to: {uri}")
    client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=5000)
    # The ismaster command is cheap and does not require auth.
    client.admin.command('ismaster')
    print("✅ Successfully connected to MongoDB Atlas!")
except Exception as e:
    print(f"❌ Connection failed: {e}")
    
    print("\nTrying with tlsAllowInvalidCertificates=true...")
    try:
        uri_alt = uri + "&tlsAllowInvalidCertificates=true"
        client = pymongo.MongoClient(uri_alt, serverSelectionTimeoutMS=5000)
        client.admin.command('ismaster')
        print("✅ Success with tlsAllowInvalidCertificates!")
    except Exception as e2:
        print(f"❌ Still failed: {e2}")
