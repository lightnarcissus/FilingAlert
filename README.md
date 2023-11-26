# Filing Scraper
Builds and deploys an AWS-hosted helper service which sends email updates if there are any relevant filings made by law firms. Can be generalized for other scraping operations as well.
The CDK project builds up following AWS resources:
- Lambda
- S3 Bucket
- SNS Email Topic
- EventBridge CRON Trigger to Lambda (Daily)


The Python Hatch project underpins the Lambda service performing the scraping and S3 file orchestration and updates via SNS if there have been any updates. 


## Installation
### Prerequisites
- Python >=3.7 and Pip
- Node (v20.9.0)
- CDK v2.1
#### AWS Deployment via CDK 

Builds up following AWS resources:
- Lambda
- S3 Bucket
- SNS Email Topic
- EventBridge CRON Trigger to Lambda (Daily)

Ensure you're inside `filing-alert-app` directory
```console
cd filing-alert-app
```
The `cdk.json` file tells the CDK Toolkit how to execute your app.

Requires you to specify `environmentName` as a context variable in CDK to define your stack's resources.
```bash
cdk synth -c environmentName=<YOUR ENV NAME>
```
```bash
cdk deploy -c environmentName=<YOUR ENV NAME> -c email=<EMAIL ADDRESS TO BE NOTIFIED>
```
### Python Hatch Project
Ensure you're inside `filing-scraper-lambda` directory
```console
cd filing-scraper-lambda
```
Then install Hatch and activate the shell
```console
pip install hatch
```
```console
hatch shell
```
Set environment variable `S3_BUCKET_NAME` to your S3 bucket.
```console
python ./filing_scraper/scraper.py
```
More instructions under [project README](https://github.com/lightnarcissus/FilingAlert/blob/main/README.md)
## License

`filing-scraper` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
