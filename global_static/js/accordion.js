const accordionElement = document.getElementById('accordion-faq');

// create an array of objects with the id, trigger element (eg. button), and the content element
const accordionItems = [
    {
        id: 'accordion-faq-heading-1',
        triggerEl: document.querySelector('#accordion-faq-heading-1'),
        targetEl: document.querySelector('#accordion-faq-body-1'),
        active: true
    },
    {
        id: 'accordion-faq-heading-2',
        triggerEl: document.querySelector('#accordion-faq-heading-2'),
        targetEl: document.querySelector('#accordion-faq-body-2'),
        active: false
    },
    {
        id: 'accordion-faq-heading-3',
        triggerEl: document.querySelector('#accordion-faq-heading-3'),
        targetEl: document.querySelector('#accordion-faq-body-3'),
        active: false
    }
];

// options with default values
const options = {
    alwaysOpen: true,
    activeClasses: 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-white',
    inactiveClasses: 'text-gray-500 dark:text-gray-400',
    onOpen: (item) => {
        console.log('accordion item has been shown');
        console.log(item);
    },
    onClose: (item) => {
        console.log('accordion item has been hidden');
        console.log(item);
    },
    onToggle: (item) => {
        console.log('accordion item has been toggled');
        console.log(item);
    },
};

// instance options object
const instanceOptions = {
    id: 'accordion-faq',
    override: true
};
