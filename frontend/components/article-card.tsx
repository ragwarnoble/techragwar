import Link from "next/link";
import type { ArticleSummary } from "../lib/articles";

export function ArticleCard({ article }: { article: ArticleSummary }) {
  return <article className="article-card">
    <time dateTime={article.date}>{article.date}</time>
    <h2><Link href={`/articles/${article.slug}`}>{article.title}</Link></h2>
    <p>{article.description}</p>
    <div className="article-tags">{article.tags.map(tag => <span key={tag}>{tag}</span>)}</div>
  </article>;
}
