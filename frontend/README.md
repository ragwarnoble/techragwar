# Ragwar Tech frontend

Next.js App Router with TypeScript. The existing backend and legacy frontend
are preserved.

## Development
Use Node 22+. Run npm install, npm test, npm run build, npm run typecheck.
Use npm run dev to preview.

## CMS
Copy .env.example to .env.local for local configuration.
CMS_PROVIDER selects local, contentful, or strapi.
Tokens are server-only. Never use NEXT_PUBLIC_ for credentials.

Contentful: create content type sitePage with slug (short text),
headline (short text), introduction (long text), services (JSON).
Publish an entry with slug home. Set CONTENTFUL_SPACE_ID,
CONTENTFUL_ENVIRONMENT and CONTENTFUL_DELIVERY_TOKEN.
Uses the global Contentful Delivery API endpoint.

Strapi 5: create single type site-page with headline (text),
introduction (text), services (JSON). Publish it.
Set STRAPI_URL and a read-only STRAPI_API_TOKEN with site-page.find access.

services is an array of objects with title and description strings.
See lib/content.ts for seed content.
Selected CMS errors do not silently fall back to local content.
CMS publishing does not automatically update the RAG knowledge base.

## RAG
Set RAG_API_URL to the existing Render HTTPS origin, without /api.
Leave RAG_CHAT_ENABLED=false until backend rate limits, spending limits,
and appropriate access controls are verified. Origin checks are not
authentication and do not prevent direct automated abuse.
The adapter uses the existing /api/chat message/response/sources contract.
Live backend and CMS verification remain required.
Request-body duration and upstream response sizes need platform controls.

## Deployment
Root netlify.toml selects frontend, npm run build, and .next.
Use Netlify Next.js support; do not use static export.
Set protected environment variables in Netlify.
Preview and check mobile, desktop, keyboard navigation, CMS and RAG before launch.
Confirm ragwartech@gmail.com as the public contact address.
This change does not provision Strapi, deploy services, or update domain DNS.
