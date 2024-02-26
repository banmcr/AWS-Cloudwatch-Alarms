import boto3
import os

def lambda_handler(event, context):
    region = os.environ['Region']
    ec2 = boto3.client('ec2', region_name=region)
    cloudwatch = boto3.client('cloudwatch')
    i=os.environ['id']
    reservations = ec2.describe_instances(InstanceIds=[i]).get('Reservations', [])
    instanceid=(reservations[0]['Instances'][0]['InstanceId'])
    imgid=(reservations[0]['Instances'][0]['ImageId'])
    InstType=(reservations[0]['Instances'][0]['InstanceType'])
    
    ##GetInstanceName##
    nameList=reservations[0]['Instances'][0]['Tags']
    nameDic=next(item for item in nameList if item['Key'] == 'Name')
    name=nameDic['Value']   
    Topic=""+os.environ['SNS']+""
    
    ############CPU Alarm#############################################
    
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
    
    ######StatusCheck Alarm################################################
    
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
    OsType=(reservations[0]['Instances'][0]['PlatformDetails'])
    print(OsType)
    if OsType=='Windows':
        print("it is windows")
        
        ###############WINDOWS######################C Drive Utilization#########################################
        
        CDiskAlarm_Name=os.environ['AccountName']+"-"+name+"-"+instanceid+"- CDrive Utilization > 90%" 
        cloudwatch.put_metric_alarm(
        AlarmName=CDiskAlarm_Name,
        ComparisonOperator='LessThanOrEqualToThreshold',
        EvaluationPeriods=1,
        MetricName='LogicalDisk % Free Space',
        Namespace='CWAgent',
        Period=300,
        Statistic='Maximum',
        Threshold=10,
        ActionsEnabled=True,
        AlarmActions=[
            ''+os.environ['SNS']+'',
        ],
        AlarmDescription=CDiskAlarm_Name,
        Dimensions=[
            {
                "Name": "instance",
                "Value": "C:"
            },
            {
                "Name": "InstanceId",
                "Value": instanceid
            },
            {
                "Name": "ImageId",
                "Value": imgid
            },
            {
                "Name": "objectname",
                "Value": "LogicalDisk"
            },
            {
                "Name": "InstanceType",
                "Value": InstType
            }
        ]
        )
        print("C Drive alarm for "+name+" "+instanceid+" created")
        
        ##############WINDOWS##########Memory Alarm#################################
        
        MemoryAlarm_Name=os.environ['AccountName']+"-"+name+"-"+instanceid+"- MemoryUtilization > 90%" 
        cloudwatch.put_metric_alarm(
        AlarmName=MemoryAlarm_Name,
        ComparisonOperator='GreaterThanThreshold',
        EvaluationPeriods=1,
        MetricName='Memory % Committed Bytes In Use',
        Namespace='CWAgent',
        Period=300,
        Statistic='Maximum',
        Threshold=90,
        ActionsEnabled=True,
        AlarmActions=[
            ''+os.environ['SNS']+'',
        ],
        AlarmDescription=MemoryAlarm_Name,
        Dimensions=[
            {
                "Name": "InstanceId",
                "Value": instanceid
            },
            {
                "Name": "ImageId",
                "Value": imgid
            },
            {
                "Name": "objectname",
                "Value": "Memory"
            },
            {
                "Name": "InstanceType",
                "Value": InstType
            }
        ]
        )
        print("Memory alarm for "+name+" "+instanceid+" created")
        
        
    elif OsType=='Linux/UNIX' or OsType=='Red Hat Enterprise Linux':
        print("it is linux")
            ##################LINUX########################ROOTDISK################################################################################################
        RootDiskAlarm_Name=os.environ['AccountName']+"-"+name+"-"+instanceid+"-RootDiskUtilization > 90%" 
        cloudwatch.put_metric_alarm(
        AlarmName=RootDiskAlarm_Name,
        ComparisonOperator='GreaterThanThreshold',
        EvaluationPeriods=1,
        MetricName='disk_used_percent',
        Namespace='CWAgent',
        Period=60,
        Statistic='Maximum',
        Threshold=90,
        ActionsEnabled=True,
        AlarmActions=[
            ''+os.environ['SNS']+'',
        ],
        AlarmDescription=RootDiskAlarm_Name,
        Dimensions=[
            {
            'Name': 'InstanceId',
            'Value': instanceid
            },
            {
                "Name": "path",
                "Value": "/"
            },
            {
                "Name": "device",
                "Value": "xvda1"
            },
            {
                "Name": "fstype",
                "Value": "xfs"
            }
            
        ]
        )
        print("RootDisk Alarm for "+name+" "+instanceid+" created")

    #########MemoryAlarm#########LINUX##########################
        MAlarm_Name=os.environ['AccountName']+"-"+name+"-"+instanceid+"-MemoryUtilization > 90%" 
        cloudwatch.put_metric_alarm(
        AlarmName=MAlarm_Name,
        ComparisonOperator='GreaterThanThreshold',
        EvaluationPeriods=1,
        MetricName='mem_used_percent',
        Namespace='CWAgent',
        Period=60,
        Statistic='Maximum',
        Threshold=90,
        ActionsEnabled=True,
        AlarmActions=[
            ''+os.environ['SNS']+'',
        ],
        AlarmDescription=MAlarm_Name,
        Dimensions=[
            {
            'Name': 'InstanceId',
            'Value': instanceid
            }

        ]
        )
        print("Memory Alarm for "+name+" "+instanceid+" created")
    
    else:
        print("unknown OS type/ unidentifiable")
        # TODO: write code...
        # TODO: write code...
        
