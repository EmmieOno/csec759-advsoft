<?php
define("DVWA_WEB_PAGE_TO_ROOT", "./");
require_once __DIR__ . "/dvwa/includes/dvwaPage.inc.php";
dvwaPageStartup(array("authenticated"));
mysqli_report(MYSQLI_REPORT_OFF);
dvwaDatabaseConnect();
?>
<!doctype html>
<html>
<body>
<form method="GET">
  <label>User ID: <input type="text" name="id"></label>
  <input type="submit" name="Submit" value="Submit">
</form>
<?php
// N1: SAFE case. Raw input is reflected as escaped text; only an int cast reaches SQL.
if (isset($_GET['Submit'])) {
    $raw = $_GET['id'] ?? '';
    if (!is_string($raw) || strlen($raw) > 128) {
        echo '<pre>INPUT REJECTED</pre>';
        exit;
    }
    echo '<pre>You searched for: ' . htmlspecialchars($raw, ENT_QUOTES) . '</pre>';

    $id = (int)$raw;   // payload text never enters the query
    $query = "SELECT first_name, last_name FROM users WHERE user_id = $id";
    $db = $GLOBALS["___mysqli_ston"];
    $result = mysqli_query($db, $query);
    if ($result === false) {
        echo '<pre>DB ERROR ' . mysqli_errno($db) . '</pre';
    } else {
        echo '<pre>ROWS=' . mysqli_num_rows($result) . '</pre>';
        mysqli_free_result($result);
    }
}
?>
</body>
</html>
