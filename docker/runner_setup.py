import docker
import os
from dotenv import load_dotenv

load_dotenv()  # Loads variables from .env into os.environ

client = docker.from_env()

env_vars = [
    f'GITHUB_OWNER={os.environ.get("GITHUB_OWNER", "")}',
    f'GITHUB_REPOSITORY={os.environ.get("GITHUB_REPOSITORY", "")}',
    f'GITHUB_TOKEN={os.environ.get("GITHUB_TOKEN", "")}',
    'RUNNER_WORKDIR=_work',
    'RUNNER_LABELS=linux'
]

image, _ = client.images.build(path='.', dockerfile='Dockerfile_runner', tag='runner-app')

containers = []
for i in range(10):
    container = client.containers.run(
        'runner-app',
        name=f'runner-{i}',
        detach=True,
        environment=env_vars + [f'RUNNER_NAME=runner-{i}']
    )
    containers.append(container)

print(f'Started {len(containers)} containers.')
