import json
def lambda_handler(event, context):
    return {
        "statusCode": 200,
        "body": json.dumps({"ok": True, "message": "romanian-public-comp-etl lambda skeleton"})
    }