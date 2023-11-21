import os
import subprocess

container_name = os.getenv("HOSTNAME")

print("My HOSTNAME: ", container_name)

# command = f"docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' {container_name}"
# result = subprocess.run(command, shell=True, capture_output=True, text=True).stdout.strip()

print("my self IP: ", os.getenv("SELF_IP"))

print("---- DONE")
