// /functions/api/ehd-watch.js
const ALLOWED_ORIGIN = "https://www.neuromorphicinference.com";

const CORS_HEADERS = {
  "Access-Control-Allow-Origin": ALLOWED_ORIGIN,
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
};

export async function onRequest(context) {
  const { request, env } = context;

  // Handle CORS preflight
  if (request.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: CORS_HEADERS });
  }

  if (request.method !== "POST") {
    return new Response(JSON.stringify({ error: "Method Not Allowed" }), {
      status: 405,
      headers: { ...CORS_HEADERS, "content-type": "application/json; charset=utf-8" },
    });
  }

  const apiKey = env.GROQ_API_KEY;
  if (!apiKey) {
    return new Response(JSON.stringify({ error: "GROQ_API_KEY is not configured" }), {
      status: 500,
      headers: { ...CORS_HEADERS, "content-type": "application/json; charset=utf-8" },
    });
  }

  let body;
  try {
    body = await request.json();
  } catch {
    return new Response(JSON.stringify({ error: "Invalid JSON body" }), {
      status: 400,
      headers: { ...CORS_HEADERS, "content-type": "application/json; charset=utf-8" },
    });
  }

  const { welfare_state = {}, trend = 0, trigger = false, history = "" } = body;
  const { w_ext = 0, budget = 0, freshness = 0 } = welfare_state;

  const lastHistoryLines = history
    .split("\n")
    .filter((line) => line.trim() !== "")
    .slice(-3)
    .join("\n");

  const systemPrompt = `You are EHD-Watch, an exocentric homeostatic agent monitoring air quality (PM2.5) in Milan. \
Think in first person. Write short sentences, 2-3 lines maximum per tick. \
Your welfare vector has three components: W_ext (primary, world-directed), budget (endocentric), freshness (endocentric). \
When trigger is true, reason about which action to take among: fetch_data, post_alert, wait. \
Output plain text only. No markdown.`;

  const userMessage = `Welfare state — W_ext: ${w_ext}, budget: ${budget}, freshness: ${freshness}. \
Trend: ${trend}. Trigger: ${trigger ? "active" : "inactive"}. \
Recent history:\n${lastHistoryLines || "(none)"}`;

  let groqResponse;
  try {
    groqResponse = await fetch("https://api.groq.com/openai/v1/chat/completions", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: "llama-3.1-8b-instant",
        messages: [
          { role: "system", content: systemPrompt },
          { role: "user", content: userMessage },
        ],
      }),
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: "Failed to reach Groq API", detail: err.message }), {
      status: 502,
      headers: { ...CORS_HEADERS, "content-type": "application/json; charset=utf-8" },
    });
  }

  if (!groqResponse.ok) {
    const errorText = await groqResponse.text();
    return new Response(JSON.stringify({ error: "Groq API error", detail: errorText }), {
      status: 502,
      headers: { ...CORS_HEADERS, "content-type": "application/json; charset=utf-8" },
    });
  }

  const groqData = await groqResponse.json();
  const thought = groqData.choices?.[0]?.message?.content;

  if (typeof thought !== "string") {
    return new Response(JSON.stringify({ error: "Unexpected response structure from Groq API" }), {
      status: 502,
      headers: { ...CORS_HEADERS, "content-type": "application/json; charset=utf-8" },
    });
  }

  return new Response(JSON.stringify({ thought }), {
    status: 200,
    headers: { ...CORS_HEADERS, "content-type": "application/json; charset=utf-8" },
  });
}
