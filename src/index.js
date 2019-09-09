'use strict';

var Elm = require("./elm/Main.elm").Elm;

var app = Elm.Main.init({
  node: document.getElementById("container")
});
