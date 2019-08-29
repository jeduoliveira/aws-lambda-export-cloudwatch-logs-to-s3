# AWS Lambda - Export CloudWatch Logs to S3 Bucket

The purpose of this function is to retain all cloudWatch logs older than 30 days in bucket s3.

It'll configure a delete policy, 90 days copy to glacier, after 365 day remove forever.

A deletion policy must be set on s3, after 365 days it should be removed forever.

## Parâmetros
    bucket_name: export-watchlogs-to-s3
    Days: 30

## S3 Bucket Policy

    {
        "Version": "2012-10-17",
        "Id": "Policy1565727952277",
        "Statement": [
            {
                "Sid": "Stmt1565727950371",
                "Effect": "Allow",
                "Principal": {
                    "Service": "logs.us-east-1.amazonaws.com"
                },
                "Action": "s3:GetBucketAcl",
                "Resource": "arn:aws:s3:::export-watchlogs-to-s3"
            },
            {
                "Sid": "Stmt1565727950370",
                "Effect": "Allow",
                "Principal": {
                    "Service": "logs.us-east-1.amazonaws.com"
                },
                "Action": "s3:PutObject",
                "Resource": "arn:aws:s3:::export-watchlogs-to-s3/*"
            }
        ]
    }
