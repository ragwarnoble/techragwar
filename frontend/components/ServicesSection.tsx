import type { getSiteContent } from "../lib/cms";

export function ServicesSection({ content }: { content: Awaited<ReturnType<typeof getSiteContent>> }) {
  return (<>
<section id="services">
        <span className="eyebrow">01 / CAPABILITIES</span>
        <h2>Start with the work that matters.</h2>
        <div className="cards">
          {content.services.map((service, i) => <article key={i}>
            <span className="eyebrow">{String(i + 1).padStart(2, "0")} ↗</span>
            <h3>{service.title}</h3>
            <p>{service.description}</p>
          </article>)}
        </div>
      </section>
  </>);
}
