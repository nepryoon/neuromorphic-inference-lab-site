export async function onRequest(context) {
  const { request } = context;

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

  const upstream = "https://mv-grid-fault-risk-api.onrender.com/health";

  let res;
  try {
    res = await fetch(upstream, { method: "GET" });
  } catch (e) {
    return new Response(JSON.stringify({ error: "Upstream fetch failed", detail: String(e) }), {
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
