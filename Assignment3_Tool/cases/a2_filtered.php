<?php
define('DVWA_WEB_PAGE_TO_ROOT', './');
require_once __DIR__ . '/dvwa/includes/dvwaPage.inc.php';
dvwaPageStartup(array('authenticated'));

$filterEnabled = true;

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
if (isset($_GET['Submit'])) {
    $id = $_GET['id'] ?? '';

    if (!is_string($id) || strlen($id) > 128) {
        echo '<pre>INPUT REJECTED</pre>';
        exit;
    }

    // Intentionally flawed filter: permits Boolean SQL expressions.
    $pattern = '/\A[0-9]{1,6}(?:[ \t]+(?:AND|OR)[ \t]+[0-9]{1,6}[ \t]*=[ \t]*[0-9]{1,6})*\z/i';

    if ($filterEnabled && !preg_match($pattern, $id)) {
        echo '<pre>INPUT REJECTED</pre>';
        exit;
    }

    // Intentionally vulnerable numeric SQL context.
    $query = "SELECT first_name, last_name FROM users WHERE user_id = $id";
    $db = $GLOBALS["___mysqli_ston"];
    $result = mysqli_query($db, $query);

    if ($result === false) {
        echo '<pre>DB ERROR ' . mysqli_errno($db) . '</pre>';
    } else {
        echo '<pre>ROWS=' . mysqli_num_rows($result) . '</pre>';
        mysqli_free_result($result);
    }
}
?>
</body>
</html>
