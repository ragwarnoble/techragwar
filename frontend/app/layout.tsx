import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Ragwar Tech | Purposeful AI & Automation",
  description:
    "AI engineering, knowledge systems, and workflow automation. " +
    "Build with purpose. Verify with evidence. Govern with integrity."
};

export default function Layout(
  { children }: Readonly<{ children: React.ReactNode }>
) {
  return <html lang="en"><body>{children}</body></html>;
}
