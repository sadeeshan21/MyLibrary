document.addEventListener("DOMContentLoaded", () => {
    const searchInputs = document.querySelectorAll(".catalog-search input, .global-search input");
    searchInputs.forEach(input => {
        input.addEventListener("focus", () => input.closest(".catalog-search, .global-search")?.classList.add("focused"));
        input.addEventListener("blur", () => input.closest(".catalog-search, .global-search")?.classList.remove("focused"));
    });
});
