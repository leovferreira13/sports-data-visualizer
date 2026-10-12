// Remote QA must never create a local production server.
export function resolveQaTarget(env) {
  if (env.PRODUCT_QA_BASE_URL !== undefined) {
    const url = new URL(env.PRODUCT_QA_BASE_URL);
    if (
      url.protocol !== "https:" || url.username || url.password ||
      url.port || url.pathname !== "/" || url.search || url.hash
    ) {
      throw new Error("PRODUCT_QA_BASE_URL must be an HTTPS origin without credentials, port, path, query or fragment");
    }
    return { base: url.origin, remote: true, serverArgs: null };
  }
  const port = Number(env.PRODUCT_QA_PORT || 3010);
  if (!Number.isInteger(port) || port < 1 || port > 65535) {
    throw new Error("PRODUCT_QA_PORT must be an integer from 1 to 65535");
  }
  return {
    base: `http://127.0.0.1:${port}`,
    remote: false,
    serverArgs: ["node_modules/next/dist/bin/next", "start", "--hostname", "127.0.0.1", "--port", String(port)],
  };
}
