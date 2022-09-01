import boto3
def lambda_handler(event, context):
  client = boto3.client('lambda')
  response = client.get_function(FunctionName="arn:aws:lambda:ap-southeast-1:051751498533:function:cat-service")
  
  return response
