import boto3

def lambda_handler(event, context):
    
    # Work in Progress: Requires help from Agents! 
    
    ec2 = boto3.client('ec2')

    instances = ec2.create_instances(
        ImageId="ami-0b89f7b3f054b957e",
        MinCount=1,
        MaxCount=1,
        InstanceType="t2.micro",
        SubnetId="subnet-0aa6ecdf900166741",
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags' : [
                    {
                        'Key': 'agent',
                        'Value': 'user-2a65a6a30db74590a4f6c8362ed03635'
                    }
                ]
            }
        ]
    )
    
    return {
        'status': 200,
        'results': 'This is work in progress. Agents, palindrome needs your help to complete the workflow! :3',
        'output': instances
    }
  