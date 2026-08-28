export function initializeAnimations() {

  const elements =
    document.querySelectorAll(
      ".section-heading, " +
      ".about-grid, " +
      ".skill-row, " +
      ".project-card, " +
      ".contact-form, " +
      ".stat"
    );


  elements.forEach(element => {
    element.classList.add("reveal");
  });


  const observer =
    new IntersectionObserver(
      entries => {

        entries.forEach(entry => {

          if (!entry.isIntersecting) {
            return;
          }

          entry.target.classList.add(
            "visible"
          );

          observer.unobserve(
            entry.target
          );

        });

      },
      {
        threshold: 0.12
      }
    );


  elements.forEach(element => {
    observer.observe(element);
  });


  const counters =
    document.querySelectorAll(
      "[data-count]"
    );


  const counterObserver =
    new IntersectionObserver(
      entries => {

        entries.forEach(entry => {

          if (!entry.isIntersecting) {
            return;
          }

          animateCounter(
            entry.target
          );

          counterObserver.unobserve(
            entry.target
          );

        });

      },
      {
        threshold: 0.5
      }
    );


  counters.forEach(counter => {
    counterObserver.observe(counter);
  });

}


function animateCounter(element) {

  const target =
    Number(element.dataset.count);

  const duration = 1000;

  const start =
    performance.now();


  function update(timestamp) {

    const progress =
      Math.min(
        (timestamp - start) / duration,
        1
      );

    element.textContent =
      Math.floor(progress * target);


    if (progress < 1) {
      requestAnimationFrame(update);
    }

  }


  requestAnimationFrame(update);
}
