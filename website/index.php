<html>
  <head>
    <title>Chat-Pacha</title>
    <style>
      #antichat-info {
        font-weight: bold;
        margin-block-start: 1em;
        margin-block-end: 1em;
      }
      .date-info {
        font-weight: bold;
        margin-block-start: 1em;
        margin-block-end: 1em;
      }
      .progress-bar-outside {
        display: inline-block;
        background-color: #A00000;
        width: 150px;
      }
      .progress-bar-outside .score1 {
        float: right;
        font-weight: bold;
        color: #eaeaea;
      }
      .progress-bar-inside {
        display: inline-block;
        background-color: #00A000;
      }
      .progress-bar-inside .score0 {
        font-weight: bold;
      }
      .class-icon {
        visibility: hidden;
        padding: 2px;
      }
      .class-icon.training-result {
        visibility: visible;
      }
      .class-icon.selected {
        border-style: solid;
        border-color: red;
      }
      .class-icon.selectable {
        visibility: visible;
        cursor: pointer;
      }
      .class-icon.selectable.training-result {
        text-decoration: underline;
        text-decoration-thickness: 3px;
      }
    </style>
  </head>
  <body>
<?php
  require "tools.php";

  function printIcon($class_id, $file_json, $page) {
    print("<span id='".$file_json["name"]."-icon-".$class_id."' class='class-icon ");
    if ($file_json["class"] == $class_id) {
      print("training-result ");
    }
    if ($page->isAdmin() && !array_key_exists("tests", $_GET)) {
      if (array_key_exists("action", $file_json) && $file_json["action"] == $class_id) {
        print("selected");
      }
      print(" selectable' onclick='onSetAction(\"".$file_json["name"]."\", \"".$class_id."\")");
      print("'");
    } else {
      print("'");
    }
    print(">".$page->getClasses()[$class_id]["icon"]."</span> ");
  }

  function printProgressBar($file_json, $class_ids, $page) {
    print("<div>");
    printIcon($class_ids[0], $file_json, $page);
    print("<span class='progress-bar-outside'>");
    if ($file_json["class"] == $class_ids[0]) {
      $score0 = $file_json["score"];
    } else {
      $score0 = 1 - $file_json["score"];
    }
    $score1 = 1 - $score0;
    print("<span class='progress-bar-inside' style='width: ".($score0 * 100)."%'>&nbsp;");
    if ($file_json["class"] == $class_ids[0]) {
      print("<span class='score0'>".intval($score0 * 100)."%</span>");
    }
    print("</span>");
    if ($file_json["class"] == $class_ids[1]) {
      print("<span class='score1'>".intval($score1 * 100)."%</span>");
    }
    print("</span> ");
    printIcon($class_ids[1], $file_json, $page);
    print("</div>");
  }

  function printAllImages($day_category, $page) {
    $class_ids = array_keys($page->getClasses());
    $previous_day = "";
    foreach ($page->getIncomingImageJSON() as $key => $file_json) {
      $date = new DateTime();
      $date->setTimestamp($file_json["timestamp"]);
      $day = $date->format('d/m/Y');
      if ($day_category && $previous_day != $day) {
        print("<hr/>");
        $previous_day = $day;
        print("<div class='date-info'>".$day."</div>");
      }
      $class = $page->getClasses()[$file_json["class"]];
      print("<table border='0' style='display: inline-table'><tr><td colspan='2'>");
      print("<a href='".$file_json["image_path"]."'>");
      print("<img src='".$file_json["thumbnail_path"]."' width='320' height='180'/>");
      print("</a>");
      print("</td></tr>");
      print("<tr>");
      print("<td>");
      print("<b>".$date->format('H:i:s')."</b>");
      print("</td><td>");
      printProgressBar($file_json, $class_ids, $page);
      print("</td>");
      print("</table>\n");
    }
  }
?>
    <script>
      var actions = {
<?php
  foreach ($page->getIncomingImageJSON() as $_ => $json) {
    if (array_key_exists("action", $json)) {
      print("'".$json["name"]."': '".$json["action"]."',\n");
    }
  }
?>
      };

      function onSetAction(image_name, action) {
        if (actions[image_name] == action) {
          action = "";
        }
        var xhr = new XMLHttpRequest();
        xhr.open("GET", "action.php?imagename=" + image_name + "&action=" + action, true);
        xhr.send();
        actions[image_name] = action;
        if (action == "chat") {
          document.getElementById(image_name + "-icon-chat").classList.add("selected");
          document.getElementById(image_name + "-icon-pas_chat").classList.remove("selected");
        } else if (action == "pas_chat") {
          document.getElementById(image_name + "-icon-chat").classList.remove("selected");
          document.getElementById(image_name + "-icon-pas_chat").classList.add("selected");
        } else {
          document.getElementById(image_name + "-icon-chat").classList.remove("selected");
          document.getElementById(image_name + "-icon-pas_chat").classList.remove("selected");
        }
      }
    </script>
<?php
  print(mainMenu($page));
  print("<div>");
  print("<span id='antichat-info'>Images: ");
  print(count($page->getIncomingImageJSON()));
  print("</span>");
  print("</div>");
  printAllImages(!array_key_exists("class", $_GET), $page);
?>
  </body>
</html>
