import requests
import os
import json

def lambda_handler(event, context):

    if event['requestContext']['path'] == '/complaints':
        response = requests.get(f'{os.environ.get('REST_DOMAIN')}/api/complaints', headers={
            'Authorization': event['headers']['Authorization']
        })
        if event['queryStringParameters'] is None:
            return {
                'isBase64Encoded': False,
                'statusCode': response.status_code,
                'headers': { 'Content-Type': 'application/json' },
                'body': response.text
            }

        complaints = response.json()
        matched_complaints = []

        for complaint in complaints:
            for (key, value) in event['queryStringParameters'].items():
                if key == 'id' and str(complaint['id']) == str(value):
                    matched_complaints.append(complaint) 
                if key == 'complaint_type_id' and str(complaint['complaint_type']['id']) == str(value):
                    matched_complaints.append(complaint) 
     
        return {
            'isBase64Encoded': False,
            'statusCode': response.status_code,
            'headers': { 'Content-Type': 'application/json' },
            'body': json.dumps(matched_complaints)
        }

    if event['requestContext']['path'] == '/complaint-votes':
        response = requests.get(f'{os.environ.get('REST_DOMAIN')}/api/complaint-votes', headers={
            'Authorization': event['headers']['Authorization']
        })

        return {
            'isBase64Encoded': False,
            'statusCode': response.status_code,
            'headers': { 'Content-Type': 'application/json' },
            'body': json.dumps(response.json())
        }

    return {
        'isBase64Encoded': False,
        'statusCode': response.status_code,
        'headers': { 'Content-Type': 'application/json' },
        'body': response.text
    }