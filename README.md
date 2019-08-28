###AWS Lambda - Export CloudWatch Logs to S3 Bucket

Está função tem como objetivo reter os logs no S3 com o tempo maior que 30 dias.

No bucket será configurado uma política de expurgo, 90 dias no glacier após 365 excluir.

##### Parâmetros
    bucket_name: export-watchlogs-to-s3
    Days: 30

##### S3 Bucket Policy

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
