# ncdu-s3
This tool generates [ncdu](http://dev.yorhel.nl/ncdu) formatted JSON data file for S3 buckets

![Screenshot](screenshots.gif)

# Usage
```bash
$ (cd ncdu-s3; sudo pip install .)
$ ncdu-s3 s3://my-bucket my-bucket.json
$ ncdu -f my-bucket.json
```

If you using an S3 compatible storage, you can set the endpoint URL and profile name as environment variables.
```bash
$ export AWS_ENDPOINT_URL=https://s3.example.com # Optional
$ export AWS_PROFILE=my-profile # Optional
$ ncdu-s3 s3://my-bucket my-bucket.json
```

Please note you need boto configured for your user before using this tool.  
See how to configure boto [here](http://boto3.readthedocs.org/en/latest/guide/configuration.html)
