export function initializeNavigation() {

  const menuToggle =
    document.querySelector("#menuToggle");

  const nav =
    document.querySelector("#nav");


  if (!menuToggle || !nav) {
    return;
  }


  menuToggle.addEventListener(
    "click",
    () => {

      const open =
        nav.classList.toggle("open");

      menuToggle.setAttribute(
        "aria-expanded",
        String(open)
      );

    }
  );


  nav.querySelectorAll("a")
    .forEach(link => {

      link.addEventListener(
        "click",
        () => {

          nav.classList.remove("open");

          menuToggle.setAttribute(
            "aria-expanded",
            "false"
          );

        }
      );

    });

}
