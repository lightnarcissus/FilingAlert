# Filing Scraper CDK Project

Builds up following AWS resources:
- Lambda
- S3 Bucket
- SNS Email Topic
- EventBridge CRON Trigger to Lambda (Daily)

The `cdk.json` file tells the CDK Toolkit how to execute your app.

Requires you to specify `environmentName` as a context variable in CDK to define your stack's resources.
```bash
cdk synth -c environmentName=<YOUR ENV NAME>
```

## Useful commands

* `npm run build`   compile typescript to js
* `npm run watch`   watch for changes and compile
* `npm run test`    perform the jest unit tests
* `cdk deploy`      deploy this stack to your default AWS account/region
* `cdk diff`        compare deployed stack with current state
* `cdk synth`       emits the synthesized CloudFormation template
