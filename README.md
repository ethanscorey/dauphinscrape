# dauphinscrape
A Scrapy spider for scraping the Dauphin County Prison jail roster.

## Prerequisites
These instructions assume:
1. You have an active AWS account.
2. You have already installed and configured version 2 of the AWS CLI.

## Usage
This project is designed to be run as an AWS Fargate task. To run your own instance, use the following steps:

### Build and push the image to AWS

1. Build the image locally: `docker build -t dauphinscrape .`
2. Create an AWS ECR repository: `aws ecr create-repository --repository-name dauphinscrape`
3. Authenticate to ECR: `aws ecr get-login-password --region <your-aws-region> | docker login --username AWS --password-stdin "<your-aws-account-id>.dkr.ecr.<your-aws-region>.amazonaws.com"`
4. Tag your local image: `docker tag dauphinscrape:latest "<your-aws-account-id>.dkr.ecr.<your-aws-region>.amazonaws.com/dauphinscrape:latest"`
5. Push the image to ECR: `docker push "<your-aws-account-id>.dkr.ecr.<your-aws-region>.amazonaws.com/dauphinscrape:latest"`

### Configure ECS with Fargate
TKTK
