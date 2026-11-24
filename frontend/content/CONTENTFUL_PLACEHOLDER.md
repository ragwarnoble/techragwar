# Ragwar Tech — Contentful content placeholder

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

## Contentful mapping

Content type API ID: `sitePage`. Create an entry with `slug` = `home`, `headline` as short text, `introduction` as long text, and `services` as a JSON field. Set `CMS_PROVIDER=contentful` and the Contentful variables listed in `frontend/.env.example`. Publish the entry.
