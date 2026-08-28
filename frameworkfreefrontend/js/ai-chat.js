const API_URL =
  "http://localhost:8000/api";


export function initializeAIChat() {

  const form =
    document.querySelector("#chatForm");

  const input =
    document.querySelector("#chatInput");

  const messages =
    document.querySelector("#chatMessages");


  if (!form || !input || !messages) {
    return;
  }


  form.addEventListener(
    "submit",
    async event => {

      event.preventDefault();


      const message =
        input.value.trim();


      if (!message) {
        return;
      }


      addMessage(
        "user",
        message
      );


      input.value = "";

      input.disabled = true;


      const loading =
        addMessage(
          "assistant",
          "Thinking..."
        );


      try {

        const response =
          await fetch(
            `${API_URL}/chat`,
            {
              method: "POST",

              headers: {
                "Content-Type":
                  "application/json"
              },

              body: JSON.stringify({
                message
              })
            }
          );


        if (!response.ok) {
          throw new Error(
            "AI request failed"
          );
        }


        const data =
          await response.json();


        loading.remove();


        addMessage(
          "assistant",
          data.response
        );


      } catch (error) {

        console.error(error);

        loading.remove();


        addMessage(
          "assistant",
          "Sorry, the AI service is currently unavailable."
        );

      } finally {

        input.disabled = false;

        input.focus();

      }

    }
  );


  function addMessage(
    role,
    text
  ) {

    const message =
      document.createElement("div");


    message.className =
      `chat-message ${role}`;


    const label =
      document.createElement("span");

    label.className =
      "chat-label";

    label.textContent =
      role === "user"
        ? "YOU"
        : "AI";


    const paragraph =
      document.createElement("p");

    paragraph.textContent =
      text;


    message.append(
      label,
      paragraph
    );


    messages.appendChild(
      message
    );


    messages.scrollTop =
      messages.scrollHeight;


    return message;

  }

}

