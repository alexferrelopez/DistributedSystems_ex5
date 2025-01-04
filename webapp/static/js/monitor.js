window.addEventListener("DOMContentLoaded", () => {
    const messages = document.createElement("ul");
    document.body.appendChild(messages);

    const keyMap = new Map(); // Map to keep track of existing keys and their DOM elements

    const websocket = new WebSocket("ws://localhost:5678/");
    websocket.onmessage = ({ data }) => {
        const [key, value] = data.split(" :"); // Split the data into key and content
        if (keyMap.has(key)) {
            // If the key exists, update the row content
            keyMap.get(key).textContent = `${key}: ${value}`;
        } else {
            // If the key doesn't exist, create a new row
            const message = document.createElement("li");
            message.textContent = `${key}: ${value}`;
            messages.appendChild(message);
            keyMap.set(key, message); // Save the key and its DOM element
        }
    };
});
