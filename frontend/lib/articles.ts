import fs from "node:fs";
import path from "node:path";
import { parseArticle, publishedSummaries, validSlug, type Article, type ArticleSummary } from "./article-metadata";

export type { Article, ArticleSummary } from "./article-metadata";

function missing(error: unknown): boolean {
  return (error as NodeJS.ErrnoException | null)?.code === "ENOENT";
}

export function getArticle(slug: string): Article | null {
  if (!validSlug(slug)) return null;
  try {
    return parseArticle(slug, fs.readFileSync(path.join(process.cwd(), "content/articles", `${slug}.mdx`), "utf8"));
  } catch (error) {
    if (missing(error)) return null;
    throw error;
  }
}

export function getArticles(): ArticleSummary[] {
  let files: string[];
  try {
    files = fs.readdirSync(path.join(process.cwd(), "content/articles"));
  } catch (error) {
    if (missing(error)) return [];
    throw error;
  }
  return publishedSummaries(files.filter(file => file.endsWith(".mdx"))
    .map(file => getArticle(file.slice(0, -4))));
}
