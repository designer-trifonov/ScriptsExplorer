"use strict";
/**
 * Единственный источник правды: какие методы считаются Unity
 * lifecycle-методами — порт data/lifecycle.py.
 */
const LIFECYCLE_METHODS = new Set(["Awake", "Start", "OnEnable"]);

module.exports = { LIFECYCLE_METHODS };
