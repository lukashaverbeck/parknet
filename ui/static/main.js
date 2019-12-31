const UPDATE_INTERVAL = 100;


class FullscreenButton {
    constructor() {
        this.button = document.getElementById("btn-fullscreen");
        this.icon = this.button.querySelector("i");
        this.isFullscreen = false;

        this.button.addEventListener("click", () => {
           this.toggle() 
        });
    }

    toggle() {
        if (this.isFullscreen) {
            document.exitFullscreen();
            this.icon.innerText = "fullscreen";
        } else {
            document.documentElement.requestFullscreen();
            this.icon.innerText = "fullscreen_exit";
        }

        this.isFullscreen = !this.isFullscreen;
    }

    updateIcon() {
        if (this.isFullscreen) {
            this.icon.innerText = "fullscreen_exit";
        } else {
            this.icon.innerText = "fullscreen";
        }
    }
}


class VideoButton {
    constructor() {
        this.button = document.getElementById("btn-video");
        this.icon = this.button.querySelector("i");
        this.isRecording = false;

        this.button.addEventListener("click", () => {
           this.toggle() 
        });
    }

    toggle() {
        this.isRecording = !this.isRecording;

        if (this.isRecording) {
            sendRequest("./start-recording");
        } else {
            sendRequest("./stop-recording");
        }

        this.updateIcon();
    }

    updateIcon() {
        if (this.isRecording) {
            this.icon.innerText = "stop";
            this.button.classList.add("active");
        } else {
            this.icon.innerText = "videocam";
            this.button.classList.remove("active");
        }
    }
}


class ModeFeed {
    constructor() {
        this.activeMode = undefined;        
        this.startButtons = document.getElementById("container-cards").querySelectorAll("button");
        this.progressCircles = document.getElementById("container-progress").querySelectorAll(".circle");
        
        for (let i = 0; i < this.startButtons.length; i++) {
            const button = this.startButtons[i];
            const circle = this.progressCircles[i];
            const mode = button.getAttribute("data-mode");

            button.addEventListener("click", () => {
                for (let j = 0; j < this.startButtons.length; j++) {
                    this.startButtons[j].classList.remove("active")
                    this.progressCircles[j].classList.remove("active")
                }
                
                if (this.activeMode != mode) {
                    this.activeMode = mode;
                    sendRequest("./change-mode", { "mode": mode });
                    
                    button.classList.add("active");
                    circle.classList.add("active");

                    if (mode == "drive/manual") 
                        Message.show("Tipp", "Nutze die Tastem WASD, um das Fahrzeug zu steuern.");
                } else {
                    this.activeMode = undefined;
                    sendRequest("./change-mode", { "mode": null });
                }
            });
        }

        this.manualDriving();
    }

    manualDriving() {
        document.addEventListener("keydown", event => {
            if (this.activeMode != "drive/manual") return;

            if (["w", "W", "8", "ArrowUp"].includes(event.key))
                sendRequest("./accelerate-forward");
            else if (["s", "S", "2", "ArrowDown"].includes(event.key))
                sendRequest("./accelerate-backward");

            if (["a", "A", "4", "ArrowLeft"].includes(event.key))
                sendRequest("./steer-left");
            else if (["d", "D", "6", "ArrowRight"].includes(event.key))
                sendRequest("./steer-right");
        });
    }
}


class Message {
    static show(title, content) {
        const message = new Message(title, content);
        message.show();

        setTimeout(() => {
            message.remove();
        }, 3000);
    }

    constructor(title, content) {
        this.container = document.createElement("div");
        this.container.classList.add("dialog");

        const closeButton = document.createElement("button");
        closeButton.addEventListener("click", this.remove.bind(this));
        this.container.appendChild(closeButton);

        const closeButtonIcon = document.createElement("i");
        closeButtonIcon.classList.add("material-icons");
        closeButtonIcon.innerText = "expand_more";
        closeButton.appendChild(closeButtonIcon);

        const heading = document.createElement("h1");
        heading.innerText = title;
        this.container.appendChild(heading);

        const text = document.createElement("p");
        text.innerText = content;
        this.container.appendChild(text);
    }

    show() {
        document.body.appendChild(this.container);
    }

    remove() {
        this.container.style.bottom = "-100%";
        setTimeout(() => {
            this.container.remove()
        }, 1000);
    }
}


function sendRequest(url, data = {}) {
    const xhr = new XMLHttpRequest();

    xhr.open("POST", url, true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.send(JSON.stringify(data));
}


function getJSON(url, callback) {
    const xhr = new XMLHttpRequest();
    xhr.open("GET", url, true);
    xhr.responseType = "json";

    xhr.onload = () => {
        const status = xhr.status;
        if (status === 200) callback(xhr.response);
    };

    xhr.send();
}


new VideoButton();
new FullscreenButton();
new ModeFeed();

document.getElementById("btn-emergency-stop").addEventListener("click", () => {
    sendRequest("./emergency-stop")
});

const carContainer = document.getElementById("container-car");
const velocityDisplay = document.getElementById("velocity").querySelector("span");
const steeringAngleDisplay = document.getElementById("steering-angle").querySelector("span");
const distanceTopDisplay = document.getElementById("distance-top").querySelector("span");
const distanceRightDisplay = document.getElementById("distance-right").querySelector("span");
const distanceBottomDisplay = document.getElementById("distance-bottom").querySelector("span");

setInterval(() => {
    getJSON("./data-interval", data => {
        data.forEach(item => {
            let display;

            switch (item.id) {
                case "velocity":
                    display = velocityDisplay;
                    break;

                case "steering-angle":
                    carContainer.style.transform = "rotate(" + item.value + "deg)"

                    display = steeringAngleDisplay;
                    break;

                case "distance-front":
                    display = distanceTopDisplay;
                    break;

                case "distance-right":
                    display = distanceRightDisplay;
                    break;

                case "distance-back":
                    display = distanceBottomDisplay;
                    break;
            
                default:
                    return;
            }

            display.innerText = item.value + " " + item.unit;
        });
    });
}, UPDATE_INTERVAL);
