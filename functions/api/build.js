// /functions/api/build.js
export function onRequestGet(context) {
  const sha = context.env.CF_PAGES_COMMIT_SHA || "";
  const branch = context.env.CF_PAGES_BRANCH || "";
  const url = context.env.CF_PAGES_URL || "";

  // Questo è il repo del sito (quello che genera il commit SHA del deploy)
  const repo = "nepryoon/neuromorphic-inference-lab-site";
  const commitUrl = sha ? `https://github.com/${repo}/commit/${sha}` : "";

  // Get build timestamp from CF_PAGES environment or generate current timestamp
  const buildDate = context.env.CF_PAGES_BUILD_DATE || new Date().toISOString();
  
  const data = {
    sha,
    shaShort: sha ? sha.slice(0, 7) : "",
    commit: sha,  // Add 'commit' alias for client compatibility
    branch,
    built: new Date().toISOString(),  // Always return current ISO timestamp
    builtAt: buildDate,
    timestamp: buildDate,  // Add 'timestamp' alias for client compatibility
    url,
    commitUrl
  };

  return Response.json(data, {
    headers: {
      "cache-control": "no-store",
      "content-type": "application/json; charset=utf-8"
    }
  });
}
