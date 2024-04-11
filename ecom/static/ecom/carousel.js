const carouselElement = document.getElementById('ecom-carousel');

const items = [
    {
        position: 0,
        el: document.getElementById('carousel-item-0')
    },
    {
        position: 1,
        el: document.getElementById('carousel-item-1')
    },
    {
        position: 2,
        el: document.getElementById('carousel-item-2')
    },
    {
        position: 3,
        el: document.getElementById('carousel-item-3')
    },
    {
        position: 4,
        el: document.getElementById('carousel-item-4')
    },
];

const options = {
    defaultPosition: 0,
    interval: 3000,

    indicators : {
        activeClasses: 'bg-white dark:bg-gray-800',
        inactiveClasses: 'bg-white/50 dark:bg-gray-800/50 hover:bg-white dark:hover:bg-gray-800',
        items: [
            {
                position: 0,
                el: document.getElementById('carousel-item-0')
            },
            {
                position: 1,
                el: document.getElementById('carousel-item-1')
            },
            {
                position: 2,
                el: document.getElementById('carousel-item-2')
            },
            {
                position: 3,
                el: document.getElementById('carousel-item-3')
            },
            {
                position: 4,
                el: document.getElementById('carousel-item-4')
            },
        ],
    },

    onNext: () => {
        console.log('Next')
    },
    onPrev: () => {
    console.log('Prev')
    },
    onChange: () => {
        console.log('Change')
    },
};

const instanceOptions = {
    id: 'ecom-carousel',
    override: true,
};
