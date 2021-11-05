import boto3


ec2 = boto3.resource('ec2')
client = boto3.client('ec2')


def get_instances(key="User", value="gpu_controller"):
    custom_filter = [{
        'Name': f'tag:{key}',
        'Values': [value]
    }]
    response = client.describe_instances(Filters=custom_filter)
    return response


def get_instance_info(response):
    """Gets the ids of isntances provided by the response
    in get_instances from boto3 ec2.

    Args:
        response ([obj]): Response from get_instances.

    Returns:
        [dict]: Object containing instance_id: state and ip.
    """
    instances = {}
    for instance in response['Reservations']:
        instance_id = instance['Instances'][0]['InstanceId']
        instance_state = instance['Instances'][0]['State']['Name']
        instace_ip = instance['Instances'][0]['PublicIpAddress']
        instances[instance_id] = {'state': instance_state, 'ip': instace_ip}

    return instances


def fetch_instance_data():
    """Wrapper function"""
    response = get_instances()
    instance_data = get_instance_info(response)
    return instance_data


def updateInstaceState(ec2_id):
    """Creates instance connection and will update
    the state depending on the existing state.

    Args:
        ec2_id (str): ec2 instance id.
    """
    instance = ec2.Instance(id=ec2_id)
    status = instance.state['Name']
    print(status)

    if status == "running":
        instance.stop()
    elif status == "stopping":
        pass
    elif status == "stopped":
        instance.start()
    elif status == "starting":
        pass

    return status


if __name__ == '__main__':
    print(fetch_instance_data())
