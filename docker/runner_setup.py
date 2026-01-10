import os

import docker
from dotenv import load_dotenv

load_dotenv()

client = docker.from_env()

env_vars = [
    f'GITHUB_OWNER={os.environ.get("GITHUB_OWNER", "")}',
    f'GITHUB_REPOSITORY={os.environ.get("GITHUB_REPOSITORY", "")}',
    f'GITHUB_TOKEN={os.environ.get("GITHUB_TOKEN", "")}',
    'RUNNER_WORKDIR=_work',
    'RUNNER_LABELS=linux'
]

print("Building Docker image...")
image, _ = client.images.build(path='.',
                               dockerfile='Dockerfile_runner',
                               tag='runner-app')

containers = []
for i in range(10):
    print(f'Starting container {i}...')
    container = client.containers.run(
        image='runner-app',
        name=f'runner-{i}',
        detach=True,
        environment=env_vars + [f'RUNNER_NAME=runner-{i}']
    )
    containers.append(container)

print(f'Started {len(containers)} containers.')
