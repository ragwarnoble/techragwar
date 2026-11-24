"use client";

import { useMemo, useState } from "react";
import type { ArticleSummary } from "../lib/articles";
import { ArticleCard } from "./article-card";

export function ArticleSearch({ articles }: { articles: ArticleSummary[] }) {
  const [query, setQuery] = useState("");
  const matches = useMemo(() => {
    const terms = query.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
    return articles.filter(article => {
      const text = [article.title, article.description, ...article.tags].join(" ").toLocaleLowerCase();
      return terms.every(term => text.includes(term));
    });
  }, [query, articles]);

  return <section aria-label="Browse articles">
    <div className="article-search-controls">
      <label htmlFor="article-search">Search articles</label>
      <input id="article-search" type="search" value={query}
        onChange={event => setQuery(event.target.value)}
        placeholder="Search by title, topic, or keyword…" autoComplete="off" />
      <p role="status" aria-live="polite">{matches.length} {matches.length === 1 ? "article" : "articles"} found</p>
    </div>
    {matches.length ? <div className="articles-grid">{matches.map(article =>
      <ArticleCard key={article.slug} article={article} />)}</div>
    : <div className="articles-empty"><p>{articles.length ? "No articles match your search." : "Articles are coming soon."}</p>
      {query && <button type="button" onClick={() => setQuery("")}>Clear search</button>}</div>}
  </section>;
}
