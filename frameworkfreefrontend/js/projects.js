const projects = [

  {
    id: "ai-research-assistant",
    title: "AI Research Assistant",
    category: "ai",
    type: "AI / LLM",

    description:
      "An AI assistant that retrieves information from a knowledge base and generates contextual responses.",

    overview:
      "A retrieval-augmented generation application combining document ingestion, retrieval, and LLM generation.",

    problem:
      "Large document collections make it difficult to quickly locate and understand relevant information.",

    solution:
      "The system retrieves relevant document chunks and supplies them as context to an LLM.",

    architecture: [
      "User",
      "Frontend",
      "API",
      "LangChain",
      "Retriever",
      "Vector Database",
      "LLM"
    ],

    technologies: [
      "Python",
      "LangChain",
      "LLM",
      "RAG",
      "Vector Database"
    ],

    github: "https://github.com/techragwar",
    demo: "#"
  },


  {
    id: "agent-platform",
    title: "Agentic Automation Platform",
    category: "ai",
    type: "AI AGENT",

    description:
      "An agent-based system capable of selecting tools and executing multi-step workflows.",

    overview:
      "An agent architecture demonstrating tool selection, reasoning, execution, and structured responses.",

    problem:
      "Complex automation often requires conditional decisions and multiple external tools.",

    solution:
      "The agent dynamically selects tools based on the task and coordinates the workflow.",

    architecture: [
      "User",
      "Frontend",
      "Agent API",
      "LLM",
      "Tool Router",
      "External APIs"
    ],

    technologies: [
      "Python",
      "LangChain",
      "Agents",
      "REST APIs"
    ],

    github: "https://github.com/techragwar",
    demo: "#"
  },


  {
    id: "developer-dashboard",
    title: "Developer Dashboard",
    category: "web",
    type: "WEB APPLICATION",

    description:
      "A responsive dashboard for monitoring applications and development workflows.",

    overview:
      "A framework-free frontend demonstrating native browser technologies and API-driven interfaces.",

    problem:
      "Developers need a central interface for viewing application information.",

    solution:
      "A responsive dashboard combines reusable JavaScript components with API data.",

    architecture: [
      "Browser",
      "HTML",
      "CSS",
      "JavaScript",
      "REST API"
    ],

    technologies: [
      "HTML",
      "CSS",
      "JavaScript",
      "REST API"
    ],

    github: "https://github.com/techragwar",
    demo: "#"
  },


  {
    id: "production-api",
    title: "Production API Platform",
    category: "backend",
    type: "BACKEND",

    description:
      "A production-oriented API architecture with validation, authentication, logging, and deployment automation.",

    overview:
      "A backend platform designed around production engineering practices.",

    problem:
      "Prototype APIs require additional security, testing, observability, and deployment infrastructure.",

    solution:
      "The platform introduces structured APIs, validation, authentication, testing, containers, and CI/CD.",

    architecture: [
      "Client",
      "API",
      "Authentication",
      "Database",
      "Docker",
      "CI/CD"
    ],

    technologies: [
      "Python",
      "REST",
      "Docker",
      "CI/CD"
    ],

    github: "https://github.com/techragwar",
    demo: "#"
  }

];

export default projects;
