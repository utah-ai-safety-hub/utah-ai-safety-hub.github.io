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

// Home hero: contour lines brighten under the pointer, and the map legend reads out the real elevation there.
(function () {
    var hero = document.querySelector('.hero');
    var topo = hero && hero.querySelector('.topo');
    var readout = document.getElementById('topo-elev');
    if (!topo || !readout || !window.matchMedia('(hover: hover)').matches) return;
    // Grid behind images/contours-timpanogos.svg: 140 x 105 cells of 4 x 4 px, elevations in feet.
    var GW = 140, GH = 105, SW = 560, SH = 420;
    var grid = null, idle = readout.textContent, pending = 0, last = null;
    fetch('images/timpanogos-elevation.bin')
        .then(function (r) { return r.ok ? r.arrayBuffer() : null; })
        .then(function (b) { if (b) grid = new Uint16Array(b); })
        .catch(function () {});
    function update() {
        pending = 0;
        var r = topo.getBoundingClientRect(), x = last.clientX - r.left, y = last.clientY - r.top;
        hero.style.setProperty('--mx', x + 'px');
        hero.style.setProperty('--my', y + 'px');
        if (!grid) return;
        // The contours are drawn with background-size: cover, centered.
        var s = Math.max(r.width / SW, r.height / SH);
        var gx = Math.floor((x - (r.width - SW * s) / 2) / s / (SW / GW));
        var gy = Math.floor((y - (r.height - SH * s) / 2) / s / (SH / GH));
        if (gx < 0 || gy < 0 || gx >= GW || gy >= GH) return;
        var ft = Math.round(grid[gy * GW + gx] / 10) * 10;
        readout.textContent = ft.toLocaleString('en-US') + ' ft here';
    }
    hero.addEventListener('pointermove', function (e) {
        if (e.pointerType !== 'mouse') return;
        last = e;
        hero.classList.add('is-pointing');
        if (!pending) pending = requestAnimationFrame(update);
    });
    hero.addEventListener('pointerleave', function () {
        hero.classList.remove('is-pointing');
        readout.textContent = idle;
    });
})();
