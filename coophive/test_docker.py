import docker

try:
    client = docker.from_env()
    print(client.version())
    print("Docker client is connected to the Docker daemon.")
except docker.errors.DockerException as e:
    print(f"Error: {e}")
