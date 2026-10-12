import { describe, expect, it } from "vitest";
import { resolveQaTarget } from "./product-qa-target.mjs";

describe("production QA target", () => {
  it("keeps remote QA independent of the local port/server", () => {
    expect(resolveQaTarget({
      PRODUCT_QA_BASE_URL: "https://portfolio.example/",
      PRODUCT_QA_PORT: "invalid",
    })).toEqual({ base: "https://portfolio.example", remote: true, serverArgs: null });
  });

  it.each(["", "http://portfolio.example", "https://user:secret@portfolio.example", "https://portfolio.example/en", "https://portfolio.example?x=1", "https://portfolio.example#methodology", "https://portfolio.example:4000"])(
    "rejects a malformed remote origin (%s)", (base) => {
      expect(() => resolveQaTarget({ PRODUCT_QA_BASE_URL: base })).toThrow();
    },
  );

  it("retains local mode and its explicit loopback binding", () => {
    const target = resolveQaTarget({ PRODUCT_QA_PORT: "4321" });
    expect(target.base).toBe("http://127.0.0.1:4321");
    expect(target.remote).toBe(false);
    expect(target.serverArgs.slice(-4)).toEqual(["--hostname", "127.0.0.1", "--port", "4321"]);
  });

  it.each(["0", "65536", "1.2", "invalid"])("rejects an invalid local port (%s)", (port) => {
    expect(() => resolveQaTarget({ PRODUCT_QA_PORT: port })).toThrow();
  });
});
