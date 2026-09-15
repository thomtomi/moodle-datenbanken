/* Raumaufteilung als progressive Erweiterung; keine Namen, Bilder oder Uploads verändern. */
(function () {
    'use strict';
    var maxRows = 8;
    var maxPlaces = 16;

    function initialise(root) {
        if (root.dataset.spReady === 'true') {
            return;
        }
        var isEditor = root.classList.contains('sp-add');
        var warning = root.querySelector('.sp-layout-warning');
        var status = root.querySelector('.sp-layout-status');
        var config = root.querySelectorAll('[data-sp-config]');
        var rows = root.querySelectorAll('[data-sp-row]');
        if (!warning || !status || config.length !== 9 || rows.length !== maxRows) {
            return; // Fehlende Vorlagenteile: Vollansicht und sichtbarer Hinweis bleiben erhalten.
        }

        function read(key, maximum, fallback) {
            var holder = root.querySelector('[data-sp-config="' + key + '"]');
            if (!holder) {
                return null;
            }
            var select = holder.querySelector('select');
            if (isEditor && !select) {
                return null;
            }
            var raw = (select ? select.value : holder.textContent).trim();
            if (raw === '') {
                return fallback;
            }
            if (!/^\d{1,2}$/.test(raw)) {
                return null;
            }
            var number = Number(raw);
            return number >= 1 && number <= maximum ? number : null;
        }

        function update() {
            var rowCount = read('rows', maxRows, 3);
            var places = [];
            for (var r = 1; r <= maxRows; r++) {
                places.push(read('row-' + r, maxPlaces, 7));
            }
            if (rowCount === null || places.indexOf(null) !== -1) {
                rows.forEach(function (row) { row.hidden = false; });
                root.querySelectorAll('[data-sp-place], [data-sp-config]').forEach(function (node) { node.hidden = false; });
                root.style.removeProperty('--sp-columns');
                root.style.removeProperty('--sp-min-width');
                warning.textContent = 'Raumaufteilung unvollständig oder ungültig. Alle 128 möglichen Plätze werden angezeigt. Prüfen Sie Reihen (1–8) und Tische (1–16) in der Bearbeitung.';
                warning.hidden = false;
                status.textContent = '';
                return;
            }
            var columns = Math.max.apply(null, places.slice(0, rowCount));
            root.style.setProperty('--sp-columns', String(columns));
            root.style.setProperty('--sp-min-width', String(Math.max(24, columns * 8)) + 'rem');
            rows.forEach(function (row) {
                var number = Number(row.dataset.spRow);
                row.hidden = number > rowCount;
                row.querySelectorAll('[data-sp-place]').forEach(function (seat) {
                    seat.hidden = Number(seat.dataset.spPlace) > places[number - 1];
                });
            });
            // Die ausgeblendeten Originalfelder bleiben aktiv im Moodle-Formular.
            // Weder value/disabled noch Datei-IDs werden verändert oder entfernt.
            if (isEditor) {
                for (var r = 1; r <= maxRows; r++) {
                    root.querySelector('[data-sp-config="row-' + r + '"]').hidden = r > rowCount;
                }
            }
            var total = places.slice(0, rowCount).reduce(function (sum, count) { return sum + count; }, 0);
            status.textContent = rowCount + (rowCount === 1 ? ' Reihe' : ' Reihen') + ' · ' + total + (total === 1 ? ' Tisch' : ' Tische') + ' · Lehrpersonensicht';
            warning.hidden = true;
        }

        if (isEditor) {
            config.forEach(function (holder) {
                var select = holder.querySelector('select');
                if (select) {
                    // Nur leere Raumgrössen vorbelegen; Sitzplatzinhalte bleiben unberührt.
                    if (select.value === '') {
                        select.value = holder.dataset.spConfig === 'rows' ? '3' : '7';
                    }
                    select.addEventListener('change', update);
                }
            });
            var form = root.closest('form');
            if (form) {
                form.addEventListener('reset', function () { window.setTimeout(update, 0); });
            }
        }
        root.dataset.spReady = 'true';
        update();
    }

    function start() {
        document.querySelectorAll('.sp-db.sp-single, .sp-db.sp-add').forEach(initialise);
    }
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', start, {once: true});
    } else {
        start();
    }
    window.addEventListener('pageshow', start);
}());
