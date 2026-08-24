export function initializeContact() {

  const form =
    document.querySelector("#contactForm");

  const status =
    document.querySelector("#formStatus");


  if (!form || !status) {
    return;
  }


  form.addEventListener(
    "submit",
    event => {

      event.preventDefault();


      const name =
        document.querySelector("#name")
          .value.trim();

      const email =
        document.querySelector("#email")
          .value.trim();

      const message =
        document.querySelector("#message")
          .value.trim();


      if (!name || !email || !message) {

        status.textContent =
          "Please complete all fields.";

        return;
      }


      status.textContent =
        "Message validated. Backend integration coming next.";

      form.reset();

    }
  );

}
