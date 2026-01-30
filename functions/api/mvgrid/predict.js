export async function onRequest(context) {
  const { request } = context;

  const cors = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
  };

  if (request.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: cors });
  }

  if (request.method !== "POST") {
    return new Response(JSON.stringify({ error: "Method not allowed" }), {
      status: 405,
      headers: { ...cors, "Content-Type": "application/json" },
    });
  }

  const upstream = "https://mv-grid-fault-risk-api.onrender.com/predict";

  // Forward JSON body as-is
  const body = await request.text();

    async function sleep(ms) {
    return new Promise((r) => setTimeout(r, ms));
  }

  async function fetchWithTimeout(url, opts, timeoutMs) {
    const ctrl = new AbortController();
    const t = setTimeout(() => ctrl.abort(), timeoutMs);
    try {
      return await fetch(url, { ...opts, signal: ctrl.signal });
    } finally {
      clearTimeout(t);
    }
  }

  let res;
  let lastErr = null;

  // Retry to mitigate Render cold starts
  for (let attempt = 1; attempt <= 3; attempt++) {
    try {
      res = await fetchWithTimeout(
        upstream,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body,
        },
        15000
      );

      // If upstream is waking up, you might see 502/503 briefly
      if (res.status >= 500 && res.status <= 599 && attempt < 3) {
        await sleep(800 * attempt);
        continue;
      }

      break;
    } catch (e) {
      lastErr = e;
      if (attempt < 3) {
        await sleep(800 * attempt);
        continue;
      }
    }
  }

  if (!res) {
    return new Response(JSON.stringify({ error: "Upstream fetch failed", detail: String(lastErr) }), {
      status: 502,
      headers: { ...cors, "Content-Type": "application/json" },
    });
  }


  const text = await res.text();
  return new Response(text, {
    status: res.status,
    headers: { ...cors, "Content-Type": res.headers.get("Content-Type") || "application/json" },
  });
}

