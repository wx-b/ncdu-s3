import boto3
import re
import os
from configparser import ConfigParser

class xboto3:
    # this is an ugly hack to bypass the fact boto3 does not read all info
    # in .aws/config, notably OVH specific options, endpoint_url
    """This class is a replacement of boto3 library. It should be used like this:
    instead of:
    
    boto3.resource('s3') -> xboto3().resource('s3')

    boto3.client('s3') -> xboto3().client('s3')

    The constructor (xboto3()) accept a profile_name argument.

    """

    BOTO3_CONFIG_REGEXP = re.compile('(\S+) = (".*?"|\S+)')
    BOTO3_ACCEPTED_OPTIONS = ['endpoint_url']
    
    def __init__(self, profile_name='default'):
        """Retrieves boto3.resource, and fills in any service-specific 
        (filtered by BOTO3_ACCEPTED_OPTIONS, as some options are not used)    
        parameters from your config, which can be specified either        
        in AWS_CONFIG_FILE or ~/.aws/config (default). Similarly,         
        profile_name is 'default' (default) unless AWS_PROFILE is set.    
                                                                        
        Assumes that additional service-specific config is specified as:  
                                                                        
        [profile_name]                                                    
        service-name =                                                    
            parameter-name = parameter-value                              
        another-service-name =                                            
            ... etc                                                       
        
        adapted from: https://github.com/aws/aws-cli/issues/1270
        thanks to https://github.com/jaklinger
        """
        # Get the AWS config file path                                    
        self.profile_name = os.environ.get('AWS_PROFILE', profile_name)
        self.conf_filepath = os.environ.get('AWS_CONFIG_FILE', '~/.aws/config')
        self.aws_endpoint_url = os.environ.get("AWS_ENDPOINT_URL")
        self.conf_filepath = os.path.expanduser(self.conf_filepath)
        
        self.service_cfg = {}
        
        if self.aws_endpoint_url:
            # Use environment variable if available
            self.service_cfg['endpoint_url']=self.aws_endpoint_url

    def __get_config__(self, service_name):
        config = dict(self.service_cfg)
        if os.path.exists(self.conf_filepath):
            parser = ConfigParser()
            with open(self.conf_filepath) as f:
                parser.read_file(f)
            cfg = dict(parser).get(f'profile {self.profile_name}', {})
            # Extract the service-specific config, if any                     
            service_raw_cfg = cfg.get(service_name, '')
            config.update({k: v for k, v in self.BOTO3_CONFIG_REGEXP.findall(service_raw_cfg)
                if k in self.BOTO3_ACCEPTED_OPTIONS})
        return config
        
    def resource(self, service_name, **kwargs):
        # Load in the service config, on top of other defaults            
        # and let boto3 do the rest                                       
        return boto3.resource(service_name=service_name,
                                **self.__get_config__(service_name), **kwargs)
    

    def client(self, service_name, **kwargs):
        # Load in the service config, on top of other defaults            
        # and let boto3 do the rest                                       
        return boto3.Session().client(
            service_name=service_name, **self.__get_config__(service_name), **kwargs
        )

def client(service_name, **kwargs):
    return xboto3().client(service_name=service_name, **kwargs)

def resource(service_name, **kwargs):
    return xboto3().resource(service_name=service_name, **kwargs)