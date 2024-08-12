document.addEventListener("DOMContentLoaded", function() {
    const elements = document.querySelectorAll("[data-md-element]");
    elements.forEach(function(element) {
        const elementType = element.getAttribute("data-md-element");

        switch (elementType) {
            case "h1":
                element.classList.add("text-gray-500 dark:text-white");
                break;
            case "h2":
                element.classList.add("text-gray-500 dark:text-white");
                break;
            case "h3":
                element.classList.add("text-gray-500 dark:text-white");
                break;
            case "h4":
                element.classList.add("text-gray-500 dark:text-white");
                break;
            case "h5":
                element.classList.add("text-gray-500 dark:text-white");
                break;
            case "h6":
                element.classList.add("text-gray-500 dark:text-white");
                break;
            case "p":
                element.classList.add("text-gray-500 dark:text-white");
                break;
            case "ul":
                element.classList.add("text-gray-500 dark:text-white");
                break;
            case "li":
                element.classList.add("text-gray-500 dark:text-white");
                break;
            case "ol":
                element.classList.add("text-gray-500 dark:text-white");
                break;
            case "li":
                element.classList.add("text-gray-500 dark:text-white");
                break;
            case "a":
                element.classList.add("text-blue-600 dark:text-blue-400 underline underline-offset-auto hover:text-blue-400 dark:hover:text-blue-600");
                break;
        }
    });
});
