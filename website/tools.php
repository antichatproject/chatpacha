<?php

  function isAdmin() {
    return strcasecmp($_SERVER['PHP_AUTH_USER'], "antichat") == 0;
  }

  $classes = array(
      "pas_chat" => array("name" => "Pas chat", "color" => "black", "icon" => "✅"),
      "chat" => array("name" => "Chat", "color" => "red", "icon" => "🐈"),
  );

?>