<?php
  require "tools.php";

  if (isAdmin()) {
    $image_name = basename(stripslashes($_GET["imagename"]));
    $action_path = "images/incoming/".$image_name.".action";
    file_put_contents($action_path, $_GET["action"]);
  }
?>