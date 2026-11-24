// Serve the PWA from this existing Cloudflare Worker using Workers Static Assets.
export default {
  async fetch(request, env) {
    return env.ASSETS.fetch(request);
  }
};
