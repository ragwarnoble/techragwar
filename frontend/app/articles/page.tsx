import type { Metadata } from "next";
import { getArticles } from "../../lib/articles";
import { ArticleSearch } from "../../components/article-search";
import "./articles.css";
import { SiteHeader } from "../../components/SiteHeader";
import { SiteFooter } from "../../components/SiteFooter";

export const metadata: Metadata = {
  title: "Articles | Ragwar Tech",
  description: "Engineering, AI governance and technology perspectives.",
};

export default function ArticlesPage() {
  return <><SiteHeader /><main id="main" className="articles-container">
    <div className="articles-heading">
      <p>RAGWAR TECH / INSIGHTS</p>
      <h1>Articles &amp; Perspectives</h1>
      <p>Engineering, governance, and technology with purpose.</p>
    </div>
    <ArticleSearch articles={getArticles()} />
  </main><SiteFooter /></>;
}
