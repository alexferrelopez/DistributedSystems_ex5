const resetAnimation = (element, animationName) => {
    element.style.animation = "none";
    requestAnimationFrame(() => {
        element.style.animation = `${animationName} 0.5s ease-out`;
    });
};

const updateOrCreateCard = (subKey, value, groupFlex, cachedValues) => {
    let card = groupFlex.querySelector(`[data-key="${subKey}"]`);
    const isAdded = !card;
    const isUpdated = card && cachedValues[subKey] !== value;

    if (!card) {
        card = document.createElement("div");
        card.dataset.key = subKey;
        card.className = "flex items-center bg-white rounded border border-gray-200 p-2 text-sm";
        groupFlex.appendChild(card);
    }

    card.innerHTML = `
        <div class="mr-1 font-medium text-gray-700">Key ${subKey}:</div>
        <div class="font-semibold text-gray-900">${value}</div>
    `;

    if (isAdded) {
        resetAnimation(card, "flash-green");
    } else if (isUpdated) {
        resetAnimation(card, "flash-blue");
    }

    cachedValues[subKey] = value;
};

const processNodeData = (jsonData, groupFlex, cachedValues) => {
    Object.entries(jsonData).forEach(([subKey, value]) => {
        updateOrCreateCard(subKey, value, groupFlex, cachedValues);
    });
};

window.addEventListener("DOMContentLoaded", () => {
    const nodeGrid = document.getElementById("node-grid");
    const keyMap = new Map();

    const websocket = new WebSocket("ws://localhost:5678/");
    websocket.onmessage = ({ data }) => {
        const [key, jsonString] = data.split(" :");
        const jsonData = JSON.parse(jsonString.trim().replace(/'/g, '"'));
        let groupContainer;
        let cachedValues;

        if (keyMap.has(key)) {
            const nodeData = keyMap.get(key);
            groupContainer = nodeData.container;
            cachedValues = nodeData.values;
        } else {
            groupContainer = document.createElement("div");
            groupContainer.className = "flex items-center gap-2 border border-gray-300 p-3 bg-gray-50 rounded w-full";
            groupContainer.innerHTML = `
                <h2 class="text-md font-bold text-gray-800 mr-4">Node ${key}</h2>
                <div class="flex flex-wrap gap-1"></div>
            `;
            cachedValues = {};
            keyMap.set(key, { container: groupContainer, values: cachedValues });
            nodeGrid.appendChild(groupContainer);
        }

        const groupFlex = groupContainer.querySelector("div.flex");
        processNodeData(jsonData, groupFlex, cachedValues);
    };
});
