import RelayControlSocket from "./RelayControl.js";

const RelayControl = new RelayControlSocket(
    "192.168.0.27:42488/v1/socketio/sprinklers/control"
);

function getToggleAction(toggle) {
    return toggle.value === "true" ? "enable" : "disable";
}

function updateToggles(relayInfo) {
    $("#toggle-group").empty();

    for (const [id, status] of Object.entries(relayInfo)) {
        const button = document.createElement("button");
        button.innerText = id;
        button.id = id;
        button.className = "toggles";
        button.value = status["is_active"].toString();

        $(button).click(function () {
            // this.value = !(this.value === "true");
            const toggleAction = this.value === "true" ? "disable" : "enable";

            let relayDuration;

            if (toggleAction === "enable") {
                let input = prompt("Enter sprinkler on duration in minutes. (default 10)");

                // user cancelled interaction
                if (input === null) return;

                // default duration (10 minutes)
                if (input === '') input = 10;

                const parsedInput = parseFloat(input);

                // prompt user if invalid input
                if (input <= 0 || isNaN(parsedInput)) {
                    alert("\n Inputted duration is invalid.")
                    return;
                }

                // convert minutes to seconds
                relayDuration = parsedInput * 60;
            }

            RelayControl.sendAction(toggleAction, this.id, relayDuration);
        });

        $("#toggle-group").append(button);
    }
}

function initSocketio() {
    RelayControl.socketio.on("relay_update", (relayInfo) => {
        if (!relayInfo) return;
        // console.log(`[SOCKETIO] Update: ${JSON.stringify(relayInfo)}`);
        console.log(`[SOCKETIO] Update`);
        updateToggles(relayInfo);
    });

    RelayControl.socketio.on("disconnect", (msg) => {
        console.log(`[SOCKETIO] Disconnected: ${msg}`);
        alert(
            "\nSocketIO is reconnecting.\nYou have either lost connection or the server is offline."
        );
    });

    RelayControl.socketio.io.on("reconnect_failed", () => {
        RelayControl.socketio.disconnect();
        alert(
            "\nSocketIO could not reconnect.\nPlease refresh the page to retry."
        );
        console.error(`[SOCKETIO] Failed to reconnect`);
    });

    RelayControl.socketio.io.on("reconnect", () => {
        console.log("[SOCKETIO] Reconnected");
        alert("\nSocketIO has reconnected.");
    });

    RelayControl.socketioConnect();
}

$(window).on("load", initSocketio);
