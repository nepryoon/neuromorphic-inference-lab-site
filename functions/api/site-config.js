import { resolveSovereignMatrixUrl } from "../../config/sovereign-matrix-config.js";

export function onRequestGet(context) {
  return Response.json(
    {
      sovereignMatrixUrl: resolveSovereignMatrixUrl(
        context.env.NEXT_PUBLIC_SOVEREIGN_MATRIX_URL
      )
    },
    {
      headers: {
        "cache-control": "public, max-age=300",
        "content-type": "application/json; charset=utf-8"
      }
    }
  );
}
