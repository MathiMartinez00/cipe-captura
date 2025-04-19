import requests
import os
import json

def get_json_response(response):
    return {
        'isBase64Encoded': False,
        'statusCode': response.status_code,
        'headers': { 
            'Content-Type': 'application/json',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
        },
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

    if event['resource'] == '/users/token':
        response = requests.post(f'{os.environ.get('REST_DOMAIN')}/api/users/token/', headers=event['headers'], data=event['body'])
        return get_json_response(response)

    if event['resource'] == '/complaints':
        if event['httpMethod'] == 'GET':
            response = requests.get(f'{os.environ.get('REST_DOMAIN')}/api/complaints/', headers=event['headers'], params=event['queryStringParameters'])
            return get_json_response(response)
        elif event['httpMethod'] == 'POST':
            response = requests.post(f'{os.environ.get('REST_DOMAIN')}/api/complaints/', headers=event['headers'], data=event['body'])
            return get_json_response(response)

    if event['resource'] == '/complaint-votes':
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

    if event['resource'] == '/reports/complaints-per-city':
        format = 'csv'
        if event['queryStringParameters']:
            format = event['queryStringParameters'].get('report-format')

        response = requests.get(f'{os.environ.get('REST_DOMAIN')}/api/reports/complaints-per-city/', headers=event['headers'], params=event['queryStringParameters'])

        if format == 'csv':
            return {
                'isBase64Encoded': False,
                'statusCode': response.status_code,
                'headers': { 
                    'Content-Type': 'text/csv', 
                    "Content-Disposition": 'attachment; filename="complaints_per_complaint_type.csv"',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
                },
                'body': response.text
            }
        else:
            return get_json_response(response)
        
    if event['resource'] == '/reports/complaints-per-complaint-type':
        format = 'csv'
        if event['queryStringParameters']:
            format = event['queryStringParameters'].get('report-format')

        response = requests.get(f'{os.environ.get('REST_DOMAIN')}/api/reports/complaints-per-complaint-type/', headers=event['headers'], params=event['queryStringParameters'])

        if format == 'csv':
            return {
                'isBase64Encoded': False,
                'statusCode': response.status_code,
                'headers': { 
                    'Content-Type': 'text/csv', 
                    "Content-Disposition": 'attachment; filename="complaints_per_complaint_type.csv"',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
                },
                'body': response.text
            }
        else:
            return get_json_response(response)

    if event['resource'] == '/complaint-types':
        response = requests.get(f'{os.environ.get('REST_DOMAIN')}/api/complaint-types/', headers=event['headers'], params=event['queryStringParameters'])
        return get_json_response(response)
    
    if event['resource'] == '/cities':
        response = requests.get(f'{os.environ.get('REST_DOMAIN')}/api/cities/', headers=event['headers'], params=event['queryStringParameters'])
        return get_json_response(response)

    return {
        'isBase64Encoded': False,
        'statusCode': 404,
        'headers': { 
            'Content-Type': 'application/json',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
        },
        'body': json.dumps({'error': 'Not Found'})
    }