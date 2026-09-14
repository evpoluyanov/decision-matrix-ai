"""Publishing any Codex review branch must not trigger a Vercel deployment."""
import json
from pathlib import Path


def test_review_branches_disable_auto_deploy_without_changing_main_policy():
    configuration = json.loads(Path("vercel.json").read_text())
    assert configuration["git"]["deploymentEnabled"] == {
        "codex/*": False,
    }
