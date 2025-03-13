# RDS Provisioning Automation

## Overview

This repository provides an automated system for provisioning RDS databases based on user input via an HTTP POST request. The system:

- Creates an RDS database according to the request parameters.
- Stores the database credentials in AWS Secrets Manager.
- Optionally sends a Slack notification with the location of the secret.
- Identifies old databases (default: older than 14 days) and deletes them.

## Architecture

The system is built using AWS SAM (Serverless Application Model) and follows this architecture:

1. **API Gateway**: Exposes an HTTP endpoint to receive user requests.
2. **SNS Topic**: Receives and forwards messages from API Gateway.
3. **SQS Queue**: Decouples the message processing and triggers a Lambda function.
4. **Lambda Function**:
   - Processes the SQS message.
   - Updates a Terraform `.tfvars` file with the request parameters.
   - Creates a PR in a GitHub repository with the Terraform changes.
5. **CircleCI Pipeline**:
   - Applies changes in the SAM stack if required.
   - Applies Terraform changes to provision or update the database.
   - If a new database is created and Slack notifications are enabled, sends a message with the ARN of the secret.
   - Identifies old databases (excluding production ones), marks them for deletion, and creates a PR for manual approval.
6. **CloudWatch Monitoring**:
   - Logs and metrics for API Gateway, Lambda, and SQS are collected.
   - A CloudWatch Dashboard is created for monitoring.
7. **IAM Policy Management**:
   - Creates an `RDS_USERS` IAM group.
   - Assigns permissions for accessing created databases and secrets.

## Installation

### 1. Fork the Repository

First, fork this repository to your GitHub account.

### 2. Connect the Repository to CircleCI

- Go to **CircleCI**.
- Add this repository as a new project.
- Set up a pipeline to trigger on pushes to `main`.

### 3. Configure Terraform Variables

Edit the following file:

```bash
terraform/terraform.tfvars
```

Ensure it contains:

- The correct AWS region
- S3 bucket for storing the Terraform state
- DynamoDB table for state locking

### 4. Configure SAM Deployment

Edit the following file:

```bash
sam/samconfig.toml
```

Update it with:

- Stack name
- AWS region
- Domain name
- ARN of the SSL certificate
- GitHub repository location (`username/repo-name`)

### 5. Set Up Environment Variables in CircleCI

Add the following environment variables to CircleCI:

- **`AWS_ACCESS_KEY_ID`**: IAM access key ID for AWS authentication.
- **`AWS_SECRET_ACCESS_KEY`**: IAM secret access key.
- **`GITHUB_TOKEN`**: A GitHub token with `repo` and `pull_requests` permissions.
- **`SLACK_BOT_TOKEN`** (optional): Slack bot token for notifications.

#### How to Obtain the Tokens?

- **AWS credentials**: Follow [AWS IAM guide](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html).
- **GitHub token**: Create one via [GitHub Personal Access Tokens](https://github.com/settings/tokens) with `repo` and `pull_requests` scopes.
- **Slack bot token**: See below.

### 6. Setting Up a Slack App for Notifications

To enable Slack notifications, follow these steps:

#### **1️⃣ Create a Slack App**

1. Go to [Slack API Apps](https://api.slack.com/apps).
2. Click **Create New App** → **From Scratch**.
3. Give your app a name and choose a workspace.

#### **2️⃣ Add Required Permissions**

1. In your app's settings, go to **OAuth & Permissions**.
2. Under **Bot Token Scopes**, add:
   - `chat:write` → To send messages to channels.
   - `chat:write.dm` → To send direct messages to users.
   - `users:read` → To retrieve user Slack IDs.
   - `im:write` → To initiate direct messages.
3. Click **Install to Workspace** and confirm.
4. Copy the **Bot User OAuth Token** (format: `xoxb-xxxxxxxxxx`).

### 7. Deploy the System

- Run the pipeline manually or push changes to `main`.
- The pipeline will deploy the API and Lambda using SAM.
- Update your domain’s DNS settings to point to the new API Gateway.
- Once deployed, you can send requests to create new environments.

## Example API Request

To create a new RDS environment, send an HTTP POST request:

The `slack_id` is the user's personal Slack ID and is optional.

```bash
curl -X POST https://api.yp3yp3.online/provision \
     -H "Content-Type: application/json" \
     -d '{"db_name": "test444", "engine": "mysql", "environment": "dev", "slack_id": "U068JF87UQP"}'
```

Alternatively:

```bash
curl -X POST https://api.yp3yp3.online/provision \
     -H "Content-Type: application/json" \
     -d '{"db_name": "test222", "engine": "postgres", "environment": "prod"}'
```

## Summary

This system automates RDS database provisioning, integrates with GitHub for version-controlled Terraform updates, and provides logging and monitoring via AWS CloudWatch. It also includes lifecycle management for old databases to prevent unnecessary costs.

