<?php
    $report_content = file_get_contents(getenv('REPORT_JSON_PATH'));
    $report = json_decode($report_content, true);

    $user = $_SERVER['PHP_AUTH_USER'];
    if (empty($user) || getenv("ALL_ADMINS") == "1") {
        $is_admin = true;
    }
    else {
        $admins = explode(',', getenv('ADMIN_USERS'));
        $is_admin = in_array($user, $admins);
    }
?>

<html>
<head>
<meta charset="UTF-8">
</head>
<body>

<h1>Manual annotation report</h1>

<p>This is an automatic report concerning the genes that were manually annotated.</p>

<p>This report is updated every night, and the present report have been generated on: <b><?php echo $report['time'] ?></b> (Paris, France time).</p>


<?php if (count($report['wa_errors']) > 0 && $is_admin): ?>

    <h2>Found <?php echo count($report['wa_errors']); ?> unexpected errors in the gff produced by WebApollo:</h2><ul>
    <?php foreach ($report['wa_errors'] as $e): ?>
        <li><?php echo $e; ?></li>
    <?php endforeach; ?>
    </ul>
<?php endif; ?>


<?php
if ($is_admin) {
    $users_to_show = $report['genes_by_users'];
}
else {
    $users_to_show = [$user => $report['genes_by_users'][$user]];
}
?>


<?php foreach ($users_to_show as $u => $data): ?>
    <h3><?php echo $u ?></h3>

    <?php if (count($data['errors']) > 0): ?>
        <p>The following <?php echo count($data['errors']) ?> <b>errors</b> were found (blocking):</p><ul>
        <?php foreach ($data['errors'] as $e): ?>
            <li><?php echo $e ?></li>
        <?php endforeach; ?>
        </ul>
    <?php endif; ?>

    <?php if (count($data['warnings']) > 0): ?>
        <p>The following <?php echo count($data['warnings']) ?> <b>warnings</b> were found (non blocking, potential issues):</p><ul>
        <?php foreach ($data['warnings'] as $w): ?>
            <li><?php echo $w ?></li>
        <?php endforeach; ?>
        </ul>
    <?php endif; ?>

    <?php if (count($data['ok']) > 0): ?>
        <p>The following <?php echo count($data['ok']) ?> genes are <b>valid</b>:</p><ul>
        <?php foreach ($data['ok'] as $o): ?>
            <li><?php echo $o ?></li>
        <?php endforeach; ?>
        </ul>
    <?php endif; ?>
<?php endforeach; ?>


<?php if ($is_admin && (getenv("DETAILED_REPORT") == "1")): ?>
    <h2>Splitted genes:</h2><ul>

    <?php foreach ($report['splitted'] as $gene => $parts): ?>
        <li><?php echo $gene ?>: <?php echo join(', ', $parts) ?></li>
    <?php endforeach; ?>
    </ul>


    <h2>Parts repartition:</h2><ul>
    <?php foreach ($report['parts'] as $p_name => $p_num): ?>
        <li><?php echo $p_name ?>: <?php echo $p_num ?></li>
    <?php endforeach; ?>
    </ul>


    <h2>Duplicated genes:</h2><ul>
    <?php foreach ($report['duplicated'] as $gene => $alleles): ?>
        <li><?php echo $gene ?>: <?php echo join(', ', $alleles) ?></li>
    <?php endforeach; ?>
    </ul>


    <h2>Alleles repartition:</h2><ul>
    <?php foreach ($report['alleles'] as $a_name => $a_num): ?>
        <li><?php echo $a_name ?>: <?php echo $a_num ?></li>
    <?php endforeach; ?>
    </ul>
<?php endif; ?>

<?php if ($is_admin): ?>
    <?php if (getenv("ANNOTATION_GROUPS") == "1"): ?>
        <h2>Group repartition:</h2><ul>
        <?php foreach ($report['groups'] as $g_name => $g_num): ?>
            <li><?php echo $g_name ?>: <?php echo $g_num ?> genes</li>
        <?php endforeach; ?>
        </ul>
    <?php endif; ?>




    <h2>User repartition:</h2><ul>
    <?php foreach ($report['genes_by_users'] as $u => $data): ?>
        <li><?php echo $u ?>: <?php echo $data['num_genes'] ?> annotated genes (<?php echo count($data['ok']) ?> valid genes, <?php echo $data['num_genes'] - count($data['ok']) ?> invalid genes, <?php echo count($data['warnings']) ?> warnings, <?php echo count($data['errors']) ?> issues)</li>
    <?php endforeach; ?>
    </ul>




    <h2>General stats:</h2>
    <p><?php echo $report['global_stats']['goid']; ?> genes have at least one goid</p>

    <p></p>
    <p>Found <?php echo $report['global_stats']['total_genes']; ?> genes (<?php echo $report['global_stats']['genes_ok']; ?> valid genes, <?php echo $report['global_stats']['total_genes'] - $report['global_stats']['genes_ok']; ?> invalid genes, <?php echo $report['global_stats']['total_warnings']; ?> warnings, <?php echo $report['global_stats']['total_errors']; ?> issues)</p><ul>
          <li><?php echo $report['global_stats']['genes_seen_once']; ?> genes with only 1 allele and 1 part</li>
          <li><?php echo count($report['duplicated']); ?> genes (or parts of genes) with multiple alleles</li>
          <li><?php echo count($report['splitted']); ?> genes (or alleles) with multiple parts</li>
    </ul>
<?php endif; ?>

</body>
</html>
