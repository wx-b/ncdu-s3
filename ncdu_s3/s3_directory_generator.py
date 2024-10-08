import urllib.parse
from . import myboto3 as boto3

class S3DirectoryGenerator(object):
    def __init__(self, s3_url):
        parsed_s3_url = urllib.parse.urlparse(s3_url)
        if parsed_s3_url.scheme != 's3':
            raise SyntaxError('Invalid S3 scheme')

        self.bucket_name = parsed_s3_url.netloc
        self.bucket_path = parsed_s3_url.path[1:] if parsed_s3_url.path.startswith('/') else parsed_s3_url.path
        bucket_path_split = self.bucket_path.split('/')

        try:
            client = boto3.client('s3')
            region = client.get_bucket_location(Bucket=self.bucket_name)['LocationConstraint']
        except:
            region=None

        s3_connection = boto3.resource('s3', region_name=region)
        self.bucket = s3_connection.Bucket(self.bucket_name)

        if bucket_path_split[-1] == '':
            # directory listing
            self.strip_length = len(self.bucket_path)
        else:
            # prefix listing
            self.strip_length = len('/'.join(bucket_path_split[:-1]))

    def __iter__(self):
        return self.generator()

    def generator(self):
        for o in self.bucket.objects.filter(Prefix=self.bucket_path):
            key = o.key[self.strip_length:]

            # S3 doesn't really have a concept of dirs. The convention is '/' is path separator, we do the same
            path = key.split('/')

            if path[0] == '' and not self.bucket_path.endswith('/'):
                # we assume the S3 prefix is a directory that wasn't terminated with a '/'
                path.pop(0)

            yield (path, o.size, o.last_modified)
