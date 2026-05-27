document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("pre code").forEach(code => {
        const pre = code.parentElement;
        const lang = code.className.replace("language-", "") || "text";
        pre.setAttribute("data-lang", lang);
    });
});
