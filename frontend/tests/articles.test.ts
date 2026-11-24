import { test } from "node:test";
import assert from "node:assert/strict";
import { parseArticle, publishedSummaries } from "../lib/article-metadata";
import { getArticle, getArticles } from "../lib/articles";

test("article inventory exposes only explicitly published entries", () => {
  const published = parseArticle("published", '---\ntitle: Published\ndate: "2026-10-29"\ndraft: false\n---\nBody');
  const draft = parseArticle("draft", "---\ntitle: Draft\ndraft: true\n---\nPrivate draft");
  const implicit = parseArticle("implicit", "---\ntitle: Implicit\n---\nNot approved");
  const stringFalse = parseArticle("string-false", '---\ndraft: "false"\n---\nNot approved');
  const summaries = publishedSummaries([published, draft, implicit, stringFalse, null]);
  assert.deepEqual(summaries.map(a => a.slug), ["published"]);
  assert.equal("body" in summaries[0], false);
  assert.equal(draft?.draft, true);
  assert.equal(implicit?.draft, true);
  assert.equal(stringFalse?.draft, true);
  assert.equal(parseArticle("../published", "Body"), null);
});

test("production loader rejects invalid and missing slugs", () => {
  assert.equal(getArticle("../published"), null);
  assert.equal(getArticle("nonexistent-fixture-9842"), null);
  const article = getArticle("microwave-charcoal-agentic-engineering");
  assert.ok(article);
  assert.equal(getArticles().some(a => a.slug === article.slug), !article.draft);
});
