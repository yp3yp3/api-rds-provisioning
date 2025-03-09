import boto3
import json
import os
import tempfile
from github import Github
import subprocess


def lambda_handler(event, context):
    # Parse the incoming SQS message
    message = event['Records'][0]['body']
    data = json.loads(message)

    db_name = data['db_name']
    engine = data['engine']
    environment = data['environment']

    # Retrieve GitHub token securely from AWS Secrets Manager
    secrets_client = boto3.client('secretsmanager')
    secret_name = os.environ['GITHUB_TOKEN_SECRET_NAME']
    secret_response = secrets_client.get_secret_value(SecretId=secret_name)
    github_token = secret_response['SecretString']

    # GitHub configuration
    repo_name = os.environ['GITHUB_REPO_NAME']
    branch_name = f"add-{environment}-{db_name}"

    # Authenticate with GitHub API
    github_client = Github(github_token)
    repo = github_client.get_repo(repo_name)

    # Path to the Terraform tfvars file
    tfvars_filename = f"{environment}-{db_name}.tfvars"
    tfvars_path = f"terraform/environments/{tfvars_filename}"

    # Generate Terraform .tfvars file content
    tfvars_content = f"""
    db_identifier = \"{db_name}\"
    engine        = \"{engine}\"
    environment   = \"{environment}\"
    """

    # Create or Ensure the branch exists
    try:
        repo.get_branch(branch_name)  # faild If Branch dosen't exist 
    except:
        main_branch = repo.get_branch("main") 
        repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=main_branch.commit.sha)  # Create the Branch החדש

    # Check if the file already exists in the repository and update
    try:
        existing_file = repo.get_contents(tfvars_path, ref=branch_name)
        file_sha = existing_file.sha 
        repo.update_file(
            path=tfvars_path,
            message=f"Update Terraform config for {db_name} in {environment}",
            content=tfvars_content,
            sha=file_sha,  
            branch=branch_name
        )
    except:
        repo.create_file(
            tfvars_path,
            f"Create Terraform config for {db_name} in {environment}",
            tfvars_content,
            branch=branch_name
        )



    # Create a pull request on GitHub
    pr_title = f"Provision RDS: {db_name} [{environment}]"
    pr_body = f"Auto-generated PR to provision RDS instance `{db_name}` ({engine}) in `{environment}` environment."

    pr = repo.create_pull(
        title=pr_title,
        body=pr_title,
        head=branch_name,
        base="main"
    )

    print(f"Pull Request created: {pr.html_url}")

    return {"status": "success", "pr_url": pr.html_url}
