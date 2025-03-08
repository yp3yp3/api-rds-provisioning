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
    github_token = secret['SecretString']

    # GitHub configuration
    repo_name = os.environ['GITHUB_REPO_NAME']
    branch_name = f"add-{environment}-{db_name}"

    # Create temporary directory for cloning the GitHub repo
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_url = f"https://{github_token}@github.com/{repo_name}.git"
        subprocess.run(["git", "clone", repo_url, tmpdir])
        subprocess.run(["git", "checkout", "-b", branch_name], cwd=tmpdir, check=True)

        # Prepare Terraform .tfvars file content
        tfvars_content = f"""
        db_identifier = \"{db_name}\"
        engine        = \"{engine}\"
        environment   = \"{environment}\"
        """

        # Write the new tfvars file into the environments folder
        tfvars_filename = f"{environment}-{db_name}.tfvars"
        tfvars_path = os.path.join(tmpdir, "terraform/environments", tfvars_filename)

        with open(tfvars_path, "w") as f:
            f.write(tfvars_content)

        # Commit and push changes to GitHub
        subprocess.run(["git", "-C", tmpdir, "add", "."], check=True)
        subprocess.run(["git", "-C", tmpdir, "commit", "-m", f"Provision RDS {db_name} in {environment}"], check=True)
        subprocess.run(["git", "-C", tmpdir, "push", "-u", "origin", branch_name], check=True)

    # Create a pull request on GitHub
    github = boto3.client('secretsmanager')
    secret = secrets_client.get_secret_value(SecretId=os.environ['GITHUB_TOKEN_SECRET_NAME'])
    github_token = secret['SecretString']

    github_client = Github(github_token)
    repo = github_client.get_repo(repo_name)

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
