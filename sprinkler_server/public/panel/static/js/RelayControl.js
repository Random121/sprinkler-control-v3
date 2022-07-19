import { fetchGet, fetchPost } from "./Utils.js";

const ACTION = Object.freeze({
    ENABLE: "enable",
    DISABLE: "disable",
});

class RelayControlSocket {
    constructor(socketioAddress) {
        this.socketioAddress = socketioAddress;
        this.socketio = io(this.socketioAddress, {
            transports: ["websocket"],
            autoConnect: false,
            reconnectionAttempts: 3,
        });
    }

    /**
     * @returns valid relay actions
     */
    static get ACTION() {
        return ACTION;
    }

    socketioConnect() {
        this.socketio.connect();
    }

    sendAction(relayAction, relayId = "", relayDuration) {
        if (this.socketio == undefined) {
            throw new Error("SocketIO was not initialized");
        }

        if (!Object.values(ACTION).includes(relayAction)) {
            throw new Error(`Invalid relay action: ${relayAction}`);
        }

        this.socketio.emit("relay_action", {
            action_name: relayAction,
            arguments: {
                relay_id: relayId,
                duration: relayDuration
            },
        });
    }
}

export default RelayControlSocket;

// class RelayApi {
//     constructor(apiAddress) {
//         this.apiAddress = apiAddress;
//     }

//     /**
//      * @returns valid relay actions
//      */
//     static get ACTION() {
//         return ACTION;
//     }

//     /**
//      *
//      * @param {ACTION} relayAction
//      * @param {string} relayId
//      */
//     async sendAction(relayAction, relayId = "") {
//         if (!Object.values(ACTION).includes(relayAction)) {
//             throw new Error(`Invalid relay action: ${relayAction}`);
//         }

//         const response = await fetchPost(`${this.apiAddress}/${relayId}`, {
//             action: relayAction,
//         });

//         if (!response.ok) {
//             throw new Error(`Failed to send relay action: ${relayAction}`);
//         }
//     }

//     /**
//      *
//      * @param {string} relayId
//      * @returns relay status dictionary
//      */
//     async getStatus(relayId = "") {
//         const response = await fetchGet(`${this.apiAddress}/${relayId}`);

//         if (!response.ok) {
//             throw new Error(`Failed to get relay status`);
//         }

//         const jsonData = await response.json();

//         return jsonData;
//     }
// }
