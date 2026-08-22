export const DEFAULT_SOVEREIGN_MATRIX_URL = "https://matrix.neuromorphicinference.com";

/**
 * Resolve the public Decision Matrix URL without allowing insecure destinations.
 * Invalid, non-HTTPS, or credential-bearing overrides fall back to production.
 */
export function resolveSovereignMatrixUrl(value) {
  if (!value) return DEFAULT_SOVEREIGN_MATRIX_URL;

  try {
    const url = new URL(value);
    if (url.protocol !== "https:" || url.username || url.password) {
      return DEFAULT_SOVEREIGN_MATRIX_URL;
    }
    return url.toString().replace(/\/$/, "");
  } catch {
    return DEFAULT_SOVEREIGN_MATRIX_URL;
  }
}
