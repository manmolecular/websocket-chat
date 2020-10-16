let accessToken = null;

var defaultFetch = fetch;

/**
 * Patch fetch to include additional 'Authorization' header
 * @param  {String} url      Original URL
 * @param  {Object} options  Original options
 * @return {Promise}
 */
fetch = function(url, options = {}) {
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

/**
 * Get data from API ('/page'), update and navigate to '/#page'
 * @param  {String} page     page URL
 * @return {null}
 */
loadPage = function(page = '') {
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

/**
 * Add status from API, add to the parent block
 * @param  {String} parent     parent HTML element to append
 * @param  {String} message    status message
 * @return {null}
 */
showStatus = function(parent, message = 'undefined') {
    const container = document.getElementById(parent);
    const element = document.createElement('div');
    element.innerHTML = message + ', go to the <a href="#home">home page</a>'
    container.appendChild(element);
}

window.addEventListener('hashchange', function(event) {
    switch (window.location.hash) {
        case '#home':
            loadPage();
            break;
        case '#chat':
            const ws = `ws://${window.location.hostname}:${window.location.port}/api/chat/ws`;
            const container = document.getElementById('chat-container');
            const socket = new WebSocket(ws);

            auth = JSON.stringify({'token': accessToken, 'message': 'auth'})
            socket.onopen = () => socket.send(auth);

            socket.onmessage = function(event) {
                const element = document.createElement('div');
                const jsonMessage = JSON.parse(event.data);
                const textMessage = document.createTextNode(`${jsonMessage.user} (${jsonMessage.time}): ${jsonMessage.message}`);
                element.appendChild(textMessage);
                container.appendChild(element);
            };
            socket.onclose = function(event) {
                const element = document.createElement('div');
                const textMessage = document.createTextNode('Websocket closed. Please reload.');
                element.appendChild(textMessage);
                element.setAttribute('style', 'color:red;');
                container.appendChild(element);
            };
            document.getElementById('send-button').addEventListener('click', function() {
                const messageFieldElem = document.getElementById('message-field');
                const jsonMessage = JSON.stringify({
                    'message': messageFieldElem.value,
                });
                socket.send(jsonMessage);
            });
            break;
        case '#register':
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
            break;
        case '#login':
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
            break;
    }
});
