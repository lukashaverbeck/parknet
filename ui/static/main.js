let standbyContainer = document.getElementById("container-standby");
let closeButton = document.getElementById("btn-close");


class Mode {
    constructor(id, name, active = false) {
        this.id = id;
        this.name = name;
        this.active = active;
        this.container = document.getElementById("container-" + name);
    }

    activate() {
        this.active = true;
        this.container.classList.remove("no-display");
    }

    deactivate() {
        this.active = false;
        this.container.classList.add("no-display");
    }
}


class ManualMode extends Mode {
    constructor() {
        super("drive/manual", "manual");

        this.keyUp = document.getElementById("key-forward");
        this.keyDown = document.getElementById("key-backward");
        this.keyLeft = document.getElementById("key-left");
        this.keyRight = document.getElementById("key-right");

        this.run();
    }

    run() {
        document.onkeydown = (event) => {
            event = event || window.event;

            if (event.key == "ArrowUp" || event.key == "w") {
                this.keyUp.classList.add("active");
            }

            if (event.key == "ArrowDown" || event.key == "s") {
                this.keyDown.classList.add("active");
            }

            if (event.key == "ArrowLeft" || event.key == "a") {
                this.keyLeft.classList.add("active");
            }

            if (event.key == "ArrowRight" || event.key == "d") {
                this.keyRight.classList.add("active");
            }
        }

        document.onkeyup = (event) => {
            event = event || window.event;

            if (event.key == "ArrowUp" || event.key == "w") {
                this.keyUp.classList.remove("active");
            }

            if (event.key == "ArrowDown" || event.key == "s") {
                this.keyDown.classList.remove("active");
            }

            if (event.key == "ArrowLeft" || event.key == "a") {
                this.keyLeft.classList.remove("active");
            }

            if (event.key == "ArrowRight" || event.key == "d") {
                this.keyRight.classList.remove("active");
            }
        }
    }
}


class AutonomousMode extends Mode {
    constructor() {
        super("drive/follow-road", "autonomous");

        this.stopButton = document.getElementById("btn-stop-autonomous");
        this.restartButton = document.getElementById("btn-restart-autonomous");

        this.stopButton.addEventListener("click", () => {
            this.stopButton.classList.add("no-display");
            this.restartButton.classList.remove("no-display");

            sendRequest("emergency-stop")
        });

        this.restartButton.addEventListener("click", () => {
            this.restartButton.classList.add("no-display");
            this.stopButton.classList.remove("no-display");

            sendRequest("change-mode", { mode: "drive/follow-road" })
        });
    }
}


class ParkingMode extends Mode {
    constructor() {
        super("parking/search", "parking");
    }
}


const MODES = [
    new ManualMode(),
    new AutonomousMode(),
    new ParkingMode()
];


class Menu {
    constructor() {
        this.buttons = [];

        MODES.forEach(mode => {
            let button = document.querySelector("nav button[data-mode=" + mode.name + "]");
            this.buttons.push(button);

            button.addEventListener("click", () => this.toggle(mode, button));
        });

        closeButton.addEventListener("click", () => {
            MODES.forEach(mode => {
                mode.deactivate();
            });

            this.buttons.forEach(button => {
                button.classList.remove("active");
            });

            standbyContainer.classList.remove("no-display");
            closeButton.classList.add("no-display");

            sendRequest("change-mode", { mode: "parking/standby" })
        });
    }

    toggle(mode, button) {
        this.buttons.forEach(btn => {
            btn.classList.remove("active");
        });

        MODES.forEach(mode => {
            mode.deactivate();
        });

        button.classList.add("active");
        mode.activate();

        standbyContainer.classList.add("no-display");
        closeButton.classList.remove("no-display")

        sendRequest("change-mode", { mode: mode.id })
    }
}


function sendRequest(url, data = {}) {
    let xhr = new XMLHttpRequest();

    xhr.open("POST", url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify(data));
}


let startRecordingButton = document.getElementById("btn-start-recording");
let stopRecordingButton = document.getElementById("btn-stop-recording");

startRecordingButton.addEventListener("click", () => {
    startRecordingButton.classList.add("no-display");
    stopRecordingButton.classList.remove("no-display");

    sendRequest("start-recording");
});

stopRecordingButton.addEventListener("click", () => {
    stopRecordingButton.classList.add("no-display");
    startRecordingButton.classList.remove("no-display");

    sendRequest("stop-recording");
});