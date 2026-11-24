import type { Metadata } from "next";
import { notFound } from "next/navigation";
import Link from "next/link";
import { MDXRemote } from "next-mdx-remote/rsc";
import remarkGfm from "remark-gfm";
import { getArticle, getArticles } from "../../../lib/articles";
import "../articles.css";
import { SiteHeader } from "../../../components/SiteHeader";
import { SiteFooter } from "../../../components/SiteFooter";

type Props = { params: Promise<{ slug: string }> };
export function generateStaticParams() { return getArticles().map(a => ({ slug: a.slug })); }
export const dynamicParams = false;

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const article = getArticle((await params).slug);
  if (!article || article.draft) return { robots: { index: false } };
  return { title: `${article.title} | Ragwar Tech`, description: article.description,
    openGraph: { title: article.title, description: article.description, type: "article",
      ...(article.date ? { publishedTime: article.date } : {}) } };
}

export default async function ArticlePage({ params }: Props) {
  const article = getArticle((await params).slug);
  if (!article || article.draft) notFound();
  return <><SiteHeader /><main id="main" className="article-container"><Link href="/articles">← All articles</Link>
    <div className="article-heading"><time dateTime={article.date}>{article.date}</time>
      <h1>{article.title}</h1><p>{article.description}</p></div>
    <div className="article-body">
      <MDXRemote source={article.body} options={{ mdxOptions: { remarkPlugins: [remarkGfm] } }} />
    </div>
  </main><SiteFooter /></>;
}
