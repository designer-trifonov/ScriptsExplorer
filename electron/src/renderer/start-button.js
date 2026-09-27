"use strict";
const pill = document.getElementById("pill");

// Сообщаем реальную ширину пилюли главному процессу — он выставит точный
// размер окна (аналог _pill_width() в ui/start_button.py, который считал
// ширину через QFontMetrics ещё до создания окна).
window.startButton.reportWidth(Math.ceil(pill.getBoundingClientRect().width));

pill.addEventListener("click", () => window.startButton.clicked());
