import projects from "./projects.js";

import {
  initializeNavigation
} from "./navigation.js";

import {
  initializeTheme
} from "./theme.js";

import {
  initializeAnimations
} from "./animations.js";

import {
  initializeContact
} from "./contact.js";


initializeNavigation();
initializeTheme();
initializeAnimations();
initializeContact();


// ========================================
// PROJECTS
// ========================================

const projectsGrid =
  document.querySelector("#projectsGrid");

const filters =
  document.querySelectorAll(".filter");


function renderProjects(category = "all") {

  const filtered =
    category === "all"
      ? projects
      : projects.filter(
          project =>
            project.category === category
        );


  projectsGrid.innerHTML =
    filtered.map((project, index) => `

      <article class="project-card">

        <a
          href="project.html?id=${project.id}"
          class="project-card-link"
        >

          <div class="project-number">
            ${String(index + 1).padStart(2, "0")}
          </div>

          <div>

            <p class="project-type">
              ${project.type}
            </p>

            <h3>
              ${project.title}
            </h3>

            <p>
              ${project.description}
            </p>

            <div class="tags">

              ${project.technologies
                .map(
                  tech =>
                    `<span>${tech}</span>`
                )
                .join("")}

            </div>

          </div>

          <div class="project-links">
            View Case Study →
          </div>

        </a>

      </article>

    `).join("");
}


renderProjects();


filters.forEach(filter => {

  filter.addEventListener("click", () => {

    filters.forEach(item =>
      item.classList.remove("active")
    );

    filter.classList.add("active");

    renderProjects(
      filter.dataset.filter
    );

  });

});


document.querySelector("#year")
  .textContent =
  new Date().getFullYear();
