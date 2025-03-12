import boto3
import json
import os
from github import Github


def lambda_handler(event, context):
    # Parse the incoming SQS message
    message = event['Records'][0]['body']
    data = json.loads(message)

    db_name = data['db_name']
    engine = data['engine']
    environment = data['environment']
    slack_id = data.get('slack_id', None)

    # Retrieve GitHub token securely from AWS Secrets Manager
    secrets_client = boto3.client('secretsmanager')
    secret_name = os.environ['GITHUB_TOKEN_SECRET_NAME']
    secret_response = secrets_client.get_secret_value(SecretId=secret_name)
    github_token = secret_response['SecretString']

    # GitHub configuration
    repo_name = os.environ['GITHUB_REPO_NAME']
    branch_name = f"add-{environment}-{db_name}"
    tfvars_path = "terraform/environments/terraform.tfvars"

    # Authenticate with GitHub API
    github_client = Github(github_token)
    repo = github_client.get_repo(repo_name)

    # Create or Ensure the branch exists
    try:
        repo.get_branch(branch_name)  # Fail if branch doesn't exist
    except:
        main_branch = repo.get_branch("main")
        repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=main_branch.commit.sha)  # Create new branch

    # Fetch the existing tfvars file content
    try:
        existing_file = repo.get_contents(tfvars_path, ref=branch_name)
        file_sha = existing_file.sha
        existing_content = existing_file.decoded_content.decode("utf-8")
    except:
        # If the file does not exist, initialize it
        existing_content = 'environments = {\n}\n\naws_region = "us-east-1"\n'
        file_sha = None

    # Convert the existing tfvars file into a list of lines
    lines = existing_content.splitlines()

    # Find the `environments = {` block
    environments_start = -1
    for i, line in enumerate(lines):
        if line.strip() == "environments = {":
            environments_start = i
            break

    if environments_start == -1:
        raise Exception("Could not find 'environments = {' in terraform.tfvars")

    # Check if the db_identifier already exists
    for line in lines[environments_start + 1 :]:
        if line.strip().startswith(f"{db_name} = "):  # Checks if db_name already exists
            print(f"Database '{db_name}' already exists. Skipping update.")
            return {"status": "skipped", "message": f"Database '{db_name}' already exists"}

    # Create the new environment line
    new_env_line = f'  {db_name} = {{ environment = "{environment}", engine = "{engine}"'
    if slack_id:
        new_env_line += f', slack_id = "{slack_id}"'
    new_env_line += " }"

    # Insert the new environment after `environments = {`
    lines.insert(environments_start + 1, new_env_line)

    # Rebuild the file content
    new_tfvars_content = "\n".join(lines) + "\n"

    # Commit the updated tfvars file to GitHub
    if file_sha:
        repo.update_file(
            path=tfvars_path,
            message=f"Update Terraform config for {db_name} in {environment}",
            content=new_tfvars_content,
            sha=file_sha,
            branch=branch_name
        )
    else:
        repo.create_file(
            tfvars_path,
            f"Create Terraform config for {db_name} in {environment}",
            new_tfvars_content,
            branch=branch_name
        )

    # Create a pull request on GitHub
    pr_title = f"Provision RDS: {db_name} [{environment}]"
    pr_body = f"Auto-generated PR to provision RDS instance `{db_name}` ({engine}) in `{environment}` environment."

    pr = repo.create_pull(
        title=pr_title,
        body=pr_body,
        head=branch_name,
        base="main"
    )

    print(f"Pull Request created: {pr.html_url}")

    return {"status": "success", "pr_url": pr.html_url}
