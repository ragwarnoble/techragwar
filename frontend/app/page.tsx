import { getSiteContent } from "../lib/cms";
import { Assistant } from "../components/Assistant";

export default async function Home() {
  const content = await getSiteContent();
  return <>
    <a className="skip" href="#main">Skip to content</a>
    <header>
      <a className="brand" href="/">RAGWAR <span>TECH</span></a>
      <nav aria-label="Main navigation">
        <a href="#services">Capabilities</a>
        <a href="#approach">Our approach</a>
        <a href="#contact">Let’s talk ↗</a>
      </nav>
    </header>
    <main id="main">
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
      <section id="contact" className="contact">
        <span className="eyebrow">03 / LET’S BUILD SOMETHING USEFUL</span>
        <h2>What could your team do with more time?</h2>
        <p>Tell us about one workflow, knowledge challenge, or AI idea.</p>
        <a className="button" href="mailto:ragwartech@gmail.com">
          Contact Ragwar Tech ↗
        </a>
      </section>
    </main>
    <footer>
      <strong>RAGWAR TECH</strong>
      <span>Purpose. Evidence. Integrity.</span>
      <span>© {new Date().getFullYear()} Ragwar Tech</span>
    </footer>
  </>;
}
