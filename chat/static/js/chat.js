document.addEventListener('DOMContentLoaded', function(event) {
    if (window.location.pathname == '/chat') {
        var ws = `ws://${window.location.hostname}:${window.location.port}/chat/ws`;
        var container = document.getElementById('chat-container');
        var socket = new WebSocket(ws);
        socket.onmessage = function (event) {
            var element = document.createElement('div');
            var text = document.createTextNode(event.data);
            element.appendChild(text);
            container.appendChild(element);
        }
        socket.onclose = function (event) {
            var element = document.createElement('div');
            var text = document.createTextNode('Websocket closed. Please reload.');
            element.appendChild(text);
            element.setAttribute('style', 'color:red;');
            container.appendChild(element);
        }
        document.getElementById('send-button').addEventListener('click', function() {
            var message_field_elem = document.getElementById('message-field');
            socket.send(message_field_elem.value);
        });
    }
    if (window.location.pathname == '/register') {
        document.getElementById('register-button').addEventListener('click', function() {
            var username = document.getElementById('username').value;
            var password = document.getElementById('password').value;
            var options = {
                method: 'POST',
                body: JSON.stringify({"username": username, "password": password}),
                headers: {
                    'Content-Type': 'application/json'
                },
            }
            fetch('/register', options)
                .then(res => res.json())
                .then(json => json['status'])
                .then(status => {
                    if (status === 'success') {
                        window.location.href = '/login';
                    }
                })
        })
    }
    if (window.location.pathname == '/login') {
        document.getElementById('login-button').addEventListener('click', function() {
            var username = document.getElementById('username').value;
            var password = document.getElementById('password').value;
            var options = {
                method: 'POST',
                body: JSON.stringify({"username": username, "password": password}),
                headers: {
                    'Content-Type': 'application/json'
                },
            }
            fetch('/login', options)
                .then(res => res.json())
                .then(json => {
                    if (json['status'] === 'success') {
                        window.location.href = '/';
                    }
                })
        })
    }
});