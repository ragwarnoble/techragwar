import { SiteHeader } from "../components/SiteHeader";
import { HeroSection } from "../components/HeroSection";
import { ServicesSection } from "../components/ServicesSection";
import { ApproachSection } from "../components/ApproachSection";
import { ContactSection } from "../components/ContactSection";
import { SiteFooter } from "../components/SiteFooter";
import { getSiteContent } from "../lib/cms";

export default async function Home() {
  const content = await getSiteContent();
  return <>
    <SiteHeader />
    <main id="main">
      <HeroSection content={content} />
      <ServicesSection content={content} />
      <ApproachSection />
      <ContactSection />
    </main>
    <SiteFooter />
  </>;
}
