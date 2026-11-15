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
<form method="POST">
  <label>User ID: <input type="text" name="id"></label>
  <input type="submit" name="Submit" value="Submit">
</form>
<?php
// N3b: MODIFIED REAL CASE. Logic copied from DVWA medium SQLi
// (mysqli_real_escape_string + numeric context). Changes vs. stock DVWA:
//   1) the mysqli_error() text is NOT printed (stock: or die(mysqli_error(...)))
//   2) output is ROWS=n so the existing parser works
//   3) free-text input instead of the <select> dropdown
if (isset($_POST['Submit'])) {
    $db = $GLOBALS["___mysqli_ston"];
    $id = $_POST['id'] ?? '';
    $id = mysqli_real_escape_string($db, $id);

    $query = "SELECT first_name, last_name FROM users WHERE user_id = $id;";
    $result = mysqli_query($db, $query);
    if ($result === false) {
        echo '<pre>DB ERROR</pre>';
    } else {
        echo '<pre>ROWS=' . mysqli_num_rows($result) . '</pre>';
        mysqli_free_result($result);
    }
}
?>
</body>
</html>
