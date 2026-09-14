const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const script = fs.readFileSync('app/static/report-feedback.js', 'utf8');
function setup({thanks = false, broadcast = true, form = true, stored = new Map(), path = '/projects/1/report'} = {}) {
    const events = {}, question = {hidden: false}, requests = [], messages = [], scrolls = [];
    const feedbackForm = {listeners: {}, addEventListener(name, fn) {this.listeners[name] = fn;}};
    const thanksNode = {
        attributes: {}, focused: false,
        setAttribute(name, value) {this.attributes[name] = value;},
        focus(options) {this.focused = true; this.focusOptions = options;},
    };
    const ctx = {
        document: {
            hidden: false,
            getElementById: id => id === 'report-feedback-question' ? (form ? question : null)
                : id === 'report-feedback-form' ? (form ? feedbackForm : null)
                : (id === 'report-feedback-thanks' && thanks ? thanksNode : null),
            addEventListener: (name, fn) => {events[name] = fn;},
        },
        fetch: (url, options) => new Promise((resolve, reject) => requests.push({url, options, resolve, reject})),
        addEventListener: (name, fn) => {events[name] = fn;},
        location: {pathname: path},
        sessionStorage: {
            getItem: key => stored.get(key) || null,
            setItem: (key, value) => stored.set(key, value),
            removeItem: key => stored.delete(key),
        },
        scrollX: 12,
        scrollY: 900,
        scrollTo: (x, y) => scrolls.push([x, y]),
        requestAnimationFrame: fn => fn(),
    };
    let channel;
    if (broadcast) ctx.BroadcastChannel = class {
        constructor(name) {assert.equal(name, 'dmatrix-report-question'); channel = this;}
        postMessage(value) {messages.push(value);}
    };
    ctx.window = ctx;
    vm.runInNewContext(script, ctx);
    return {ctx, events, question, feedbackForm, thanksNode, requests, messages, channel, stored, scrolls};
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

    const positionStore = new Map();
    const submitting = setup({stored: positionStore});
    submitting.feedbackForm.listeners.submit();
    const saved = JSON.parse(positionStore.get('dmatrix-report-feedback-position:/projects/1/report'));
    assert.equal(saved.path, '/projects/1/report');
    assert.equal(saved.y, 900);
    const returned = setup({thanks: true, form: false, stored: positionStore});
    assert.deepEqual(returned.scrolls, [[12, 900]]);
    assert.equal(returned.thanksNode.focused, true);
    assert.equal(returned.thanksNode.focusOptions.preventScroll, true);
    assert.equal(positionStore.size, 0);

    const unrelated = new Map([['dmatrix-report-feedback-position:/projects/1/report', JSON.stringify(saved)]]);
    const anotherReport = setup({thanks: true, form: false, stored: unrelated, path: '/projects/2/report'});
    assert.deepEqual(anotherReport.scrolls, []);
    console.log('Report feedback: cache, tabs, failures, races and optional channel OK');
})().catch(error => {console.error(error); process.exitCode = 1;});
