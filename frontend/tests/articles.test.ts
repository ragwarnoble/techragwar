import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, writeFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { getArticle, getArticles } from "../lib/articles";

test("article inventory exposes only explicitly published entries", () => {
  const root = mkdtempSync(join(tmpdir(), "ragwar-articles-"));
  try {
    writeFileSync(join(root, "published.mdx"), '---\ntitle: Published\ndate: "2026-10-29"\ndraft: false\n---\nBody');
    writeFileSync(join(root, "draft.mdx"), '---\ntitle: Draft\ndraft: true\n---\nPrivate draft');
    writeFileSync(join(root, "implicit.mdx"), '---\ntitle: Implicit\n---\nNot approved');
    assert.deepEqual(getArticles(root).map(a => a.slug), ["published"]);
    assert.equal(getArticle("draft", root)?.draft, true);
    assert.equal(getArticle("implicit", root)?.draft, true);
    assert.equal(getArticle("../published", root), null);
    assert.equal(getArticle("missing", root), null);
  } finally { rmSync(root, { recursive: true, force: true }); }
});
