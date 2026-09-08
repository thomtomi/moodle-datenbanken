/* Eingabehilfen; Speicherung, Berechtigungen und Pflichtfeldprüfung bleiben bei Moodle. */
(function () {
    'use strict';
    function enhanceEntry() {
        document.querySelectorAll('.ha-db.ha-entry .ha-control').forEach(function (wrapper) {
            var control = wrapper.querySelector('input[type="text"], textarea');
            if (!control || control.dataset.haReady === 'true') {
                return;
            }
            if (wrapper.closest('[data-ha-field="question"]') && control.tagName === 'INPUT') {
                var multiline = document.createElement('textarea');
                Array.from(control.attributes).forEach(function (attribute) {
                    if (attribute.name !== 'type' && attribute.name !== 'value') {
                        multiline.setAttribute(attribute.name, attribute.value);
                    }
                });
                multiline.defaultValue = control.defaultValue;
                multiline.value = control.value;
                multiline.rows = 4;
                control.replaceWith(multiline);
                control = multiline;
            }
            var help = wrapper.getAttribute('data-ha-help');
            if (help && document.getElementById(help)) {
                var describedBy = (control.getAttribute('aria-describedby') || '').split(/\s+/).filter(Boolean);
                if (describedBy.indexOf(help) === -1) {
                    describedBy.push(help);
                }
                control.setAttribute('aria-describedby', describedBy.join(' '));
            }
            control.setAttribute('aria-required', 'true');
            control.required = true;
            control.dataset.haReady = 'true';
        });
    }
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', enhanceEntry, {once: true});
    } else {
        enhanceEntry();
    }
}());
