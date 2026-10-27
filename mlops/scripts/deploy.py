"""Start a reviewed CodeDeploy revision; no shell interpolation of workflow input."""

import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

task = os.environ["TASK_DEFINITION"]
if not re.fullmatch(r"arn:aws:ecs:[a-z0-9-]+:\d{12}:task-definition/c4l-[A-Za-z0-9_-]+:\d+", task):
    raise SystemExit("Invalid Clarity4Life task definition ARN")
if not os.environ["GATE_RECORD"].startswith("https://"):
    raise SystemExit("A gate evidence URL is required")


def aws(*args):
    return json.loads(subprocess.check_output(["aws", *args, "--output", "json"]))


definition = aws("ecs", "describe-task-definition", "--task-definition", task)["taskDefinition"]
container = next(c for c in definition["containerDefinitions"] if c["name"] == "api")
if not re.search(r"@sha256:[a-f0-9]{64}$", container["image"]):
    raise SystemExit("Mutable image rejected")
env = {item["name"]: item["value"] for item in container.get("environment", [])}
if env.get("ENVIRONMENT") != "production":
    raise SystemExit("Production release requires production task environment")
if env.get("AGENT_FACTORY", "c4l.adapters:DemoAgent") == "c4l.adapters:DemoAgent":
    raise SystemExit("Demo agent rejected")
if env.get("POLICY_FACTORY", "c4l.policy:BaselinePolicy") == "c4l.policy:BaselinePolicy":
    raise SystemExit("Demo policy rejected")
appspec = {
    "version": 0.0,
    "Resources": [
        {
            "TargetService": {
                "Type": "AWS::ECS::Service",
                "Properties": {
                    "TaskDefinition": task,
                    "LoadBalancerInfo": {"ContainerName": "api", "ContainerPort": 8000},
                },
            }
        }
    ],
}
payload = {
    "applicationName": os.environ["DEPLOY_APPLICATION"],
    "deploymentGroupName": os.environ["DEPLOY_GROUP"],
    "description": "Reviewed gate: " + os.environ["GATE_RECORD"][:200],
    "revision": {"revisionType": "AppSpecContent", "appSpecContent": {"content": json.dumps(appspec)}},
}
with tempfile.TemporaryDirectory() as temp:
    path = Path(temp) / "deployment.json"
    path.write_text(json.dumps(payload))
    result = aws("deploy", "create-deployment", "--cli-input-json", "file://" + str(path))
    print(json.dumps(result))
print("Validate the green task, then explicitly continue traffic using the release runbook.")
