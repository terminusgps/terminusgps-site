document.addEventListener("DOMContentLoaded", function() {
    const article = document.querySelector("article.prose");
    if (article) {
        article.querySelectorAll("h1").forEach(el => {
            el.classList.add(
                "text-gray-900",
                "dark:text-gray-100",
            );
        });
        article.querySelectorAll("h2").forEach(el => {
            el.classList.add(
                "text-gray-800",
                "dark:text-gray-200",
            );
        });
        article.querySelectorAll("h3").forEach(el => {
            el.classList.add(
                "text-gray-800",
                "dark:text-gray-200",
            );
        });
        article.querySelectorAll("h4").forEach(el => {
            el.classList.add(
                "text-gray-800",
                "dark:text-gray-200",
            );
        });
        article.querySelectorAll("h5").forEach(el => {
            el.classList.add(
                "text-gray-800",
                "dark:text-gray-200",
            );
        });
        article.querySelectorAll("h6").forEach(el => {
            el.classList.add(
                "text-gray-800",
                "dark:text-gray-200",
            );
        });
        article.querySelectorAll("p").forEach(el => {
            el.classList.add(
                "text-gray-800",
                "dark:text-gray-200",
            );
        });
        article.querySelectorAll("a").forEach(el => {
            el.classList.add(
                "text-blue-400",
                "hover:text-blue-600",
                "dark:text-blue-600",
                "dark:hover:text-blue-400",
            );
        });
        article.querySelectorAll("ul").forEach(el => {
            el.classList.add(
                "text-gray-800",
                "dark:text-gray-200",
            );
        });
        article.querySelectorAll("ol").forEach(el => {
            el.classList.add(
                "text-gray-800",
                "dark:text-gray-200",
            );
        });
        article.querySelectorAll("li").forEach(el => {
            el.classList.add(
                "text-gray-800",
                "dark:text-gray-200",
            );
        });
        article.querySelectorAll("strong").forEach(el => {
            el.classList.add(
                "text-gray-900",
                "dark:text-gray-100",
            );
        });
        article.querySelectorAll("em").forEach(el => {
            el.classList.add(
                "text-gray-800",
                "font-semibold",
                "dark:text-gray-200",
            );
        });
        article.querySelectorAll("code").forEach(el => {
            el.classList.add(
                "bg-gray-700",
                "dark:bg-gray-200",
                "dark:text-gray-900",
                "p-1",
                "rounded-sm",
                "text-gray-50",
            );
        });
        article.querySelectorAll("pre").forEach(el => {
            el.classList.add(
            );
        });
        article.querySelectorAll("blockquote").forEach(el => {
            el.classList.add(
                "p-4",
                "rounded-md",
                "bg-blue-200",
                "dark:bg-blue-500",
                "opacity-60",
            );
        });
        article.querySelectorAll("table").forEach(el => {
            el.classList.add(
                "touch-pan-x",
                "border",
                "border-solid",
                "dark:text-gray-100",
                "rounded-lg",
                "shadow",
                "text-gray-900",
                "text-left",
            );
        });
    }
});
