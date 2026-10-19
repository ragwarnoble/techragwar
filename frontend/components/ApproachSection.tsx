import { Assistant } from "./Assistant";

export function ApproachSection() {
  return (<>
<section id="approach" className="approach">
        <div>
          <span className="eyebrow">02 / OUR APPROACH</span>
          <h2>Build with purpose.<br/>Verify with evidence.<br/>
            <em>Govern with integrity.</em></h2>
          <p>We begin with your team’s real problem, agree on what success
            looks like, and build a focused solution. Testing and human
            review help you decide what is ready for the next step.</p>
          <p>Grounded in service, education, and responsible technology.</p>
        </div>
        <Assistant enabled={
          process.env.RAG_CHAT_ENABLED === "true" &&
          Boolean(process.env.RAG_API_URL)
        } />
      </section>
  </>);
}
