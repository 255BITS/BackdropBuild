import os
import argparse
import subprocess

def docker_build_push(service_path, service, ecr, version):
    original_dir = os.getcwd()
    os.chdir('../')
    cmd = [
        'docker', 
        'buildx', 
        'build', 
        '--platform', 
        'linux/arm64', 
        '-t', 
        f'{ecr}/{service}:{version}', 
        '-f',
        f'{service_path}/Dockerfile',
        '--push', 
        '.'
    ]
    print("-- Running >", (" ").join(cmd))
    subprocess.check_call(cmd)
    os.chdir(original_dir)  # change back to the original directory

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('pattern', nargs='?', default=None)
    args = parser.parse_args()

    print("Logging into aws ecr")
    aws_password = subprocess.check_output(['aws', 'ecr', 'get-login-password']).decode().strip()

    ecr = os.getenv('ECR', '532091552808.dkr.ecr.us-west-2.amazonaws.com')
    subprocess.run(['docker', 'login', '--username', 'AWS', '--password-stdin', ecr], input=aws_password, text=True, check=True)

    print("build push and tag docker image")

    services = ['gptactionhub', 'gptactionhubproxy', 'gptactionhubmemory']
    version = '1.0'
    service_paths = {
        'gptactionhub': 'portal',
        'gptactionhubproxy': 'proxy',
        'gptactionhubmemory': 'memory',
    }

    for service in services:
        if args.pattern is None or args.pattern in service:
            service_path = service
            if service in service_paths:
                service_path = service_paths[service]
                docker_build_push(service_path, service, ecr, version)
            else:
                print("Skipping ", service)

    print("Project has been built but not redeployed.  To redeploy run:")
    print("   ./deploy.sh")

if __name__ == '__main__':
    main()

