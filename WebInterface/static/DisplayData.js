const UNIT_VELOCITY = 'km/h';
const UNIT_DISTANCE = 'cm';

const agentOutlines = [];

function updateValues() {
    const request = new XMLHttpRequest();
    const dataRoute = '/data';
    request.open('GET', dataRoute, true);

    request.onload = function() {
        if (request.status >= 200 && request.status < 400) {
            const data = JSON.parse(request.responseText);
            new DisplayData(data);
        } else {
            console.log('error!');
        }
    };

    request.send();
}


class DisplayData {
    static getDetails(route) {
        const details = {};

        const container = document.getElementById('details-' + route);
        const detailContainers = container.getElementsByClassName('detail');

        for(let i = 0; i < detailContainers.length; i++) {
            const detailContainer = detailContainers[i];
            const detailID = detailContainer.getAttribute('data-detail');
            details[detailID] = detailContainer.querySelector('.value');
        }

        return details;
    }

    constructor(data_map) {
        this.formation = new Formation(data_map['formation']);
        this.driver = new Driver(data_map['driver']);
        this.sensors = new Sensors(data_map['sensors']);
    }
}


class Driver {
    constructor(data_map) {
        this.detailContainers = DisplayData.getDetails('driver');

        this.velocity = data_map['velocity'];
        this.angle = data_map['angle'];
        this.mode = data_map['mode'];
        this.isRecording = data_map['is_recording'];

        this.speedometer = document.getElementById('speedometer');
        this.steeringWheel = document.getElementById('steering-wheel');

        this.refresh();
    }

    refresh() {
        this.detailContainers.velocity.innerText = this.velocity;
        this.detailContainers.angle.innerText = this.angle;
        this.detailContainers.mode.innerText = this.mode;
        this.detailContainers.isRecording.innerText = this.isRecording;

        this.speedometer.innerText = this.velocity + ' ' + UNIT_VELOCITY;
        this.steeringWheel.style.transform = 'rotate(' + this.angle + 'deg)'
    }
}


class Formation {
    constructor(data_map) {
        this.detailContainers = DisplayData.getDetails('formation');

        this.agents = data_map['agents'];
        this.longest = data_map['longest'];
        this.gap = data_map['gap'];

        this.refresh();
    }

    refresh() {
        this.detailContainers.longest.innerText = this.longest;
        this.detailContainers.gap.innerText = this.gap;

        for (let i = 0; i < this.agents.length; i++) {
            const agent = this.agents[i];
            const id = agent.id;
            const length = agent.length;

            if (i >= agentOutlines.length) {
                agentOutlines.push(new AgentOutline(id, length));
            } else {
                const agentOutline = agentOutlines[i];
                if (id != agentOutline.id) {
                    agentOutline.update(id, length);
                }
            }
        }
    }
}


class Sensors {
    constructor(data_map) {
        this.detailContainers = DisplayData.getDetails('sensors');

        this.front = data_map['front'];
        this.right = data_map['right'];
        this.back = data_map['back'];

        this.topRectangle = document.getElementById('sensor-top');
        this.bottomRectangle = document.getElementById('sensor-bottom');

        this.refresh();
    }

    refresh() {
        this.detailContainers.front.innerText = this.front;
        this.detailContainers.right.innerText = this.right;
        this.detailContainers.back.innerText = this.back;

        this.topRectangle.style.height = this.calcExtent(this.front) + '%';
        this.topRectangle.style.width = this.calcExtent(this.right) + '%';
        this.bottomRectangle.style.height = this.calcExtent(this.back) + '%';
        this.bottomRectangle.style.width = this.calcExtent(this.right) + '%';
    }

    calcExtent(distance) {
        const MAX_DISTANCE = 100;
        let extent = distance / MAX_DISTANCE;

        if (extent > 1) {
            extent = 1;
        }

        return extent * 100;
    }
}


class AgentOutline {
    constructor(id, length) {
        this.id = id;

        this.container = document.createElement('div');
        this.container.classList.add('agent');

        const body = document.createElement('div');
        body.classList.add('body');
        this.container.appendChild(body);

        const tagContainer = document.createElement('div');
        tagContainer.classList.add('tags');
        this.container.appendChild(tagContainer);

        this.idTag = document.createElement('span');
        this.idTag.classList.add('tag');
        tagContainer.appendChild(this.idTag);

        this.lengthTag = document.createElement('span');
        this.lengthTag.classList.add('tag');
        tagContainer.appendChild(this.lengthTag);

        for (let i = 0; i < 4; i++) {
            const wheel = document.createElement('div');
            wheel.classList.add('wheel', 'wheel-' + i);
            body.appendChild(wheel);
        }

        document.getElementById('agents').appendChild(this.container);
        this.update(id, length);
    }

    update(id, length) {
        this.id = id;
        this.idTag.innerHTML = '<i class="material-icons"> bookmark_border </i> <span>' + id + '</span>';
        this.lengthTag.innerHTML = '<i class="material-icons"> space_bar </i> <span>' + length + UNIT_DISTANCE + '</span>';
    }
}