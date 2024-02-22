import boto3
import os

def lambda_handler(event, context):
    region = os.environ['Region']
    ec2 = boto3.client('ec2', region_name=region)
    cloudwatch = boto3.client('cloudwatch')
    i=os.environ['id']
    reservations = ec2.describe_instances(InstanceIds=[i]).get('Reservations', [])
    instanceid=(reservations[0]['Instances'][0]['InstanceId'])
    Topic=""+os.environ['SNS']+""
    ##GetInstanceName##
    nameList=reservations[0]['Instances'][0]['Tags']
    nameDic=next(item for item in nameList if item['Key'] == 'Name')
    name=nameDic['Value']

    #CPU Alarm#
    
    CPU_Alarm_Name=os.environ['AccountName']+"-"+name+"-"+instanceid+"-CPUUtilization > 90%" 
    cloudwatch.put_metric_alarm(
    AlarmName=CPU_Alarm_Name,
    ComparisonOperator='GreaterThanThreshold',
    EvaluationPeriods=1,
    MetricName='CPUUtilization',
    Namespace='AWS/EC2',
    Period=300,
    Statistic='Maximum',
    Threshold=90.0,
    ActionsEnabled=True,
    AlarmActions=[
        ''+os.environ['SNS']+'',
    ],
    AlarmDescription=CPU_Alarm_Name,
    Dimensions=[
        {
          'Name': 'InstanceId',
          'Value': instanceid
        },
    ],
    Unit='Percent'
    )
    print("Cpu Alarm for "+name+" "+instanceid+" created")
    
    #StatusCheck Alarm#
    
    StatusCheck_Alarm_Name=os.environ['AccountName']+"-"+name+"-"+instanceid+"-StatusCheck Failed" 
    cloudwatch.put_metric_alarm(
    AlarmName=StatusCheck_Alarm_Name,
    ComparisonOperator='GreaterThanThreshold',
    EvaluationPeriods=1,
    MetricName='StatusCheckFailed',
    Namespace='AWS/EC2',
    Period=60,
    Statistic='Average',
    Threshold=0.99,
    ActionsEnabled=True,
    AlarmActions=[
        ''+os.environ['SNS']+'',
    ],
    AlarmDescription=StatusCheck_Alarm_Name,
    Dimensions=[
        {
          'Name': 'InstanceId',
          'Value': instanceid
        },
    ],
    Unit='Count'
    )
    print("StatusCheck Alarm for "+name+" "+instanceid+" created")
    
