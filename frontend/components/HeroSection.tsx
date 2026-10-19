import type { getSiteContent } from "../lib/cms";

export function HeroSection({ content }: { content: Awaited<ReturnType<typeof getSiteContent>> }) {
  return (<>
<section className="hero">
        <div>
          <span className="eyebrow">AI ENGINEERING · DATA · AUTOMATION</span>
          <h1>{content.headline}</h1>
          <p className="intro">{content.introduction}</p>
          <a className="button" href="#contact">Start a conversation ↗</a>
          <p className="principles">
            Human oversight · Measurable quality · Clear accountability
          </p>
        </div>
        <div className="blueprint">
          <span className="eyebrow">THE RAGWAR STANDARD</span>
          <div className="orbit">Purpose<br/>+ Evidence<br/>+ Integrity</div>
          <p>Useful systems.<br/>Trust earned at every step.</p>
        </div>
      </section>
  </>);
}
