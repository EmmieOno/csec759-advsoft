<?php

define('DVWA_WEB_PAGE_TO_ROOT', './');

require_once __DIR__ . '/dvwa/includes/dvwaPage.inc.php';

dvwaPageStartup(array('authenticated'));

 

// Additional variant of cases/boolean-oracle/a2_filtered.php.

// ONLY CHANGE FROM a2_filtered.php: request method GET -> POST

// (form method + $_GET -> $_POST). Filter logic, query construction,

// and all other behavior are identical to a2_filtered.php.

$filterEnabled = true;

 

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

if (isset($_POST['Submit'])) {

    $id = $_POST['id'] ?? '';

 

    if (!is_string($id) || strlen($id) > 128) {

        echo '<pre>INPUT REJECTED</pre>';

        exit;

    }

 

    // Identical filter to a2_filtered.php: permits Boolean SQL expressions,

    // rejects everything else (including SQLiFuzz's special-character set).

 
    $pattern = '/\A[0-9]{1,6}(?:[ \t]+(?:AND|OR)[ \t]+[0-9]{1,6}[ \t]*=[ \t]*[0-9]{1,6})*\z/i';

 

    if ($filterEnabled && !preg_match($pattern, $id)) {

        echo '<pre>INPUT REJECTED</pre>';

        exit;

    }

 

    // Identical vulnerable numeric SQL context to a2_filtered.php.

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
