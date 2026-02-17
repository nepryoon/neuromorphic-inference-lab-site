// /functions/api/health.js
// Cloudflare Pages Function: proxy/fallback for /api/health

export async function onRequest(context) {
  const { request, env } = context;

  const cors = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
  };

  if (request.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: cors });
  }

  if (request.method !== "GET") {
    return new Response(JSON.stringify({ error: "Method not allowed" }), {
      status: 405,
      headers: { ...cors, "Content-Type": "application/json" },
    });
  }

  // Get backend URL from environment variable
  const backendUrl = env.API_BACKEND_URL || "https://api.neuromorphicinference.com";
  const upstream = `${backendUrl}/health`;

  try {
    // Fetch with 5s timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000);

    const res = await fetch(upstream, {
      method: "GET",
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    // If successful, return backend response
    if (res.ok) {
      const data = await res.json();
      return new Response(JSON.stringify(data), {
        status: 200,
        headers: { ...cors, "Content-Type": "application/json" },
      });
    }

    // If backend returns error status, still try to parse and return it
    const text = await res.text();
    return new Response(text, {
      status: res.status,
      headers: { ...cors, "Content-Type": "application/json" },
    });

  } catch (error) {
    // On failure (timeout, network error, etc.), return degraded status
    const fallbackResponse = {
      status: "degraded",
      services: {
        inference: "unreachable"
      },
      timestamp: new Date().toISOString(),
      error: error.name === "AbortError" ? "timeout" : (error.message || "unreachable")
    };

    return new Response(JSON.stringify(fallbackResponse), {
      status: 503,
      headers: { ...cors, "Content-Type": "application/json" },
    });
  }
}
