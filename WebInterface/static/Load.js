class LoadScreen {
    constructor(duration=2000) {
        const overlay = document.createElement('div');
        overlay.id = 'load-overlay';
        document.body.appendChild(overlay);

        const loadIncication = document.createElement('img');
        loadIncication.src = './static/img/loading.svg';
        overlay.appendChild(loadIncication);

        setTimeout(() => {
            overlay.remove();
        }, duration);
    }
}