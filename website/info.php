<html>
  <body>
<?php
  $string = file_get_contents("training/data.json");
  $json = json_decode($string, true);
?>
    <div><b>Data set</b></div>
    <br/>
    <table>
      <tr>
        <td>Chat&nbsp;</td><td style="text-align:right"><span class="local-number"><?php print($json["picture_count"]["chat"]); ?></span></td>
      </tr>
      <tr>
        <td>Pas chat&nbsp;</td><td style="text-align:right"><span class="local-number"><?php print($json["picture_count"]["pas_chat"]); ?></span></td>
      </tr>
      <tr>
        <td>Total&nbsp;</td><td style="text-align:right"><span class="local-number"><?php print($json["picture_count"]["pas_chat"] + $json["picture_count"]["chat"]); ?></span></td>
      </tr>
      <tr>
        <td>Image size&nbsp;</td><td style="text-align:right"><?php print($json["image_size"][0]."x".$json["image_size"][1]); ?></td>
      </tr>
    </table>
    <hr/>
    <div><b>Training</b></div>
    <br/>
    <table>
      <tr>
        <td>Training images&nbsp;</td><td style="text-align:right"><span class="local-number"><?php print($json["picture_count"]["traning"]); ?></span></td>
      </tr>
      <tr>
        <td>Validation images&nbsp;</td><td style="text-align:right"><span class="local-number"><?php print($json["picture_count"]["validation"]); ?></span></td>
      </tr>
      <tr>
        <td>Total&nbsp;</td><td style="text-align:right"><?php print(gmdate("H\\h i\\m s\\s", intval($json["total_time"]))); ?></td>
      </tr>
      <tr>
        <td>Loading&nbsp;</td><td style="text-align:right"><?php print(gmdate("H\\h i\\m s\\s", intval($json["loading_time"]))); ?></td>
      </tr>
      <tr>
        <td>Processing&nbsp;</td><td style="text-align:right"><?php print(gmdate("H\\h i\\m s\\s", intval($json["processing_time"]))); ?></td>
      </tr>
      <tr>
        <td>Compiling&nbsp;</td><td style="text-align:right"><?php print(gmdate("H\\h i\\m s\\s", intval($json["compiling_time"]))); ?></td>
      </tr>
      <tr>
        <td>Training&nbsp;</td><td style="text-align:right"><?php print(gmdate("H\\h i\\m s\\s", intval($json["training_time"]))); ?></td>
      </tr>
    </table>
    <br/>
    <code>
      <?php print(nl2br($json["model_summary"])); ?>
    </code>
    <img src="training/training.png" />
<script>
var array = document.getElementsByClassName("local-number");
for (element of array) {
  element.innerHTML = parseFloat(element.innerHTML).toLocaleString();
}
</script>
  </body>
</html>
