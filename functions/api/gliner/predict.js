export async function onRequestOptions() {
  return new Response(null, {
    status: 204,
    headers: {
      "access-control-allow-origin": "*",
      "access-control-allow-methods": "POST, OPTIONS",
      "access-control-allow-headers": "content-type",
    },
  });
}

export async function onRequestPost(context) {
  const { request, env } = context;

  const backendBase = (env.GLINER_DEMO_BACKEND_URL || "https://diamond-mounts-general-steady.trycloudflare.com").trim();

  let payload;
  try {
    payload = await request.json();
  } catch {
    return json({ detail: "Invalid JSON body." }, 400);
  }

  const texts = Array.isArray(payload?.texts) ? payload.texts : null;
  if (!texts || texts.length < 1 || texts.length > 10) {
    return json({ detail: "Field 'texts' must be a list with 1..10 items." }, 422);
  }

  const threshold = typeof payload?.threshold === "number" ? payload.threshold : 0.4;
  const labels = Array.isArray(payload?.labels) ? payload.labels : undefined;

  let upstreamResp;
  try {
    upstreamResp = await fetch(backendBase.replace(/\/+$/, "") + "/predict", {
      method: "POST",
      headers: { "content-type": "application/json", accept: "application/json" },
      body: JSON.stringify({ texts, threshold, ...(labels ? { labels } : {}) }),
    });
  } catch (err) {
    return json({ detail: "Upstream request failed.", error: String(err) }, 502);
  }

  const text = await upstreamResp.text();
  return new Response(text, {
    status: upstreamResp.status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "access-control-allow-origin": "*",
      "cache-control": "no-store",
    },
  });
}

function json(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "access-control-allow-origin": "*",
    },
  });
}
