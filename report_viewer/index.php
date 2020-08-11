<?php
    $report_content = file_get_contents(getenv('REPORT_PATH') . "full_report.json");
    $report_dict = json_decode($report_content, true);

    $user = $_SERVER['PHP_AUTH_USER'];
    if (empty($user) && array_key_exists('HTTP_REMOTE_USER', $_SERVER)) {
      $user = $_SERVER['HTTP_REMOTE_USER'];
    }

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
<link rel="stylesheet" type="text/css" href="style.css">
<script src="script.js"></script>
<title>Manual annotation report</title>
</head>

<body onload="openOrga('<?php echo key($report_dict) ?>')">

<button onclick="getToTop()" id="topButton">Top</button>

<h1>Manual annotation report</h1>

<?php if (empty($report_content)): ?>
      <p>Failed to load report, please come back later.</p>
<?php else: ?>

<p>This is an automatic report concerning the genes that were manually annotated.</p>

<p>This report is updated every night, and the present report has been generated on: <?php echo $report_dict[key($report_dict)]["time"] ?>  (Paris, France time).</p>

<p>The following organisms are available : </p>
<br>
<div class="tab">
    <?php foreach($report_dict as $organism=>$report) {?>
      <?php if (array_key_exists($user, $report['permissions'])  && in_array($organism, $report['permissions'][$user])) { ?>
        <button class="tablinks" id="button-<?php echo $organism?>"  onclick="openOrga('<?php echo $organism ?>')"><?php echo $organism ?></button>
      <?php } ?>
    <?php } ?>
</div>

<?php foreach($report_dict as $organism=>$report) {?>
<?php if (array_key_exists($user, $report['permissions'])  && in_array($organism, $report['permissions'][$user])) { ?>

<?php
if ($is_admin) {
    $users_to_show = $report['genes_by_users'];
}
else {
    $users_to_show = [$user => $report['genes_by_users'][$user]];
}

$org_id = str_replace(' ', '_', $organism);
?>

<div id="<?php echo $organism ?>" class="tabcontent" >
    <h2> General statistics for <?php echo $organism ?></h2>

    <p></p>
    <p>Found <b><?php echo $report['global_stats']['total_genes']; ?> genes</b> (<b><?php echo $report['global_stats']['genes_ok']; ?></b> valid genes, <b><?php echo $report['global_stats']['total_genes'] - $report['global_stats']['genes_ok']; ?></b> invalid genes, <b><?php echo $report['global_stats']['total_warnings']; ?></b> warnings, <b><?php echo $report['global_stats']['total_errors']; ?></b> issues)</p><ul>
          <li><b><?php echo $report['global_stats']['genes_seen_once']; ?></b> genes with only 1 allele and 1 part</li>
          <li><b><?php echo count($report['duplicated']); ?></b> genes (or parts of genes) with multiple alleles</li>
          <li><b><?php echo count($report['splitted']); ?></b> genes (or alleles) with multiple parts</li>
          <li><b><?php echo $report['global_stats']['total_deleted']; ?></b> deleted genes</li>
          <li><b><?php echo $report['global_stats']['goid']; ?></b> genes have at least one goid</li>
    </ul>

    <p>Downloads:</p>
    <ul>
        <li><a href="./report_data/<?php echo $org_id."/raw_apollo.gff"; ?>">Raw GFF3 from Apollo</a></li>
        <li><a href="./report_data/<?php echo $org_id."/valid.gff"; ?>">GFF3 of valid genes</a> (<a href="./report_data/<?php echo $org_id."/valid_transcripts.fa"; ?>">transcripts FASTA</a>, <a href="./report_data/<?php echo $org_id."/valid_cds.fa"; ?>">CDS FASTA</a>, <a href="./report_data/<?php echo $org_id."/valid_proteins.fa"; ?>">proteins FASTA</a>)</li>
        <li><a href="./report_data/<?php echo $org_id."/invalid.gff"; ?>">GFF3 of invalid genes</a></li>
        <li><a href="./report_data/<?php echo $org_id."/deleted.tsv"; ?>">List of genes marked as deleted</a></li>
        <li><a href="./report_data/<?php echo $org_id."/by_groups/"; ?>">GFF3 and FASTA for each groups</a></li>

    <?php if (getenv("ANNOTATION_GROUPS") == "1"): ?>
        <li>Downloads by annotation groups:</li>
        <ul>
        <?php
            foreach ($report['genes_by_groups'] as $group_name => $data) {
                $group_prefix = preg_replace('/[-\s]+/', '-', strtolower(trim(preg_replace('/[^\w\s-]/', '', $group_name))));
                if (file_exists("./report_data/".$org_id."/by_groups/".$group_prefix."_raw.gff")) {
                    echo "<li>".$group_name." -&gt;
                              Raw from Apollo: <a href=\"./report_data/".$org_id."/by_groups/".$group_prefix."_raw.gff\">GFF3</a>
                              <a href=\"./report_data/".$org_id."/by_groups/".$group_prefix."_raw_cds.fa\">CDS</a>
                              <a href=\"./report_data/".$org_id."/by_groups/".$group_prefix."_raw_proteins.fa\">proteins</a>
                              <a href=\"./report_data/".$org_id."/by_groups/".$group_prefix."_raw_transcripts.fa\">transcripts</a>
                              - Valid genes:
                              <a href=\"./report_data/".$org_id."/by_groups/".$group_prefix."_valid.gff\">GFF3</a>
                              <a href=\"./report_data/".$org_id."/by_groups/".$group_prefix."_valid_cds.fa\">CDS</a>
                              <a href=\"./report_data/".$org_id."/by_groups/".$group_prefix."_valid_proteins.fa\">proteins</a>
                              <a href=\"./report_data/".$org_id."/by_groups/".$group_prefix."_valid_transcripts.fa\">transcripts</a>
                          </li>";
                }
            }
        ?>
        </ul>
    <?php endif; ?>
    </ul>

<ul>
<?php if ($is_admin): ?>
    <li><a href="#by_user">Report by users:</a></li>
    <ul>
        <?php foreach ($users_to_show as $u => $data): ?>
            <li><a href="#user-<?php echo $u ?>"><?php echo $u ?></a>:
                <b><?php echo $data['num_genes'] ?></b> genes
               (<font color="green"><?php echo count($data['ok']) ?></font> valid genes,
                <font color="red"><?php echo $data['num_genes'] - count($data['ok']) ?></font> invalid genes,
                <font color="#cc7a00"><?php echo count($data['warnings']) ?></font> warnings,
                <font color="red"><?php echo count($data['errors']) ?></font> issues,
                <b><?php echo count($data['deleted']) ?></b> deleted genes
                )</li>
        <?php endforeach; ?>
    </ul>
<?php else: ?>
    <li><a href="#by_user">Your genes:</a></li>
<?php endif; ?>
<?php if (getenv("ANNOTATION_GROUPS") == "1"): ?>
    <li><a href="#by_group">Report by groups:</a></li>
    <ul>
        <?php foreach ($report['genes_by_groups'] as $group_name => $data): ?>
            <li><a href="#group-<?php echo strtolower(trim(preg_replace('/[^A-Za-z0-9-]+/', '-', $group_name))) ?>"><?php echo $group_name ?></a>:
                <b><?php echo $data['num_genes'] ?></b> genes
                (<b><?php echo count($data['ok']) ?></b> valid genes,
                 <b><?php echo $data['num_genes'] - count($data['ok']) ?></b> invalid genes,
                 <b><?php echo count($data['warnings']) ?></b> warnings,
                 <b><?php echo count($data['errors']) ?></b> issues,
                 )
            </li>
        <?php endforeach; ?>
    </ul>
<?php endif; ?>
<?php if ($is_admin && (getenv("DETAILED_REPORT") == "1")): ?>
    <li><a href="#splitted">Splitted genes</a></li>
    <li><a href="#parts">Parts repartition</a></li>
    <li><a href="#duplicated">Duplicated genes</a></li>
    <li><a href="#alleles">Alleles repartition</a></li>
<?php endif; ?>
<?php if (count($report['wa_errors']) > 0 && $is_admin): ?>
    <li><a href="#unexpected">Unexpected errors </a> : <font color="red"> <?php echo count($report['wa_errors']) ?></font></li>
<?php endif; ?>
</ul>

<?php if ($is_admin): ?>
    <h2 id="by_user">Report by users</h2>
<?php else: ?>
    <h2 id="by_user">Your genes</h2>
<?php endif; ?>
<?php foreach ($users_to_show as $u => $data): ?>
    <h3 id="user-<?php echo $u ?>"><?php echo $u ?></h3>

    <?php if (isset($data)): ?>
        <?php if (count($data['errors']) > 0): ?>
            <p>The following <b><?php echo count($data['errors']) ?> errors</b> were found (blocking):</p><ul>
            <?php foreach ($data['errors'] as $e): ?>
                <li><?php echo $e ?></li>
            <?php endforeach; ?>
            </ul>
        <?php endif; ?>

        <?php if (count($data['warnings']) > 0): ?>
            <p>The following <b><?php echo count($data['warnings']) ?> warnings</b> were found (non blocking, potential issues):</p><ul>
            <?php foreach ($data['warnings'] as $w): ?>
                <li><?php echo $w ?></li>
            <?php endforeach; ?>
            </ul>
        <?php endif; ?>

        <?php if (count($data['ok']) > 0): ?>
            <p>The following <b><?php echo count($data['ok']) ?></b> genes are <b>valid</b>:</p><ul>
            <?php foreach ($data['ok'] as $o): ?>
                <li><?php echo $o ?></li>
            <?php endforeach; ?>
            </ul>
        <?php endif; ?>

        <?php if (count($data['deleted']) > 0): ?>
            <p>The following <b><?php echo count($data['deleted']) ?></b> genes will be <b>deleted</b>:</p><ul>
            <?php foreach ($data['deleted'] as $o): ?>
                <li><?php echo $o ?></li>
            <?php endforeach; ?>
            </ul>
        <?php endif; ?>
    <?php else: ?>
       No gene
    <?php endif; ?>
<?php endforeach; ?>


<?php if (getenv("ANNOTATION_GROUPS") == "1"): ?>
    <h2 id="by_group">Report by groups</h2>
    <?php foreach ($report['genes_by_groups'] as $group_name => $data): ?>
        <h3 id="group-<?php echo strtolower(trim(preg_replace('/[^A-Za-z0-9-]+/', '-', $group_name))) ?>"><?php echo $group_name ?></h3>

        <?php if (count($data['errors']) > 0): ?>
            <p>The following <b><?php echo count($data['errors']) ?> errors</b> were found (blocking):</p><ul>
            <?php foreach ($data['errors'] as $e): ?>
                <li><?php echo $e ?></li>
            <?php endforeach; ?>
            </ul>
        <?php endif; ?>

        <?php if (count($data['warnings']) > 0): ?>
            <p>The following <b><?php echo count($data['warnings']) ?> warnings</b> were found (non blocking, potential issues):</p><ul>
            <?php foreach ($data['warnings'] as $w): ?>
                <li><?php echo $w ?></li>
            <?php endforeach; ?>
            </ul>
        <?php endif; ?>

        <?php if (count($data['ok']) > 0): ?>
            <p>The following <b><?php echo count($data['ok']) ?></b> genes are <b>valid</b>:</p><ul>
            <?php foreach ($data['ok'] as $o): ?>
                <li><?php echo $o ?></li>
            <?php endforeach; ?>
            </ul>
        <?php endif; ?>
    <?php endforeach; ?>
<?php endif; ?>

<?php if ($is_admin && (getenv("DETAILED_REPORT") == "1")): ?>
    <h2 id="splitted">Splitted genes:</h2><ul>

    <?php foreach ($report['splitted'] as $gene => $parts): ?>
        <li><?php echo $gene ?>: <?php echo join(', ', $parts) ?></li>
    <?php endforeach; ?>
    </ul>


    <h2 id="parts">Parts repartition:</h2><ul>
    <?php foreach ($report['parts'] as $p_name => $p_num): ?>
        <li><?php echo $p_name ?>: <?php echo $p_num ?></li>
    <?php endforeach; ?>
    </ul>


    <h2 id="duplicated">Duplicated genes:</h2><ul>
    <?php foreach ($report['duplicated'] as $gene => $alleles): ?>
        <li><?php echo $gene ?>: <?php echo join(', ', $alleles) ?></li>
    <?php endforeach; ?>
    </ul>


    <h2 id="alleles">Alleles repartition:</h2><ul>
    <?php foreach ($report['alleles'] as $a_name => $a_num): ?>
        <li><?php echo $a_name ?>: <?php echo $a_num ?></li>
    <?php endforeach; ?>
    </ul>
<?php endif; ?>

<?php if (count($report['wa_errors']) > 0 && $is_admin): ?>

    <h2 id="unexpected">Found <?php echo count($report['wa_errors']); ?> unexpected errors in the gff produced by WebApollo:</h2><ul>
    <?php foreach ($report['wa_errors'] as $e): ?>
        <li><?php echo $e; ?></li>
    <?php endforeach; ?>
    </ul>
<?php endif; ?>
</div>
<?php } ?>
<?php };?>
<?php endif; ?>
</body>
</html>
