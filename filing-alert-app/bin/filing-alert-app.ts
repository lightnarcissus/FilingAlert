#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { FilingAlertAppStack } from '../lib/filing-alert-app-stack';

const app = new cdk.App();
new FilingAlertAppStack(app, 'FilingAlertAppStack', {
});