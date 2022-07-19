/**
 *
 * @param {string} postUrl
 * @param {dict} postBodyData
 * @returns {Promise} fetch post response
 */
function fetchPost(postUrl, postBodyData = {}) {
    return fetch(postUrl, {
        method: "POST",
        cache: "no-cache",
        referrerPolicy: "no-referrer",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(postBodyData),
    });
}

/**
 *
 * @param {string} getUrl
 * @returns {Promise} fetch get response
 */
function fetchGet(getUrl) {
    return fetch(getUrl, {
        method: "GET",
        referrerPolicy: "no-referrer",
        headers: {
            Accept: "application/json",
        },
    });
}

export { fetchGet, fetchPost };
