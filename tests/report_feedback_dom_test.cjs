const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const script = fs.readFileSync('app/static/report-feedback.js', 'utf8');
function setup({thanks = false, broadcast = true, form = true} = {}) {
    const events = {}, question = {hidden: false}, requests = [], messages = [];
    const ctx = {
        document: {
            hidden: false,
            getElementById: id => id === 'report-feedback-question' ? (form ? question : null)
                : (id === 'report-feedback-thanks' && thanks ? {} : null),
            addEventListener: (name, fn) => {events[name] = fn;},
        },
        fetch: (url, options) => new Promise((resolve, reject) => requests.push({url, options, resolve, reject})),
        addEventListener: (name, fn) => {events[name] = fn;},
    };
    let channel;
    if (broadcast) ctx.BroadcastChannel = class {
        constructor(name) {assert.equal(name, 'dmatrix-report-question'); channel = this;}
        postMessage(value) {messages.push(value);}
    };
    ctx.window = ctx;
    vm.runInNewContext(script, ctx);
    return {ctx, events, question, requests, messages, channel};
}
const tick = () => new Promise(resolve => setImmediate(resolve));
const resolve = (request, answered) => request.resolve({ok: true, json: async () => ({answered})});
(async () => {
    const env = setup();
    assert.equal(env.question.hidden, false); // first server render, no answer
    assert.equal(env.requests.length, 0); // opening does not submit or answer
    env.events.pagehide();
    assert.equal(env.question.hidden, true);
    env.events.pageshow({persisted: true});
    assert.equal(env.requests.length, 1);
    assert.equal(env.requests[0].url, '/feedback/report-question/state');
    assert.equal(env.requests[0].options.cache, 'no-store');
    resolve(env.requests[0], false); await tick();
    assert.equal(env.question.hidden, false); // an unanswered question may return

    env.channel.onmessage({data: 'answer-saved'});
    assert.equal(env.question.hidden, true);
    resolve(env.requests[1], true); await tick();
    assert.equal(env.question.hidden, true); // another tab answered

    env.events.visibilitychange();
    env.events.pagehide();
    resolve(env.requests[2], false); await tick();
    assert.equal(env.question.hidden, true); // late response cannot reveal cached form

    env.events.pageshow({persisted: true});
    env.requests[3].reject(Error('offline')); await tick();
    assert.equal(env.question.hidden, true);
    env.events.pageshow({persisted: true});
    env.requests[4].resolve({ok: false}); await tick();
    assert.equal(env.question.hidden, true); // expired authentication

    const fallback = setup({broadcast: false});
    fallback.events.pageshow({persisted: true});
    resolve(fallback.requests[0], true); await tick();
    assert.equal(fallback.question.hidden, true);
    const success = setup({thanks: true, form: false});
    assert.deepEqual(success.messages, ['answer-saved']); // no IDs/content broadcast
    success.events.pageshow({persisted: true});
    assert.equal(success.requests.length, 0);
    console.log('Report feedback: cache, tabs, failures, races and optional channel OK');
})().catch(error => {console.error(error); process.exitCode = 1;});
