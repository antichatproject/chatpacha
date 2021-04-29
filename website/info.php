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
        <td>Chat</td><td><?php print($json["chat_count"]); ?></td>
      </tr>
      <tr>
        <td>Pas chat</td><td><?php print($json["pas_chat_count"]); ?></td>
      </tr>
      <tr>
        <td>Total</td><td><?php print($json["pas_chat_count"] + $json["chat_count"]); ?></td>
      </tr>
      <tr>
        <td>Image size</td><td><?php print($json["image_size"][0]."x".$json["image_size"][1]); ?></td>
      </tr>
    </table>
    <hr/>
    <div><b>Training</b></div>
    <br/>
    <table>
      <tr>
        <td>Training images</td><td><?php print($json["traning_count"]); ?></td>
      </tr>
      <tr>
        <td>Validation images</td><td><?php print($json["validation_count"]); ?></td>
      </tr>
      <tr>
        <td>Total</td><td><?php print(gmdate("H\\h i\\m s\\s", intval($json["total_time"]))); ?></td>
      </tr>
      <tr>
        <td>Loading</td><td><?php print(gmdate("H\\h i\\m s\\s", intval($json["loading_time"]))); ?></td>
      </tr>
      <tr>
        <td>Processing</td><td><?php print(gmdate("H\\h i\\m s\\s", intval($json["processing_time"]))); ?></td>
      </tr>
      <tr>
        <td>Compiling</td><td><?php print(gmdate("H\\h i\\m s\\s", intval($json["compiling_time"]))); ?></td>
      </tr>
      <tr>
        <td>Training</td><td><?php print(gmdate("H\\h i\\m s\\s", intval($json["training_time"]))); ?></td>
      </tr>
    </table>
    <br/>
    <code>
      <?php print(nl2br($json["model_summary"])); ?>
    </code>
    <img src="training/training.png" />
  </body>
</html>
