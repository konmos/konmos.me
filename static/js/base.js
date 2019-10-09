function copyToClipboard(text) {
    if (window.clipboardData && window.clipboardData.setData) {
        // IE specific code path to prevent textarea being shown while dialog is visible.
        return clipboardData.setData('Text', text);

    } else if (document.queryCommandSupported && document.queryCommandSupported('copy')) {
        let textarea = document.createElement('textarea');
        textarea.textContent = text;
        textarea.style.position = 'fixed';  // Prevent scrolling to bottom of page in MS Edge.
        document.body.appendChild(textarea);
        textarea.select();
        try {
            return document.execCommand('copy');  // Security exception may be thrown by some browsers.
        } catch (ex) {
            console.warn('Copy to clipboard failed.', ex);
            return false;
        } finally {
            document.body.removeChild(textarea);
        }
    }
}

function httpGetAsync(url, callback) {
    let xmlHttp = new XMLHttpRequest();

    xmlHttp.onreadystatechange = function() {
        if (xmlHttp.readyState === 4 && xmlHttp.status === 200)
            callback(xmlHttp.responseText);
    };

    xmlHttp.open("GET", url, true); // true for asynchronous
    xmlHttp.send(null);
}

function httpPostAsync(url, callback, params) {
    let xmlHttp = new XMLHttpRequest();

    xmlHttp.onreadystatechange = function() {
        if (xmlHttp.readyState === 4 && xmlHttp.status === 200)
            callback(xmlHttp.responseText);
    };

    xmlHttp.open("POST", url, true); // true for asynchronous
    xmlHttp.setRequestHeader('Content-type', 'application/json');
    xmlHttp.send(JSON.stringify(params));
}

document.getElementById('email').onclick = function(){
    function c(resp) {
        document.getElementById('email').innerText = '[' + resp + ']';
        document.getElementById('popup-email').classList.toggle('hidden');

        document.getElementById('email').onclick = function() {
            copyToClipboard(resp);
            document.getElementById('popup-email').classList.toggle('hidden');
            document.getElementById('email').onclick = null;
        }
    }

    httpGetAsync('/api/email', c);
};

document.getElementById('top-button').onclick = function() {
    window.scrollTo(0, 0);
};
