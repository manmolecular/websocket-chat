let accessToken = null;

var defaultFetch = fetch;

fetch = function(url, options) {
    if (accessToken !== null) {
        if (options['headers'] !== undefined) {
            options['headers']['Authorization'] = `Bearer ${accessToken}`;
        } else {
            options['headers'] = {
                'Authorization': `Bearer ${accessToken}`
            }
        }
    }
    return defaultFetch(url, options);
}

loadPage = function(page) {
    const container = document.getElementById('home-container');
    const options = {
        method: 'GET',
    };
    fetch('/' + page, options)
        .then((res) => res.text())
        .then((html) => {
            container.innerHTML = html;
            window.location.hash = '#' + page;
        });
}

showStatus = function(parent, message) {
    const container = document.getElementById(parent);
    const element = document.createElement('div');
    element.innerHTML = message + ', go to the <a href="#home">home page</a>'
    container.appendChild(element);
}

window.addEventListener('hashchange', function(event) {
    if (window.location.hash === '#home') {
        loadPage('');
    }
    if (window.location.hash === '#chat') {
        const ws = `ws://${window.location.hostname}:${window.location.port}/api/chat/ws`;
        const container = document.getElementById('chat-container');
        const socket = new WebSocket(ws);
        socket.onmessage = function(event) {
            const element = document.createElement('div');
            const text = document.createTextNode(event.data);
            element.appendChild(text);
            container.appendChild(element);
        };
        socket.onclose = function(event) {
            const element = document.createElement('div');
            const text = document.createTextNode('Websocket closed. Please reload.');
            element.appendChild(text);
            element.setAttribute('style', 'color:red;');
            container.appendChild(element);
        };
        document.getElementById('send-button').addEventListener('click', function() {
            const messageFieldElem = document.getElementById('message-field');
            socket.send(messageFieldElem.value);
        });
    }
    if (window.location.hash === '#register') {
        window.document.getElementById('register-button').addEventListener('click', function() {
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const options = {
                method: 'POST',
                body: JSON.stringify({
                    'username': username,
                    'password': password,
                }),
                headers: {
                    'Content-Type': 'application/json',
                },
            };
            fetch('/api/register', options)
                .then((res) => res.json())
                .then((json) => {
                    if (json.status === 'success') {
                        showStatus('register-container', json.message);
                    }
                });
        });
    }
    if (window.location.hash === '#login') {
        document.getElementById('login-button').addEventListener('click', function() {
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const options = {
                method: 'POST',
                body: JSON.stringify({
                    'username': username,
                    'password': password,
                }),
                headers: {
                    'Content-Type': 'application/json',
                },
            };
            fetch('/api/login', options)
                .then((res) => res.json())
                .then((json) => {
                    if (json.status === 'success') {
                        accessToken = json.token;
                        showStatus('login-container', json.message);
                    }
                });
        });
    }
});
