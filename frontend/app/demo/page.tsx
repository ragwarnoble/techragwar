import { SiteHeader } from "../../components/SiteHeader";
import { SiteFooter } from "../../components/SiteFooter";
import { GovernanceDemo } from "../../components/GovernanceDemo";
import styles from "./demo.module.css";

export const metadata = { title: "Governed AI Engineering Demo | Ragwar Tech" };
export default function DemoPage() {
  return <>
    <SiteHeader />
    <main id="main" className={styles.page}>
      <h1>Trust through verification</h1>
      <p>Explore how engineering evaluation, independent policy review, human approval and scoped authorization precede an AI-assisted software change.</p>
      <p><strong>Interactive simulation:</strong> all operations and evidence are synthetic. No live Control Plane, credentials, repository access or production changes are involved.</p>
      <GovernanceDemo />
      <p>Try failing evaluation or denying approval to see how execution remains blocked.</p>
      <a href="/#contact">Discuss a governed engineering pilot</a>
    </main>
    <SiteFooter />
  </>;
}
