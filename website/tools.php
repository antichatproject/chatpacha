<?php

  class Page {
    function isAdmin() {
      return strcasecmp($_SERVER['PHP_AUTH_USER'], "antichat") == 0;
    }

    function isURL($document) {
      $document = addPHPExtension($document);
      return strlen($_SERVER["DOCUMENT_URI"]) >= strlen($document) && substr($_SERVER["DOCUMENT_URI"], -strlen($document)) == $document;
    }

    function getClasses() {
      return array(
        "pas_chat" => array("name" => "Pas chat", "color" => "black", "icon" => "✅"),
        "chat" => array("name" => "Chat", "color" => "red", "icon" => "🐈"),
      );
    }

    function getClassName($string) {
      return $this->getClasses()[$string]["name"];
    }

    function getIncomingDir() {
      if (array_key_exists("tests", $_GET)) {
        return "images/tests/";
      }
      return "images/incoming/";
    }

    function loadIncomingDir() {
      if (property_exists($this, "incoming_info_json")) {
        return;
      }
      $this->incoming_image_json = array();
      $class_filter = $this->selectedClass();
      $this->incoming_classified_count = array("total" => 0);
      $dir = $this->getIncomingDir();
      $cdir = scandir($dir);
      foreach ($cdir as $key => $filename) {
        if (pathinfo($filename, PATHINFO_EXTENSION) == "json") {
          $string = file_get_contents($dir.$filename);
          $json = json_decode($string, true);
          $class = $json["class"];
          if (!array_key_exists($class, $this->incoming_classified_count)) {
            $this->incoming_classified_count[$class] = 0;
          }
          $this->incoming_classified_count[$class] = $this->incoming_classified_count[$class] + 1;
          $this->incoming_classified_count["total"] = $this->incoming_classified_count["total"] + 1;
          if ($class_filter != "" && $class != $class_filter) {
            continue;
          }
          $json["image_path"] = $dir.$json["file"];
          $json["thumbnail_path"] = $dir.$json["thumbnail"];
          if (file_exists($dir.$json["name"].".action")) {
            $action = file_get_contents($dir.$json["name"].".action");
            if (array_key_exists($action, $this->getClasses())) {
              $json["action"] = $action;
            }
          }
          array_push($this->incoming_image_json, $json);
        }
      }
      usort($this->incoming_image_json, build_json_soter($this->selectedClass()));
    }

    function selectedClass() {
      if (array_key_exists("class", $_GET)) {
        return $_GET["class"];
      }
      if ($this->isURL("dataset")) {
        return "chat";
      }
      return "";
    }

    function isClassSelected($string) {
      return $string == $this->selectedClass();
    }

    function getIncomingImageJSON() {
      $this->loadIncomingDir();
      return $this->incoming_image_json;
    }

    function getIncomingClassifiedCount($type) {
      $this->loadIncomingDir();
      return $this->incoming_classified_count[$type];
    }

    function loadTrainingInfo() {
      if (property_exists($this, "training_info")) {
        return;
      }
      $string = file_get_contents("training/data.json");
      $this->training_info = json_decode($string, true);
    }

    function getTrainingInfo() {
      $this->loadTrainingInfo();
      return $this->training_info;
    }

    function getTrainingClassPictureCount($string) {
      $this->loadTrainingInfo();
      return $this->training_info["picture_count"]["dataset"][$string];
    }

  }

  $page = new Page;

  function addPHPExtension($document) {
    $php_extension = ".php";
    if (strlen($document) < strlen($php_extension) || substr($document, -strlen($php_extension)) != $php_extension) {
      $document = $document.$php_extension;
    }
    return $document;
  }

  function menuWithLink($title, $url, $on_url) {
    if ($on_url) {
      return $title;
    } else {
      return "<a href='".$url."'>".$title."</a>";
    }
  }

  function incomingSubmenu($page) {
    $sub_menu = "<div>";
    $sub_menu = $sub_menu.menuWithLink("All ".$page->getIncomingClassifiedCount("total"), "index.php", $page->isClassSelected(""));
    $sub_menu = $sub_menu." | ";
    $sub_menu = $sub_menu.menuWithLink($page->getClassName("chat")." ".$page->getIncomingClassifiedCount("chat"), "index.php?class=chat", $page->isClassSelected("chat"));
    $sub_menu = $sub_menu." | ";
    $sub_menu = $sub_menu.menuWithLink($page->getClassName("pas_chat")." ".$page->getIncomingClassifiedCount("pas_chat"), "index.php?class=pas_chat", $page->isClassSelected("pas_chat"));
    $sub_menu = $sub_menu."</div>";
    return $sub_menu;
  }

  function classifiedSubmenu($page) {
    $sub_menu = "<div>";
    $sub_menu = $sub_menu.menuWithLink($page->getClassName("chat")." ".$page->getTrainingClassPictureCount("chat"), "dataset.php?class=chat", $page->isClassSelected("chat"));
    $sub_menu = $sub_menu." | ";
    $sub_menu = $sub_menu.menuWithLink($page->getClassName("pas_chat")." ".$page->getTrainingClassPictureCount("pas_chat"), "dataset.php?class=pas_chat", $page->isClassSelected("pas_chat"));
    $sub_menu = $sub_menu."</div>";
    return $sub_menu;
  }

  function mainMenu($page) {
    $result = "<div><b>";
    $sub_menu = "";
    $result = $result.menuWithLink("Incoming", "index.php", $page->isURL("index"));
    if ($page->isURL("index")) {
      $sub_menu = incomingSubmenu($page);
    }
    $result = $result." | ";
    $result = $result.menuWithLink("Dataset", "dataset.php", $page->isURL("dataset"));
    if ($page->isURL("dataset")) {
      $sub_menu = classifiedSubmenu($page);
    }
    $result = $result." | ";
    if ($page->isURL("info")) {
      $result = $result."Info";
    } else {
      $result = $result."<a href='info.php'>Info</a>";
    }
    $result = $result."</b></div>";
    if ($sub_menu != "") {
      $result = $result."<br/>".$sub_menu;
    }
    $result = $result."<br/>";
    return $result;
  }

  function compare_score($a, $b) {
    if ($a == $b) {
        return 0;
    }
    return ($a < $b) ? -1 : 1;
  }

  function build_json_soter($sort_class) {
    return function ($a, $b) use($sort_class) {
      if ($sort_class == "chat") {
        return compare_score($a["score"], $b["score"]);
      } elseif ($sort_class == "pas_chat") {
        return compare_score($a["score"], $b["score"]);
      } else {
        return strcmp($b["timestamp"], $a["timestamp"]);
      }
    };
  }
?>