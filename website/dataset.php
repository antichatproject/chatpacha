<html>
  <head>
  </head>
  <body>
<?php
  require "tools.php";

  print(mainMenu($page));

  $page_offset = 0;
  if (array_key_exists("offset", $_GET)) {
    $page_offset = $_GET["offset"];
  }
  if (array_key_exists("class", $_GET)) {
    $class = $_GET["class"];
  } else {
    $class = "";
  }
  if (!array_key_exists($class, $page->getClasses())) {
    $class = array_keys($page->getClasses())[1];
  }
  $page_count = 100;
  $pictures = array();
  $cdir = scandir("images/generated/".$class);
  $counter = 0;
  foreach ($cdir as $key => $filename) {
    $ext = pathinfo($filename, PATHINFO_EXTENSION);
    if ($ext != "jpg") {
      continue;
    }
    $counter += 1;
    if ($counter >= $page_offset && count($pictures) < $page_count) {
      array_push($pictures, $filename);
    }
  }
  print("<div>");
  $page_links = array();
  for ($i = 0; $i < $counter; $i += $page_count) {
    $string = "<span>";
    if ($i != $page_offset) {
      $string = $string."<a href='?class=".$class."&offset=".strval($i)."'>";
    }
    $string = $string."Page ".strval(($i / $page_count) + 1);
    if ($i != $page_offset) {
      $string = $string."</a>";
    }
    $string = $string."</span>";
    array_push($page_links, $string);
  }
  print(implode(" | ", $page_links));
  print("</div><br/>");
  foreach ($pictures as $_ => $filename) {
    print("<a href='images/generated/".$class."/".$filename."'><img src='images/generated/".$class."/thumbnails/".$filename."' /></a>\n");
  }
?>
  </body>
</html>