# Why I made this

We wanted to block unwanted crawlers without having to implement ALB+WAF and most importantly pay the high costs for WAF.

# How to use the serverless stuff

## Adding a secret

Go to `infra/common` and run:

`serverless encrypt -n <key> -v <value> -k a467f127-a021-4385-8ee9-629b13653411 --stage <stage>`

## Decrypt a secret

Go to `infra/common` and run:

`serverless decrypt -n <key> -k a467f127-a021-4385-8ee9-629b13653411 --stage <stage>`


## Remove stack

`serverless remove`

## Build and deploy

`./build_deploy.sh <stage>`

## Undeploy

### If running this from your machine use `--local` flag

`./undeploy.sh <stage>`

### Which secrets you need

* SentryDSN: DSN for reporting errors to sentry.

* datadogApiKey: Datadog Api Key

* datadogAppKey: Datadog App Key

![aws infra](https://i.imgur.com/YvItj3u.png)

## Infrastructure

It consists on 3 modules:

* Elb Bot Detector: Which checks the Cloudwatch logs for ip's that match the treshold specified in variables.yml files and updates them in the DynamoDB table

Using multithreading it will check that the crawlers are not good ones like Google, Bing, etc as specified in variables.yml or is not coming from trusted ip's ( office for example )

* Autobahn: Responds to trigger from DynamoDB when item is inserted and updates Network ACL's to block traffic from the crawlers

* Unbanner: Cron lambda that checks if the ban time has passed and removes the entry from the ACL
