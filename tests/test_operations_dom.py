import shutil
import subprocess
import json
import re
import pytest
from jinja2 import Environment, FileSystemLoader


def test_operation_dom_contracts():
    node = shutil.which("node")
    if not node:
        pytest.skip("Node.js is required for JS contract tests")
    result = subprocess.run([node, "tests/operations_dom_test.cjs"], capture_output=True, text=True, timeout=20)
    assert result.returncode == 0, result.stdout + result.stderr


def test_report_feedback_dom_contracts():
    node = shutil.which("node")
    if not node:
        pytest.skip("Node.js is required for JS contract tests")
    result = subprocess.run([node, "tests/report_feedback_dom_test.cjs"], capture_output=True, text=True, timeout=20)
    assert result.returncode == 0, result.stdout + result.stderr


def test_product_analytics_consent_storage_failure_and_private_urls():
    node = shutil.which("node")
    if not node:
        pytest.skip("Node.js is required for JS contract tests")
    html = Environment(loader=FileSystemLoader("app/templates")).get_template("_product_analytics.html").render(product_analytics_counter_id=12345)
    script = re.search(r"<script>(.*?)</script>", html, re.S).group(1)
    check = """
const assert=require('node:assert/strict'),vm=require('node:vm');
const script=SCRIPT;
function run(consent,blocked=false,loaded=false){
 const calls=[],scripts=[];const c={localStorage:{getItem:()=>{if(blocked)throw Error('blocked');return consent;}},document:{createElement:()=>({}),head:{appendChild:e=>scripts.push(e)}}};
 c.window=c;if(loaded)c.ym=(...args)=>calls.push(args);vm.createContext(c);vm.runInContext(script,c);
 c.dmatrixReachGoal('feedback_submitted',{category:'interface',has_rating:true});return {c,calls,scripts};
}
for(const e of [run(null),run('no'),run('yes',true)]){assert.equal(e.scripts.length,0);assert.equal(e.calls.length,0);}
const fresh=run('yes');assert.equal(fresh.scripts.length,1);
const init=fresh.c.ym.a.find(x=>x[1]==='init')[2];
assert.equal(init.defer,true);assert.equal(init.trackLinks,false);assert.equal(init.webvisor,false);
const existing=run('yes',false,true);assert.equal(existing.scripts.length,0);assert.equal(existing.calls.length,1);
assert.equal(existing.calls[0][1],'reachGoal');assert.equal(existing.calls[0][2],'feedback_submitted');
""".replace("SCRIPT", json.dumps(script))
    result = subprocess.run([node, "-e", check], capture_output=True, text=True, timeout=20)
    assert result.returncode == 0, result.stdout + result.stderr
