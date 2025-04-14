import requests
import os
import json

def get_json_response(response):
    return {
        'isBase64Encoded': False,
        'statusCode': response.status_code,
        'headers': { 'Content-Type': 'application/json' },
        'body': response.text
    }

def get_raw_response(response):
    return {
        'isBase64Encoded': False,
        'statusCode': response.status_code,
        'headers': { 'Content-Type': 'application/json' },
        'body': response.text
    }

def lambda_handler(event, context):

    if event['requestContext']['path'] == '/users/token':
        response = requests.post(f'{os.environ.get('REST_DOMAIN')}/api/users/token/', headers=event['headers'], data=event['body'])
        return get_json_response(response)

    if event['requestContext']['path'] == '/complaints':
        if event['httpMethod'] == 'GET':
            response = requests.get(f'{os.environ.get('REST_DOMAIN')}/api/complaints/', headers={
                'Authorization': event['headers']['Authorization']
            })
            if event['queryStringParameters'] is None:
                return get_raw_response(response)

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
        elif event['httpMethod'] == 'POST':
            response = requests.post(f'{os.environ.get('REST_DOMAIN')}/api/complaints/', headers=event['headers'], data=event['body'])
            return get_json_response(response)

    if event['requestContext']['path'] == '/complaint-votes':
        if event['httpMethod'] == 'GET':
            response = requests.get(f'{os.environ.get('REST_DOMAIN')}/api/complaint-votes/', headers=event['headers'])
            return get_json_response(response)
        elif event['httpMethod'] == 'POST':
            response = requests.post(f'{os.environ.get('REST_DOMAIN')}/api/complaint-votes/', headers=event['headers'], data=event['body'])
            return get_json_response(response)
        else:
            return {
                'isBase64Encoded': False,
                'statusCode': 405,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Method not supported'})
            }

    if event['requestContext']['path'] == '/reports/complaints-per-city':
        format = 'csv'
        if event['queryStringParameters']:
            format = event['queryStringParameters'].get('report-format')

        response = requests.get(f'{os.environ.get('REST_DOMAIN')}/api/reports/complaints-per-city/', headers={
            'Authorization': event['headers']['Authorization']
        }, params=event['queryStringParameters'])

        if format == 'csv':
            return {
                'isBase64Encoded': False,
                'statusCode': response.status_code,
                'headers': { 'Content-Type': 'text/csv', "Content-Disposition": 'attachment; filename="complaints_per_complaint_type.csv"'},
                'body': response.text
            }
        else:
            return {
                'isBase64Encoded': False,
                'statusCode': response.status_code,
                'headers': { 'Content-Type': 'application/json' },
                'body': json.dumps(response.json())
            }
        
    if event['requestContext']['path'] == '/complaint-types':
        response = requests.get(f'{os.environ.get('REST_DOMAIN')}/api/complaint-types/', headers=event['headers'], params=event['queryStringParameters'])
        return get_json_response(response)
    
    if event['requestContext']['path'] == '/cities':
        response = requests.get(f'{os.environ.get('REST_DOMAIN')}/api/cities/', headers=event['headers'], params=event['queryStringParameters'])
        return get_json_response(response)

    return {
        'isBase64Encoded': False,
        'statusCode': 404,
        'headers': { 'Content-Type': 'application/json' },
        'body': json.dumps({'error': 'Not Found'})
    }