# ================================================================
# Orbit API
# Description: FastAPI backend for the Orbit application.
# Author: Jerry
# License: MIT
# ================================================================

import argparse
import logging
import os
import sys

import docker
from dotenv import load_dotenv

ENV_VARS = [
    f'GITHUB_OWNER={os.environ.get("GITHUB_OWNER", "")}',
    f'GITHUB_REPOSITORY={os.environ.get("GITHUB_REPOSITORY", "")}',
    f'GITHUB_TOKEN={os.environ.get("GITHUB_TOKEN", "")}',
    'RUNNER_WORKDIR=_work',
    'RUNNER_LABELS=linux'
]


def build_parser():
    """ Build argument parser. """

    parser = argparse.ArgumentParser(
        description='Tool to build and start docker containers for the runner app.'
    )
    parser.add_argument(
        '-b', '--build',
        dest='build',
        default=False,
        help='Optionally build the docker image before starting containers.',
        action='store_true'
    )
    parser.add_argument(
        '-i', '--image-name',
        dest='image_name',
        default='runner-app',
        help='Name of the docker image to build/use.',
        type=str
    )
    parser.add_argument(
        '-v',
        dest='verbose',
        action='count',
        help='verbose output.'
    )

    return parser


def clean_existing_containers(client,
                              match_str: str = None):
    """ Clean up existing containers with names starting with 'runner-' """

    # Remove existing containers
    for container in client.containers.list(all=True):
        logging.info(f'Removing container {container.name}...')

        try:
            if match_str and container.name.startswith(match_str):
                container.remove(force=True)

            else:
                container.remove(force=True)

        except Exception as e:
            logging.info(f'Error removing {container.name}: {e}')


def build_docker_image(client,
                       images_name: str,
                       docker_file_path: str,
                       docker_file: str):
    """ Build Docker image for the runner app """

    logging.info(f"Building Docker image {images_name}...")
    build_logs = client.api.build(
        path=docker_file_path,
        dockerfile=docker_file,
        tag=images_name,
        decode=True
    )

    for chunk in build_logs:
        if 'stream' in chunk:
            logging.info(chunk['stream'], end='')

    image = client.images.get(images_name)

    return image, image.name


def start_runner_containers(client,
                            n: int,
                            image_name: str,
                            env_vars: list):
    """ Start a Docker container for the runner app """

    containers = []
    for i in range(n):
        logging.info(f'Starting container {i}...')
        container = client.containers.run(
            image=image_name,
            name=f'runner-{i}',
            detach=True,
            environment=env_vars + [f'RUNNER_NAME=runner-{i}']
        )
        containers.append(container)

    logging.info(f'Started {len(containers)} containers.')


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    logging.basicConfig(datefmt="%Y-%m-%d %H:%M:%S",
                        format="[%(asctime)s.%(msecs)03d] %(module)s - %(levelname)s: %(message)s",
                        stream=sys.stdout,
                        level=logging.INFO)

    load_dotenv()

    client = docker.from_env()

    clean_existing_containers(client)

    if args.build:
        build_docker_image(
            client=client,
            images_name=args.image_name,
            docker_file_path='.',
            docker_file='Dockerfile_runner'
        )

    start_runner_containers(client=client,
                            n=10,
                            image_name=args.image_name,
                            env_vars=ENV_VARS)
