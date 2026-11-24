# Ragwar Tech — Strapi content placeholder

Status: draft for editorial review. This Markdown is a copy reference, not an automatic CMS importer.

## Homepage copy

Headline: Purposeful AI. Practical results.

Introduction: Ragwar Tech helps organizations turn complex data and repetitive work into useful, accountable software. Start with one problem. Build the evidence to move forward.

## Services JSON

```json
[
  {"title":"AI & knowledge systems","description":"Find answers in your own information with retrieval augmented generation, grounded responses, and measurable quality."},
  {"title":"Workflow automation","description":"Connect the tools you already use, reduce manual handoffs, and give your team time back."},
  {"title":"Responsible AI engineering","description":"Build evaluation, human oversight, and clear authorization into the workflow from the beginning."}
]
```

## Brand statement

Build with purpose. Verify with evidence. Govern with integrity.

The current CMS contract supports headline, introduction and services only. Approach, contact and footer copy remain in their section components.

## Publishing checklist

Confirm the public contact address, review all copy, preview on mobile and desktop, and publish only approved text. Keep delivery credentials in protected environment settings.

## Strapi mapping

Use the endpoint and response contract documented in `frontend/README.md` and `frontend/lib/cms.ts`. Set `CMS_PROVIDER=strapi` and the Strapi variables in `frontend/.env.example`. Supply `headline`, `introduction` and `services` in the adapter’s expected response. Confirm API read permissions and publish the content.
