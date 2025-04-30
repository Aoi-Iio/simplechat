import json
import os
import re
import requests  # 外部APIに接続するため追加

FASTAPI_URL = os.environ.get("FASTAPI_URL", "https://5438-35-233-241-194.ngrok-free.app/predict")

def lambda_handler(event, context):
    try:
        print("Received event:", json.dumps(event))
        
        # Cognitoで認証されたユーザー情報を取得（任意）
        user_info = None
        if 'requestContext' in event and 'authorizer' in event['requestContext']:
            user_info = event['requestContext']['authorizer']['claims']
            print(f"Authenticated user: {user_info.get('email') or user_info.get('cognito:username')}")
        
        # リクエストボディの解析
        body = json.loads(event['body'])
        message = body['message']
        
        print("Sending message to FastAPI:", message)
        
        # FastAPI にリクエストを送信
        response = requests.post(
            FASTAPI_URL,
            headers={"Content-Type": "application/json"},
            json={"message": message}
        )

        if response.status_code != 200:
            raise Exception(f"FastAPI error: {response.status_code} - {response.text}")
        
        response_json = response.json()
        assistant_response = response_json.get("response")
        
        if not assistant_response:
            raise Exception("No response from FastAPI")
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": True,
                "response": assistant_response
            })
        }

    except Exception as error:
        print("Error:", str(error))

        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": False,
                "error": str(error)
            })
        }
