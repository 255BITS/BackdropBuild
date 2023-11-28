import subprocess
import argparse
import sys
import os

def ecr_login(manager, key):
    # Command to retrieve the ECR login password using AWS CLI
    get_login_password_cmd = "aws ecr get-login-password --region us-west-2"
    
    # Command to execute Docker login
    docker_login_cmd = (
        f"{get_login_password_cmd} | "
        f"sudo docker login --username AWS --password-stdin 532091552808.dkr.ecr.us-west-2.amazonaws.com"
    )

    # Full SSH command to log in to ECR on the manager node
    ssh_command = f"ssh -i {key} {manager} '{docker_login_cmd}'"
    subprocess.check_call(ssh_command, shell=True)

def parse_arguments():
    parser = argparse.ArgumentParser(description='Deploy services to Docker Swarm.')
    parser.add_argument('project', help='Specify the project to deploy.')
    parser.add_argument('--manager', default='ubuntu@35.93.41.128', help='Specify the Docker Swarm manager host.')
    parser.add_argument('--key', required=True, help='Specify the SSH key path.')
    return parser.parse_args()

def file_exists(project):
    return os.path.isfile(f'./docker-swarm/{project}.yml')

def sync_files(project, manager, key):
    subprocess.check_call(['rsync', '-avz', '-e', f'ssh -i {key}', f'./secrets/{project}.yml', f'{manager}:~/'])

def deploy_stack(project, manager, key):
    deploy_command = f'sudo docker stack deploy --compose-file ~/{project}.yml --with-registry-auth {project} --resolve-image always'
    ssh_command = f'ssh -i {key} {manager} "{deploy_command}"'
    subprocess.check_call(ssh_command, shell=True)

def read_env_file(filename):
    """
    Reads a file and creates a hashmap (dictionary) from its content.
    The file is expected to have lines in the format 'KEY=VALUE'.

    Parameters:
    filename (str): The name of the file to be read.

    Returns:
    dict: A dictionary containing the key-value pairs from the file.
    """
    env_variables = {}

    with open(filename, 'r') as file:
        for line in file:
            # Stripping any leading/trailing whitespace and skipping empty lines
            line = line.strip()
            if line:
                key, value = line.split('=')
                env_variables[key] = value

    return env_variables

def read_env_file(filename):
    """
    Reads a file and creates a hashmap (dictionary) from its content.
    The file is expected to have lines in the format 'KEY=VALUE'.
    Parameters:
    filename (str): The name of the file to be read.

    Returns:
    dict: A dictionary containing the key-value pairs from the file.
    """
    env_variables = {}

    with open(filename, 'r') as file:
        for line in file:
            # Stripping any leading/trailing whitespace and skipping empty lines
            line = line.strip()
            if line:
                key, value = line.split('=', 1)
                env_variables[key] = value

    return env_variables

def replace_secrets(ymlfile, secretsfile, outputymlfile):
    replaced = replace_secrets_in_file(ymlfile, secretsfile)
    with open(outputymlfile, "w") as file:
        file.write(replaced)

def replace_secrets_in_file(source_file, secret_file):
    """
    Reads a source file and a secrets file. Replaces placeholders in the source file with actual secrets.
    Parameters:
    source_file (str): The name of the source file where placeholders are located.
    secret_file (str): The name of the file containing secrets in 'KEY=VALUE' format.

    Returns:
    str: The content of the source file with secrets replaced.
    """
    # Read the secrets into a dictionary
    secrets = read_env_file(secret_file)

    # Read the source file
    with open(source_file, 'r') as file:
        content = file.read()

    # Replace all occurrences of $KEY with its corresponding value in secrets
    for key, value in secrets.items():
        placeholder = f"${key}"
        content = content.replace(placeholder, value)

    return content

def main():
    args = parse_arguments()

    if not file_exists(args.project):
        print(f'The yml file for the project "{args.project}" does not exist.', file=sys.stderr)
        sys.exit(1)
    if not os.path.isfile(f'./secrets/{args.project}.secrets'):
        print(f'The secrets file for the project "{args.project}" does not exist.', file=sys.stderr)
        sys.exit(1)
    try:
        replace_secrets(f'./docker-swarm/{args.project}.yml', f'./secrets/{args.project}.secrets', f'./secrets/{args.project}.yml')
        ecr_login(args.manager, args.key)
        sync_files(args.project, args.manager, args.key)
        deploy_stack(args.project, args.manager, args.key)
        print(f'Project {args.project} deployed successfully!')
    except subprocess.CalledProcessError as e:
        print(f'An error occurred: {e}', file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
