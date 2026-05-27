document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".highlight").forEach(block => {
        const title = block.querySelector("span.filename");
        const nav = block.querySelector(".md-code__nav");
        if (title && nav) {
            title.appendChild(nav);
        }
    });
});
