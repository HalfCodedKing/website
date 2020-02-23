<html>
<body>

<?php 

if ($_GET["value"] == "on" || $_GET["value"] == "off") {
    $jsonString = file_get_contents('data.json');
    $data = json_decode($jsonString, true);
    $data["lights"] = $_GET['value'];
    $newJsonString = json_encode($data);
    file_put_contents('data.json', $newJsonString);
}
header("Location: index.html");

/*$jsonString = file_get_contents('accounts.json');
$data = json_decode($jsonString, true);
$account = array("username" => $_POST["username"], "password" => $_POST["password"], "id" => count($data)+1);
$data[] = $account;
$newJsonString = json_encode($data);
file_put_contents('accounts.json', $newJsonString); */
?>

</body>
</html>