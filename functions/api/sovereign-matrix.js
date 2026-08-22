import { resolveSovereignMatrixUrl } from "../../config/sovereign-matrix-config.js";

export function onRequestGet(context) {
  const destination = resolveSovereignMatrixUrl(
    context.env.NEXT_PUBLIC_SOVEREIGN_MATRIX_URL
  );
  return Response.redirect(destination, 302);
}
