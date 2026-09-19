(function () {
  "use strict";

  function markStatuses() {
    document
      .querySelectorAll(".ss-db [data-ss-status]")
      .forEach(function (status) {
        var value = status.textContent.trim();
        status.classList.remove("is-complete", "is-pending");
        if (value === "Alle Zertifikate abgegeben") {
          status.classList.add("is-complete");
        } else if (value === "Nicht alle Zertifikate abgegeben") {
          status.classList.add("is-pending");
        }
      });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", markStatuses);
  } else {
    markStatuses();
  }
})();
