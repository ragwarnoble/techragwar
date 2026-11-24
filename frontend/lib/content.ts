export type SiteContent = {
  headline: string;
  introduction: string;
  services: { title: string; description: string }[];
};

export const localContent: SiteContent = {
  headline: "Purposeful AI. Practical results.",
  introduction:
    "Ragwar Tech helps organizations turn complex data and repetitive work " +
    "into useful, accountable software. Start with one problem. " +
    "Build the evidence to move forward.",
  services: [
    {
      title: "AI & knowledge systems",
      description:
        "Find answers in your own information with grounded responses " +
        "and measurable retrieval quality."
    },
    {
      title: "Workflow automation",
      description:
        "Connect your tools, reduce manual handoffs, and give your team time back."
    },
    {
      title: "Responsible AI engineering",
      description:
        "Build evaluation, human oversight, and clear authorization " +
        "into the workflow from the beginning."
    }
  ]
};

function validText(value: unknown, max: number): value is string {
  return typeof value === "string" &&
    value.trim().length > 0 && value.length <= max;
}

export function parseContent(input: unknown): SiteContent {
  if (!input || typeof input !== "object") {
    throw new Error("Invalid site content");
  }
  const value = input as Record<string, unknown>;
  if (
    !validText(value.headline, 160) ||
    !validText(value.introduction, 2000) ||
    !Array.isArray(value.services) ||
    value.services.length < 1 ||
    value.services.length > 12
  ) throw new Error("Invalid site content");

  const services = value.services.map((item: unknown) => {
    if (!item || typeof item !== "object") {
      throw new Error("Invalid service");
    }
    const service = item as Record<string, unknown>;
    if (
      !validText(service.title, 120) ||
      !validText(service.description, 1000)
    ) throw new Error("Invalid service");
    return { title: service.title, description: service.description };
  });

  return {
    headline: value.headline,
    introduction: value.introduction,
    services
  };
}
