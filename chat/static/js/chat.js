/**
 * Create token storage closure
 */
var tokenStorage = function() {
    return {
        /**
         * Set token variable
         * @param {String} token    access token
         * @return {null}
         */
        setToken: function(token) {
            localStorage.setItem('accessToken', token);
        },
        /**
         * Get token variable
         * @return {String} token   access token
         */
        getToken: function() {
            return localStorage.getItem('accessToken');
        },
        /**
         * Delete item
         * @return {null}
         */
        deleteToken: function() {
            localStorage.removeItem('accessToken');
        }
    };
}();

// Patch original fetch function to include auth header
var defaultFetch = fetch;

/**
 * Patch fetch to include additional 'Authorization' header
 * @param  {String} url      Original URL
 * @param  {Object} options  Original options
 * @return {Promise}
 */
var fetch = function(url, options = {}) {
    accessToken = tokenStorage.getToken();
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
var loadPage = function(page = '', method = 'GET', prefix = '') {
    const options = {
        method: method,
    };
    if (prefix !== '') {
        prefix = prefix + '/'
    }
    fetch('/' + prefix + page, options)
        .then(function(response) {
            if (response.ok) {
                return response.text()
            }
            return Promise.reject(`Response status is ${response.status}, not available`);
        })
        .then((text) => {
            document.body.innerHTML = text;
            window.location.hash = '#' + page;
        });
}

/**
 * Add self-made enter listener (because we don't use "submit" listener)
 * @param  {String} element      element to click on
 * @param  {String} container    container to check events
 * @return {null}
 */
var enterListener = function(element, container) {
    window.document.getElementById(container).addEventListener('keyup', function(event) {
        if (event.keyCode === 13) {
            event.preventDefault();
            document.getElementById(element).click();
        }
    });
}

/**
 * Add status from API, add to the parent block
 * @param  {String} parent     parent HTML element to append
 * @param  {String} message    status message
 * @return {null}
 */
var showStatus = function(parent, message = 'undefined', additional = 'go to the <a href="#home">home page</a>') {
    const container = document.getElementById(parent);
    const element = document.createElement('div');
    element.innerHTML = message + ', ' + additional;
    container.appendChild(element);
}

window.addEventListener('hashchange', function(event) {
    switch (window.location.hash) {
        case '#home':
            // Load main page
            loadPage();
            break;
        case '#logout':
            // Remove token, load main page
            tokenStorage.deleteToken();
            loadPage();
            break;
        case '#feedback':
            // Follow feedback url, API usage not required (static)
            break;
        case '#chat':
            // Create WebSocket connection
            const ws = `ws://${window.location.hostname}:${window.location.port}/api/chat/ws`;
            const container = document.getElementById('chat-container');
            const socket = new WebSocket(ws);

            auth = JSON.stringify({'token': tokenStorage.getToken(), 'message': 'auth'})
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
            enterListener('send-button', 'chat-container');
            document.getElementById('send-button').addEventListener('click', function() {
                const messageFieldElem = document.getElementById('message-field');
                const jsonMessage = JSON.stringify({
                    'message': messageFieldElem.value,
                });
                socket.send(jsonMessage);
            });
            break;
        case '#register':
            // Handle registration, send REST API backend request
            enterListener('register-button', 'register-container');
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
                        else {
                            showStatus('register-container', json.message, 'try again');
                        }
                    });
            });
            break;
        case '#login':
            // Handle login, send REST API backend request
            enterListener('login-button', 'login-container');
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
                            tokenStorage.setToken(json.token);
                            showStatus('login-container', json.message);
                        }
                        else {
                            showStatus('login-container', json.message, 'try again');
                        }
                    });
            });
            break;
    }
});
