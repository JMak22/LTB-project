(function () {
  "use strict";

  const button = document.querySelector(".nav-toggle");
  const nav = document.querySelector(".primary-nav");

  if (button && nav) {
    button.addEventListener("click", function () {
      const open = button.getAttribute("aria-expanded") === "true";
      button.setAttribute("aria-expanded", String(!open));
      nav.classList.toggle("is-open", !open);
    });

    nav.addEventListener("click", function (event) {
      if (event.target.matches("a")) {
        button.setAttribute("aria-expanded", "false");
        nav.classList.remove("is-open");
      }
    });
  }

  document.querySelectorAll("[data-section-nav]").forEach(function (sectionNav) {
    const links = Array.from(sectionNav.querySelectorAll('.section-nav-links a[href^="#"]'));
    const select = sectionNav.querySelector("[data-section-select]");
    const sections = [];

    links.forEach(function (link) {
      const target = document.querySelector(link.getAttribute("href"));
      const observed = target && (target.closest("section") || target);
      if (observed && !sections.includes(observed)) sections.push(observed);
    });

    function setActive(hash) {
      links.forEach(function (link) {
        const active = link.getAttribute("href") === hash;
        link.classList.toggle("is-active", active);
        if (active) link.setAttribute("aria-current", "location");
        else link.removeAttribute("aria-current");
      });
      if (select && select.value !== hash) select.value = hash;
    }

    if (select) {
      select.addEventListener("change", function () {
        if (!select.value) return;
        const target = document.querySelector(select.value);
        if (target) target.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    }

    if ("IntersectionObserver" in window && sections.length) {
      const observer = new IntersectionObserver(function (entries) {
        const visible = entries.filter(function (entry) { return entry.isIntersecting; })
          .sort(function (left, right) { return left.boundingClientRect.top - right.boundingClientRect.top; });
        if (!visible.length) return;
        const current = visible[0].target;
        const link = links.find(function (candidate) {
          const target = document.querySelector(candidate.getAttribute("href"));
          return target && (target.closest("section") || target) === current;
        });
        if (link) setActive(link.getAttribute("href"));
      }, { rootMargin: "-145px 0px -58% 0px", threshold: [0, .05] });
      sections.forEach(function (section) { observer.observe(section); });
    }
  });
})();
