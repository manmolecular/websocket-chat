document.addEventListener('DOMContentLoaded', function(event) {
    if (window.location.pathname === '/chat') {
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
    if (window.location.pathname === '/register') {
        document.getElementById('register-button').addEventListener('click', function() {
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
                .then((json) => json.status)
                .then((status) => {
                    if (status === 'success') {
                        window.location.href = '/login';
                    }
                });
        });
    }
    if (window.location.pathname === '/login') {
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
                        window.location.href = '/';
                    }
                });
        });
    }
});