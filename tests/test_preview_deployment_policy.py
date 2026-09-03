"""Publishing the review branch must not trigger an automatic Vercel deployment."""
import json
from pathlib import Path


def test_review_branch_disables_auto_deploy_without_changing_main_policy():
    configuration = json.loads(Path("vercel.json").read_text())
    assert configuration["git"]["deploymentEnabled"] == {
        "codex/preview-reliability-favicon": False,
    }
