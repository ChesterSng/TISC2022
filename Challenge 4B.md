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




