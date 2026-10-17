import "server-only";
import { localContent, parseContent } from "./content";

function required(name: string): string {
  const value = process.env[name];
  if (!value) throw new Error(`Missing ${name}`);
  return value;
}

export async function getSiteContent() {
  const provider = process.env.CMS_PROVIDER || "local";
  if (provider === "local") return localContent;

  let url: URL;
  let token: string;

  if (provider === "contentful") {
    const space = encodeURIComponent(required("CONTENTFUL_SPACE_ID"));
    const environment = encodeURIComponent(
      process.env.CONTENTFUL_ENVIRONMENT || "master"
    );
    url = new URL(
      `https://cdn.contentful.com/spaces/${space}/environments/${environment}/entries`
    );
    url.searchParams.set("content_type", "sitePage");
    url.searchParams.set("fields.slug", "home");
    url.searchParams.set("limit", "1");
    token = required("CONTENTFUL_DELIVERY_TOKEN");
  } else if (provider === "strapi") {
    url = new URL("/api/site-page", required("STRAPI_URL"));
    const local = process.env.NODE_ENV !== "production" &&
      url.hostname === "localhost" && url.protocol === "http:";
    if (url.protocol !== "https:" && !local) {
      throw new Error("Strapi requires HTTPS");
    }
    token = required("STRAPI_API_TOKEN");
  } else {
    throw new Error("Unsupported CMS_PROVIDER");
  }

  const response = await fetch(url, {
    headers: { Authorization: `Bearer ${token}` },
    redirect: "error",
    next: { revalidate: 300 },
    signal: AbortSignal.timeout(8000)
  });
  if (!response.ok) throw new Error("CMS request failed");
  const data = await response.json();
  return parseContent(
    provider === "contentful" ? data.items?.[0]?.fields : data.data
  );
}
