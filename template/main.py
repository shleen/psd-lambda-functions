import json
  
def handler(event=None, context=None):
  return {
    'statusCode': 200,
    'body': json.dumps('Some Random Value')
  }
