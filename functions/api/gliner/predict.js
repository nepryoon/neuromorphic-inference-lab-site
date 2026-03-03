/**
 * /functions/api/gliner/predict.js
 *
 * Cloudflare Pages Function: same-origin proxy for the GLiNER Financial NER API.
 *
 * Why this exists:
 * - Keeps the demo UI on a clean same-origin endpoint (/api/gliner/predict)
 * - Avoids CORS headaches and lets you swap the backend URL without editing frontend code
 * - Allows minimal abuse-mitigation controls (origin allowlist, request size limits)
 *
 * Environment variables (Cloudflare Pages):
 * - GLINER_DEMO_BACKEND_URL   e.g. "https://gliner-ner-api.yourdomain.com"
 * - GLINER_DEMO_BACKEND_AUTH  optional, e.g. "Bearer <token>" or "Basic <base64>"
 * - DEMO_ALLOWED_ORIGIN       optional, default "https://www.neuromorphicinference.com"
 */

function jsonResponse(body, status = 200, extraHeaders = {}) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
      ...extraHeaders,
    },
  });
}

function withCors(headers, origin) {
  const h = new Headers(headers);
  if (origin) h.set("access-control-allow-origin", origin);
  h.set("access-control-allow-methods", "POST, OPTIONS");
  h.set("access-control-allow-headers", "content-type");
  h.set("access-control-max-age", "86400");
  return h;
}

export async function onRequestOptions(context) {
  const { request, env } = context;

  const allowedOrigin =
    env.DEMO_ALLOWED_ORIGIN || "https://www.neuromorphicinference.com";
  const origin = request.headers.get("Origin") || "";

  // Only echo CORS headers for the allowed origin.
  const corsOrigin = origin === allowedOrigin ? origin : allowedOrigin;

  return new Response(null, {
    status: 204,
    headers: withCors(
      {
        "cache-control": "no-store",
      },
      corsOrigin
    ),
  });
}

export async function onRequestPost(context) {
  const { request, env } = context;

  const allowedOrigin =
    env.DEMO_ALLOWED_ORIGIN || "https://www.neuromorphicinference.com";
  const origin = request.headers.get("Origin") || "";

  // Minimal origin allowlist (helps against casual abuse; not a full security boundary).
  if (origin && origin !== allowedOrigin) {
    return jsonResponse(
      { detail: "Forbidden origin." },
      403,
      Object.fromEntries(withCors({}, allowedOrigin))
    );
  }

  const backendBase = (env.GLINER_DEMO_BACKEND_URL || "").trim();
  if (!backendBase) {
    return jsonResponse(
      { detail: "Backend URL is not configured (GLINER_DEMO_BACKEND_URL)." },
      500,
      Object.fromEntries(withCors({}, allowedOrigin))
    );
  }

  // Basic payload size guard (demo safety).
  const contentLength = request.headers.get("content-length");
  if (contentLength && Number(contentLength) > 64_000) {
    return jsonResponse(
      { detail: "Request too large for demo endpoint." },
      413,
      Object.fromEntries(withCors({}, allowedOrigin))
    );
  }

  let payload;
  try {
    payload = await request.json();
  } catch {
    return jsonResponse(
      { detail: "Invalid JSON body." },
      400,
      Object.fromEntries(withCors({}, allowedOrigin))
    );
  }

  // Minimal schema validation (the backend will validate properly too).
  const texts = Array.isArray(payload?.texts) ? payload.texts : null;
  if (!texts || texts.length < 1 || texts.length > 32) {
    return jsonResponse(
      { detail: "Field 'texts' must be a list with 1..32 items." },
      422,
      Object.fromEntries(withCors({}, allowedOrigin))
    );
  }

  const threshold =
    typeof payload?.threshold === "number" ? payload.threshold : 0.5;

  const labels = Array.isArray(payload?.labels) ? payload.labels : undefined;

  const upstreamUrl = backendBase.replace(/\/+$/, "") + "/predict";

  const upstreamHeaders = {
    accept: "application/json",
    "content-type": "application/json",
  };

  if (env.GLINER_DEMO_BACKEND_AUTH) {
    upstreamHeaders["authorization"] = env.GLINER_DEMO_BACKEND_AUTH;
  }

  let upstreamResp;
  try {
    upstreamResp = await fetch(upstreamUrl, {
      method: "POST",
      headers: upstreamHeaders,
      body: JSON.stringify({
        texts,
        threshold,
        ...(labels ? { labels } : {}),
      }),
    });
  } catch (err) {
    return jsonResponse(
      { detail: "Upstream request failed.", error: String(err) },
      502,
      Object.fromEntries(withCors({}, allowedOrigin))
    );
  }

  const respText = await upstreamResp.text();
  const respHeaders = withCors(
    {
      "cache-control": "no-store",
      "content-type":
        upstreamResp.headers.get("content-type") ||
        "application/json; charset=utf-8",
    },
    allowedOrigin
  );

  return new Response(respText, {
    status: upstreamResp.status,
    headers: respHeaders,
  });
}
