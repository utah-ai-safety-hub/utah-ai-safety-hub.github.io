// Sign-up form endpoint. Paste a Formspree form URL here (https://formspree.io/f/xxxxxxx).
// Until it is set, the form tells visitors that sign-ups are not open yet.
var FORM_ENDPOINT = '';

// Light/dark toggle. The initial theme is set inline in each page's <head> to avoid a flash.
(function () {
    var button = document.querySelector('.theme-toggle');
    if (!button) return;
    function label() {
        var dark = document.documentElement.getAttribute('data-theme') === 'dark';
        button.textContent = dark ? 'Light' : 'Dark';
        button.setAttribute('aria-label', dark ? 'Switch to light theme' : 'Switch to dark theme');
    }
    button.addEventListener('click', function () {
        var next = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', next);
        try { localStorage.setItem('theme', next); } catch (e) {}
        label();
    });
    label();
})();

// Sign-up form submission.
(function () {
    var form = document.getElementById('signup-form');
    if (!form) return;
    var status = form.querySelector('.form-status');
    form.addEventListener('submit', function (event) {
        event.preventDefault();
        if (!FORM_ENDPOINT) {
            status.textContent = 'Sign-ups open soon. Please check back in a few days.';
            return;
        }
        status.textContent = 'Sending…';
        fetch(FORM_ENDPOINT, {
            method: 'POST',
            body: new FormData(form),
            headers: { Accept: 'application/json' }
        }).then(function (response) {
            if (!response.ok) throw new Error(response.status);
            form.reset();
            status.textContent = 'Thanks! You are on the list. We will be in touch about the first events.';
        }).catch(function () {
            status.textContent = 'Something went wrong. Please try again in a moment.';
        });
    });
})();
