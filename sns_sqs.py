from troposphere import GetAtt, Output, Parameter, Ref, Template
from troposphere.sns import Subscription, Topic
from troposphere.sqs import Queue, RedrivePolicy, QueuePolicy

template = Template()

template.add_description(
    "AWS CloudFormation Sample Template SNS_AND_SQS_: Sample")

dead_letter_queue = template.add_resource(Queue(
    "deadSQS", 
    QueueName="dead__letter_queue__iac_sqs_sample"
    )
)

sqs_aws = template.add_resource(Queue(
    "iacSQS",
    QueueName="iac_sqs_sample",
    RedrivePolicy=RedrivePolicy(
        deadLetterTargetArn=GetAtt(dead_letter_queue, "Arn"),
        maxReceiveCount="5",
    )
))

sns_aws = template.add_resource(Topic("iacSNS",
    TopicName="iac_sns_sample",
    Subscription=[Subscription(
        Protocol="sqs",
        Endpoint=GetAtt(sqs_aws, "Arn")
    )]
))

template.add_output([
    Output(
        "SourceQueueURL",
        Description="URL of the source queue",
        Value=Ref(sqs_aws)
    ),
    Output(
        "SourceQueueARN",
        Description="ARN of the source queue",
        Value=GetAtt(sqs_aws, "Arn")
    ),
    Output(
        "DeadLetterQueueURL",
        Description="URL of the dead letter queue",
        Value=Ref(dead_letter_queue)
    ),
    Output(
        "DeadLetterQueueARN",
        Description="ARN of the dead letter queue",
        Value=GetAtt(dead_letter_queue, "Arn")
    ),
])

template.add_resource(QueuePolicy(
    "AllowSNS2SQSPolicy",
    Queues=[Ref(sqs_aws)],
    PolicyDocument={
        "Version": "2008-10-17",
        "Id": "PublicationPolicy",
        "Statement": [{
            "Sid": "Allow-SNS-SendMessage",
            "Effect": "Allow",
            "Principal": {
              "AWS": "*"
            },
            "Action": ["sqs:SendMessage"],
            "Resource": GetAtt(sqs_aws, "Arn"),
            "Condition": {
                "ArnEquals": {"aws:SourceArn": Ref(sns_aws)}
            }
        }]
    }
))

print(template.to_json())
