import matter from "gray-matter";

export type Article = {
  slug: string; title: string; description: string; date: string;
  tags: string[]; draft: boolean; body: string;
};
export type ArticleSummary = Omit<Article, "body" | "draft">;

export function validSlug(slug: string): boolean {
  return /^[a-z0-9-]+$/.test(slug);
}

export function parseArticle(slug: string, source: string): Article | null {
  if (!validSlug(slug)) return null;
  const { data, content } = matter(source);
  return {
    slug, title: String(data.title ?? slug), description: String(data.description ?? ""),
    date: String(data.date ?? ""), tags: Array.isArray(data.tags) ? data.tags.map(String) : [],
    draft: data.draft !== false, body: content,
  };
}

export function publishedSummaries(articles: (Article | null)[]): ArticleSummary[] {
  return articles.filter((article): article is Article => !!article && !article.draft)
    .map(({ slug, title, description, date, tags }) => ({ slug, title, description, date, tags }))
    .sort((a, b) => b.date.localeCompare(a.date));
}
