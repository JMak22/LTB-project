(function () {
  "use strict";
  var select = document.getElementById("wt-year");
  var controls = document.getElementById("wt-controls");
  var status = document.getElementById("wt-status");
  if (!select || !controls) { return; }
  var items = document.querySelectorAll("[data-year]");

  function show(id, announce) {
    var found = false;
    for (var i = 0; i < select.options.length; i++) {
      if (select.options[i].value === id) { found = true; }
    }
    if (!found) { id = select.options[0].value; }
    for (var j = 0; j < items.length; j++) {
      items[j].hidden = items[j].getAttribute("data-year") !== id;
    }
    select.value = id;
    if (announce) {
      status.textContent = "Showing " + select.options[select.selectedIndex].text;
      try { history.replaceState(null, "", "#" + id); } catch (err) { /* ignore */ }
    }
  }

  controls.hidden = false;
  select.addEventListener("change", function () { show(select.value, true); });
  show(window.location.hash.replace("#", ""), false);
})();
