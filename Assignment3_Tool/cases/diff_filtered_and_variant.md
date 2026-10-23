
- There is no content differences between these files. However, a3_variant.php was intially going to change the SQL query from
WHERE user_id = $user_id to WHERE user_id > $user_id. But this variant was decided against. When running the actual variant
(changing AND to OR) a3_variant.php was still used but with the = not the >. It was already loaded into the script and I did not change
it before running the variation trials.
