export function initializeTheme() {

  const button =
    document.querySelector("#themeToggle");

  if (!button) {
    return;
  }


  const saved =
    localStorage.getItem("theme");


  if (saved === "light") {
    document.body.classList.add("light");
  }


  updateIcon();


  button.addEventListener(
    "click",
    () => {

      document.body.classList.toggle("light");

      const light =
        document.body.classList.contains("light");

      localStorage.setItem(
        "theme",
        light ? "light" : "dark"
      );

      updateIcon();

    }
  );


  function updateIcon() {

    const light =
      document.body.classList.contains("light");

    button.textContent =
      light ? "☀" : "◐";

  }

}
