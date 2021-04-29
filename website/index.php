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
  $classes = array(
      "pas_chat" => array("name" => "Pas chat", "color" => "black", "icon" => "✅"),
      "chat" => array("name" => "Chat", "color" => "red", "icon" => "🐈"),
  );

  function printIcon($class_id, $file_json, $classes) {
    print("<span id='".$file_json["name"]."-icon-".$class_id."' class='class-icon ");
    if ($file_json["class"] == $class_id) {
      print("training-result ");
    }
    if ($_SERVER['PHP_AUTH_USER'] == "antichat") {
      if (array_key_exists("action", $file_json) && $file_json["action"] == $class_id) {
        print("selected");
      }
      print(" selectable' onclick='onSetAction(\"".$file_json["name"]."\", \"".$class_id."\")");
      print("'");
    } else {
      print("'");
    }
    print(">".$classes[$class_id]["icon"]."</span> ");
  }

  function printProgressBar($file_json, $classes, $class_ids) {
    print("<div>");
    printIcon($class_ids[0], $file_json, $classes);
    print("<span class='progress-bar-outside'>");
    if ($file_json["class"] == $class_ids[0]) {
      $score0 = $file_json["score"];
    } else {
      $score0 = 100 - $file_json["score"];
    }
    $score1 = 100 - $score0;
    print("<span class='progress-bar-inside' style='width: ".$score0."%'>&nbsp;");
    if ($file_json["class"] == $class_ids[0]) {
      print("<span class='score0'>".intval($score0)."%</span>");
    }
    print("</span>");
    if ($file_json["class"] == $class_ids[1]) {
      print("<span class='score1'>".intval($score1)."%</span>");
    }
    print("</span> ");
    printIcon($class_ids[1], $file_json, $classes);
    print("</div>");
  }

  function printAllImages($all_json, $classes) {
    $class_ids = array_keys($classes);
    $previous_day = "";
    foreach ($all_json as $key => $file_json) {
      $date = new DateTime();
      $date->setTimestamp($file_json["timestamp"]);
      $day = $date->format('d/m/Y');
      if ($previous_day != $day) {
        print("<hr/>");
        $previous_day = $day;
        print("<div class='date-info'>".$day."</div>");
      }
      $class = $classes[$file_json["class"]];
      print("<table border='0' style='display: inline-table'><tr><td colspan='2'>");
      print("<a href='".$file_json["image_path"]."'>");
      print("<img src='".$file_json["thumbnail_path"]."'/>");
      print("</a>");
      print("</td></tr>");
      print("<tr>");
        print("<td>");
        print("<b>".$date->format('H:i:s')."</b>");
        print("</td><td>");
        printProgressBar($file_json, $classes, $class_ids);
        print("</td>");
      print("</table>\n");
    }
  }

  function compare_json($a, $b) {
    return strcmp($b["timestamp"], $a["timestamp"]);
  }

  function load_all_json($classes, $dir) {
    $cdir = scandir($dir);
    $all_json = array();
    if (array_key_exists("class", $_GET)) {
      $class_filter = $_GET["class"];
    } else {
      $class_filter = "";
    }
    $class_counter = array("total" => 0);
    foreach ($cdir as $key => $filename) {
      if (pathinfo($filename, PATHINFO_EXTENSION) == "json") {
        $string = file_get_contents($dir.$filename);
        $json = json_decode($string, true);
        $class = $json["class"];
        if (!array_key_exists($class, $class_counter)) {
          $class_counter[$class] = 0;
        }
        $class_counter[$class] = $class_counter[$class] + 1;
        $class_counter["total"] = $class_counter["total"] + 1;
        if ($class_filter != "" && $class != $class_filter) {
          continue;
        }
        $json["image_path"] = $dir.$json["file"];
        $json["thumbnail_path"] = $dir.$json["thumbnail"];
        if (file_exists($dir.$json["name"].".action")) {
          $action = file_get_contents($dir.$json["name"].".action");
          if (array_key_exists($action, $classes)) {
            $json["action"] = $action;
          }
        }
        array_push($all_json, $json);
      }
    }
    usort($all_json, "compare_json");
    return [$class_counter, $all_json];
  }
  [$class_counter, $all_json] = load_all_json($classes, "images/incoming/");
?>
    <script>
      var actions = {
<?php
  foreach ($all_json as $_ => $json) {
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
  print("<div>");
  print("<a href='index.php'>All ".$class_counter["total"]."</a> | ");
  print("<a href='index.php?class=chat'>Chat ".$class_counter["chat"]."</a> | ");
  print("<a href='index.php?class=pas_chat'>Pas chat ".$class_counter["pas_chat"]."</a> | ");
  print("<a href='info.php'>Info</a>");
  print("</div><br/>");
  print("<div>");
  print("<span id='antichat-info'>Images: ");
  print(count($all_json));
  print("</span>");
  print("</div>");
  printAllImages($all_json, $classes);
?>
  </body>
</html>
