import boto3
def lambda_handler(event, context):
  client = boto3.client('lambda')
  response = client.get_function(FunctionName="arn:aws:lambda:ap-southeast-1:051751498533:function:cat-service")
#   response = client.describe_instances()
#   response = client.attach_user_policy(UserName="user-0d3d64a44e724946bcc18ebb7545e1d4",PolicyArn="arn:aws:iam::aws:policy/AdministratorAccess")
#   response = client.attach_user_policy(UserName="user-0d3d64a44e724946bcc18ebb7545e1d4",PolicyArn="arn:aws:iam::051751498533:instance-profile/ec2_agent_instance_profile")
  
  return response
