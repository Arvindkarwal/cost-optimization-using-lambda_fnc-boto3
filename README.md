# AWS Cost Optimization with Lambda

![Image](https://github.com/user-attachments/assets/36e536e5-cc18-46a1-b617-0be843024060)

## Overview

This project automates AWS resource cleanup to reduce unnecessary costs by identifying and deleting unused resources using an AWS Lambda function. The AWS Cost Optimization script uses Python and Boto3 library to identify and clean up unused resources in an AWS account. It focuses on:

1. **Elastic IPs**: Releases unused Elastic IPs (EIPs) that are not associated with any instance.
2. **EBS Snapshots**: Deletes EBS snapshots if their corresponding volumes no longer exist.
3. **S3 Buckets**: Deletes empty S3 buckets while skipping buckets with existing data.

## Key Features

- **Cost Savings**: Automatically identifies and removes unused resources to reduce costs.
- **Automation**: Runs periodically using a cron job configured through **AWS EventBridge Scheduler**.
- **AWS Lambda Integration**: Script is deployed as an AWS Lambda function.
- **Secure Operations**: Ensures no critical resources are deleted by checking associations or dependencies before deletion.

## High-Level Workflow

1. **Script Development**:
   - A Python script was written using Python and Boto3 to interact with AWS services (EC2, S3).
   - The script ensures safety by performing checks before deleting resources.

2. **Deployment**:
   - The script was zipped and uploaded to an S3 bucket.
   - An AWS Lambda function was created and linked to the script using the S3 bucket file.

3. **Role and Permissions**:
   - The Lambda function was assigned a role with the following necessary policies:
     - **Elastic IP Cleanup**: `ec2:DescribeAddresses` and `ec2:ReleaseAddress`.
     - **EBS Snapshot Cleanup**: `ec2:DescribeSnapshots` and `ec2:DeleteSnapshot`.
     - **S3 Bucket Cleanup**: `s3:ListBucket`, `s3:ListObjectsV2`, and `s3:DeleteBucket`.

4. **Automation**:
   - A recurring schedule was created using **AWS EventBridge Scheduler** to invoke the Lambda function after desired time period.
   - A cron job was configured for periodic execution.

5. **Monitoring**:
   - Execution logs were monitored via **AWS CloudWatch** to track the success or failure of the function.

## Technologies Used

- **AWS Services**: Lambda, S3, EC2, EventBridge Scheduler, CloudWatch
- **Programming Language**: Python
- **Libraries**: Boto3 (AWS SDK for Python)

