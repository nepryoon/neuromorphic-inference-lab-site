// /functions/api/build.js
export function onRequestGet(context) {
  const sha = context.env.CF_PAGES_COMMIT_SHA || "";
  const branch = context.env.CF_PAGES_BRANCH || "";
  const url = context.env.CF_PAGES_URL || "";

  // Questo è il repo del sito (quello che genera il commit SHA del deploy)
  const repo = "nepryoon/neuromorphic-inference-lab-site";
  const commitUrl = sha ? `https://github.com/${repo}/commit/${sha}` : "";

  const data = {
    sha,
    shaShort: sha ? sha.slice(0, 12) : "",
    branch,
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
