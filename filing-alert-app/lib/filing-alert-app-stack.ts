import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as s3 from "aws-cdk-lib/aws-s3";
import * as targets from "aws-cdk-lib/aws-events-targets";
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as sns from "aws-cdk-lib/aws-sns";
import * as iam from "aws-cdk-lib/aws-iam";
import * as events from "aws-cdk-lib/aws-events";
import * as subscriptions from 'aws-cdk-lib/aws-sns-subscriptions';

export class FilingAlertAppStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);
    const environmentName = this.node.tryGetContext('environmentName');
    // Create S3 bucket to store artifacts
    const bucket = new s3.Bucket(this, 'FileStoreBucket', {
      bucketName: `filing-storage-${environmentName}`
    })

    // Create daily trigger
    const triggerRule = new events.Rule(this, 'Rule', {
      schedule: events.Schedule.rate(cdk.Duration.days(1)),
    });
    const filingTopic = new sns.Topic(this, 'FilingTopic');
    const email = this.node.tryGetContext('email');
    filingTopic.addSubscription(new subscriptions.EmailSubscription(email));


    // Lambda function to execute core logic
    const lambdaFunctionHandler = new lambda.Function(this, 'MyLambdaHandler', {
      runtime: lambda.Runtime.PYTHON_3_11,
      code: lambda.Code.fromAsset('../filing-scraper-lambda/dist/filing-scraper-lambda.zip'),
      handler: "filing_scraper.scraper.main",
      environment: {
        S3_BUCKET_NAME: bucket.bucketName,
        SNS_ARN: filingTopic.topicArn,
      },
      timeout: cdk.Duration.seconds(90),
    })
    // Event trigger to invoke lambda
    triggerRule.addTarget(new targets.LambdaFunction(lambdaFunctionHandler))

    const snsTopicPolicy = new iam.PolicyStatement({
      actions: ['sns:publish'],
      resources: ['*'],
    });

    lambdaFunctionHandler.addToRolePolicy(snsTopicPolicy)

    bucket.grantReadWrite(lambdaFunctionHandler);
  }
}
