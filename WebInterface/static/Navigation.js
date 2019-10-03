const ACTIVE_ELEMENT_STORAGE_NAME = 'nav-active-element';

class Navigation {
    constructor() {
        this.container = document.querySelector('nav');
        this.routes = ['driver', 'formation', 'sensors'];

        this.buttons = {};
        this.containers = {};
        this.details = {};
        
        this.routes.forEach(route => {
            const button = this.container.querySelector('button[data-route="' + route + '"]');
            const container = document.getElementById(route);
            const details = document.getElementById('details-' + route);

            this.buttons[route] = button;
            this.containers[route] = container;
            this.details[route] = details;

            button.addEventListener('click', () => this.toggle(route));
        });

        let route = localStorage.getItem(ACTIVE_ELEMENT_STORAGE_NAME);
        if (!route) {
            route = this.routes[0];
        }
        this.toggle(route);
    }
    
    toggle(desiredRoute) {
        this.routes.forEach(route => {
            this.buttons[route].classList.remove('active');
            this.containers[route].classList.add('no-display');
            this.details[route].classList.add('no-display');
        });

        this.buttons[desiredRoute].classList.add('active');
        this.containers[desiredRoute].classList.remove('no-display');
        this.details[desiredRoute].classList.remove('no-display');
        
        localStorage.setItem(ACTIVE_ELEMENT_STORAGE_NAME, desiredRoute);
    }
}