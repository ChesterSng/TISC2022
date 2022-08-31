## CloudyNekos
Start [here](https://d20whnyjsgpc34.cloudfront.net/).
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

`aws s3 ls s3://palindromecloudnekos`
```
chester@Macintosh TISC2022 % aws s3 ls s3://palindromecloudynekos
                           PRE api/
                           PRE img/
2022-08-23 21:16:20         34 error.html
2022-08-23 21:16:20       2257 index.html
```

`aws s3 ls s3://palindromecloudnekos --recursive`
```
chester@Macintosh TISC2022 % aws s3 ls s3://palindromecloudynekos --recursive
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

```
# Neko Access System Invocation Notes

Invoke with the passcode in the header "x-cat-header". The passcode is found on the cloudfront site, all lower caps and separated using underscore.

https://b40yqpyjb3.execute-api.ap-southeast-1.amazonaws.com/prod/agent

All EC2 computing instances should be tagged with the key: 'agent' and the value set to your username. Otherwise, the antivirus cleaner will wipe out the resources.
```

![Challenge4_1](Challenge4_1.png)

```
{"Message": "Welcome there agent! Use the credentials wisely! It should be live for the next 120 minutes! Our antivirus will wipe them out and the associated resources after the expected time usage.", "Access_Key": "AKIAQYDFBGMSV3WJSARP", "Secret_Key": "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"}
```

I tried to list all the resources I can find inside `aws ec2`. It seems like we cannot `describe-instances` (list ec2 instances), `describe-volumes` (list volumes), but we can `describe-subnets` (list subnets available).

The subnet below has the name `palindrome`, looks like a good lead. Maybe we need to spawn an ec2 instance, join this subnet and then scan the network?
```
chester@Macintosh TISC2022 % aws ec2 describe-subnets
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
chester@Macintosh TISC2022 % aws ec2 run-instances --instance-type t2.nano --image-id ami-0b89f7b3f054b957e --subnet-id subnet-0aa6ecdf900166741

An error occurred (VcpuLimitExceeded) when calling the RunInstances operation: You have requested more vCPU capacity than your current vCPU limit of 32 allows for the instance bucket that the specified instance type belongs to. Please visit http://aws.amazon.com/contact-us/ec2-request to request an adjustment to this limit.
```

Seems like the number of vCPUs is maxed. The way forward shouldn't be to spawn an ec2 instance...

```
chester@Macintosh TISC2022 % aws ec2 describe-security-groups
{
    "SecurityGroups": [
        {
            "Description": "Access to c2 infra",
            "GroupName": "default-agents-sg",
            "IpPermissions": [
                {
                    "FromPort": 0,
                    "IpProtocol": "tcp",
                    "IpRanges": [
                        {
                            "CidrIp": "0.0.0.0/0"
                        }
                    ],
                    "Ipv6Ranges": [],
                    "PrefixListIds": [],
                    "ToPort": 65535,
                    "UserIdGroupPairs": []
                }
            ],
            "OwnerId": "051751498533",
            "GroupId": "sg-047c958320ee832f0",
            "IpPermissionsEgress": [
                {
                    "IpProtocol": "-1",
                    "IpRanges": [
                        {
                            "CidrIp": "0.0.0.0/0"
                        }
                    ],
                    "Ipv6Ranges": [],
                    "PrefixListIds": [],
                    "UserIdGroupPairs": []
                }
            ],
            "VpcId": "vpc-095cd9241e386169d"
        },
        {
            "Description": "default VPC security group",
            "GroupName": "default",
            "IpPermissions": [
                {
                    "IpProtocol": "-1",
                    "IpRanges": [],
                    "Ipv6Ranges": [],
                    "PrefixListIds": [],
                    "UserIdGroupPairs": [
                        {
                            "GroupId": "sg-0521a956628208ccc",
                            "UserId": "051751498533"
                        }
                    ]
                }
            ],
            "OwnerId": "051751498533",
            "GroupId": "sg-0521a956628208ccc",
            "IpPermissionsEgress": [
                {
                    "IpProtocol": "-1",
                    "IpRanges": [
                        {
                            "CidrIp": "0.0.0.0/0"
                        }
                    ],
                    "Ipv6Ranges": [],
                    "PrefixListIds": [],
                    "UserIdGroupPairs": []
                }
            ],
            "VpcId": "vpc-095cd9241e386169d"
        }
    ]
}
```

Used [IAM-Flaws](https://github.com/nikhil1232/IAM-Flaws) to enumerate permissions.

```
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

`aws iam list-roles`

```
{
    "Roles": [
        {
            "Path": "/service-role/",
            "RoleName": "AWSBackupDefaultServiceRole",
            "RoleId": "AROAQYDFBGMSZL3H3GO7H",
            "Arn": "arn:aws:iam::051751498533:role/service-role/AWSBackupDefaultServiceRole",
            "CreateDate": "2022-04-04T08:49:38Z",
            "AssumeRolePolicyDocument": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "backup.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            },
            "Description": "Provides AWS Backup permission to create backups and perform restores on your behalf across AWS services",
            "MaxSessionDuration": 3600
        },
        {
            "Path": "/aws-service-role/ecs.application-autoscaling.amazonaws.com/",
            "RoleName": "AWSServiceRoleForApplicationAutoScaling_ECSService",
            "RoleId": "AROAQYDFBGMSYWTC7NWT2",
            "Arn": "arn:aws:iam::051751498533:role/aws-service-role/ecs.application-autoscaling.amazonaws.com/AWSServiceRoleForApplicationAutoScaling_ECSService",
            "CreateDate": "2022-04-05T08:40:04Z",
            "AssumeRolePolicyDocument": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "ecs.application-autoscaling.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            },
            "MaxSessionDuration": 3600
        },
        {
            "Path": "/aws-service-role/autoscaling.amazonaws.com/",
            "RoleName": "AWSServiceRoleForAutoScaling",
            "RoleId": "AROAQYDFBGMS4MP6LHPP5",
            "Arn": "arn:aws:iam::051751498533:role/aws-service-role/autoscaling.amazonaws.com/AWSServiceRoleForAutoScaling",
            "CreateDate": "2022-01-26T05:28:49Z",
            "AssumeRolePolicyDocument": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "autoscaling.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            },
            "Description": "Default Service-Linked Role enables access to AWS Services and Resources used or managed by Auto Scaling",
            "MaxSessionDuration": 3600
        },
        {
            "Path": "/aws-service-role/backup.amazonaws.com/",
            "RoleName": "AWSServiceRoleForBackup",
            "RoleId": "AROAQYDFBGMSVCRSJJY6H",
            "Arn": "arn:aws:iam::051751498533:role/aws-service-role/backup.amazonaws.com/AWSServiceRoleForBackup",
            "CreateDate": "2022-04-04T08:48:50Z",
            "AssumeRolePolicyDocument": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "backup.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            },
            "MaxSessionDuration": 3600
        },
        {
            "Path": "/aws-service-role/ecs.amazonaws.com/",
            "RoleName": "AWSServiceRoleForECS",
            "RoleId": "AROAQYDFBGMSVMLCEWBCF",
            "Arn": "arn:aws:iam::051751498533:role/aws-service-role/ecs.amazonaws.com/AWSServiceRoleForECS",
            "CreateDate": "2022-03-23T19:19:11Z",
            "AssumeRolePolicyDocument": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "ecs.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            },
            "Description": "Role to enable Amazon ECS to manage your cluster.",
            "MaxSessionDuration": 3600
        },
        {
            "Path": "/aws-service-role/elasticache.amazonaws.com/",
            "RoleName": "AWSServiceRoleForElastiCache",
            "RoleId": "AROAQYDFBGMSSZ2SIGYG2",
            "Arn": "arn:aws:iam::051751498533:role/aws-service-role/elasticache.amazonaws.com/AWSServiceRoleForElastiCache",
            "CreateDate": "2022-03-27T07:43:15Z",
            "AssumeRolePolicyDocument": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "elasticache.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            },
            "Description": "This policy allows ElastiCache to manage AWS resources on your behalf as necessary for managing your cache.",
            "MaxSessionDuration": 3600
        },
        {
            "Path": "/aws-service-role/elasticloadbalancing.amazonaws.com/",
            "RoleName": "AWSServiceRoleForElasticLoadBalancing",
            "RoleId": "AROAQYDFBGMS7NWSKKIXS",
            "Arn": "arn:aws:iam::051751498533:role/aws-service-role/elasticloadbalancing.amazonaws.com/AWSServiceRoleForElasticLoadBalancing",
            "CreateDate": "2022-01-26T06:38:44Z",
            "AssumeRolePolicyDocument": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "elasticloadbalancing.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            },
            "Description": "Allows ELB to call AWS services on your behalf.",
            "MaxSessionDuration": 3600
        },
        {
            "Path": "/aws-service-role/globalaccelerator.amazonaws.com/",
            "RoleName": "AWSServiceRoleForGlobalAccelerator",
            "RoleId": "AROAQYDFBGMS22KZIJ7RV",
            "Arn": "arn:aws:iam::051751498533:role/aws-service-role/globalaccelerator.amazonaws.com/AWSServiceRoleForGlobalAccelerator",
            "CreateDate": "2022-03-27T09:20:41Z",
            "AssumeRolePolicyDocument": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "globalaccelerator.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            },
            "Description": "Allows Global Accelerator to call AWS services on customer's behalf",
            "MaxSessionDuration": 3600
        },
        {
            "Path": "/aws-service-role/rds.amazonaws.com/",
            "RoleName": "AWSServiceRoleForRDS",
            "RoleId": "AROAQYDFBGMSQUMKE56M3",
            "Arn": "arn:aws:iam::051751498533:role/aws-service-role/rds.amazonaws.com/AWSServiceRoleForRDS",
            "CreateDate": "2022-02-01T18:29:33Z",
            "AssumeRolePolicyDocument": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "rds.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            },
            "Description": "Allows Amazon RDS to manage AWS resources on your behalf",
            "MaxSessionDuration": 3600
        },
        {
            "Path": "/aws-service-role/support.amazonaws.com/",
            "RoleName": "AWSServiceRoleForSupport",
            "RoleId": "AROAQYDFBGMSR5TXKZZ6B",
            "Arn": "arn:aws:iam::051751498533:role/aws-service-role/support.amazonaws.com/AWSServiceRoleForSupport",
            "CreateDate": "2022-01-26T04:43:09Z",
            "AssumeRolePolicyDocument": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "support.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            },
            "Description": "Enables resource access for AWS to provide billing, administrative and support services",
            "MaxSessionDuration": 3600
        },
        {
            "Path": "/aws-service-role/trustedadvisor.amazonaws.com/",
            "RoleName": "AWSServiceRoleForTrustedAdvisor",
            "RoleId": "AROAQYDFBGMSS5GZWA7HZ",
            "Arn": "arn:aws:iam::051751498533:role/aws-service-role/trustedadvisor.amazonaws.com/AWSServiceRoleForTrustedAdvisor",
            "CreateDate": "2022-01-26T04:43:09Z",
            "AssumeRolePolicyDocument": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": "trustedadvisor.amazonaws.com"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ]
            },
            "Description": "Access for the AWS Trusted Advisor Service to help reduce cost, increase performance, and improve security of your AWS environment.",
            "MaxSessionDuration": 3600
        },
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