<?php
const TITLE = "Project View";
include '../assets/layouts/header.php';
include 'includes/projects.inc.php';
check_verified();
?>

<main class="container">

	<div class="row">
		<div class="col-sm-9">

			<div class="d-flex align-items-center p-3 mt-5 mb-3 text-black-50 rounded box-shadow">
				<div class="lh-100">
					<h4 class="mb-0 text-black lh-100">Project: <?php echo $_GET['project_name'] ?></h4>
					<?php
					require '../assets/setup/db.inc.php';
					require '../assets/includes/projects.php';

					if (isset($_GET['project_name'])) {
						if (!isAllowedToViewProject($conn, $_SESSION['id'], $_GET['project_name'])) {
							header("Location: ../");
							exit();
						}
					} else {
						header("Location: ../");
						exit();
					}

					$info = getProjectInfo($conn, $_SESSION['id'], $_GET['project_name']);
					echo '<br>Operating System: ' . $info[0];

					if (empty($info[1])) {
						if ($info[0] == "Debian") {
							echo '<br>Package file: No Debian XML uploaded yet.';
							echo '<br>CVE check: not active';
							echo '<form action="includes/projects.inc.php" method="post" enctype="multipart/form-data">';
							echo '		<br><br>Upload Debian XML:<br>';
							echo '		<input type="file" name="fileToUpload" id="fileToUpload">';
							echo '		<input type="hidden" value="Debian" name="os">';
							echo '		<input type="hidden" value="' . $_GET['project_name'] . '" name="pname"><br><br>';
							echo '		<button class="btn btn-lg btn-primary btn-block mb-5" type="submit" name="submit">';
							echo '		Upload';
							echo '		</button>';
							echo '</form>';
						} else {
							echo '<br>Package file: No Yocto CSV uploaded yet.';
							echo '<br>CVE check: not active';
							echo '<form action="includes/projects.inc.php" method="post" enctype="multipart/form-data">';
							echo '		<br><br>Upload Yocto CSV:<br>';
							echo '		<input type="file" name="fileToUpload" id="fileToUpload">';
							echo '		<input type="hidden" value="Yocto" name="os">';
							echo '		<input type="hidden" value="' . $_GET['project_name'] . '" name="pname"><br><br>';
							echo '		<button class="btn btn-lg btn-primary btn-block mb-5" type="submit" name="submit">';
							echo '		Upload';
							echo '		</button>';
							echo '</form>';
						}
					} else {
						echo '<br>Uploaded file: ' . $info[1];
						$check_status = isCheckActive($conn, $_SESSION['id'], $_GET['project_name']);
						if ($check_status) {
							echo '<br>CVE check: <b style="color:green;">active</b>';
						} else {
							echo '<br>CVE check: <b style="color:red;">not active</b>';
						}
						$status = getCheckStatus($conn, $_SESSION['id'], $_GET['project_name']);
						if ($status == "Running") {
							echo '<br>Status CVE check: <b style="color:green;">Running</b>';
						} else {
							echo '<br>Status CVE check: <b style="color:green;">Finished successfully</b>';
						}
						echo '<br><br>';
					}
					if ($info[0] == "Debian") {
						if (!empty($list = listVulnerablePackages($conn, $_SESSION['id'], "Debian", $_GET['project_name']))) {
							echo '<p class="media-body pb-3 mb-0 lh-125 border-top border-bottom border-gray">';
							echo '<br><b>Vulnerable packages:</b><br><br>';
							$i = 0;
							foreach ($list as $l) {
								$i++;
								echo $l . ' ';
								if ($i % 2 == 0)
									echo '<br>';
							}
							echo '</p>';
						}
					} else if ($info[0] == "Yocto") {
						if (!empty($list = listVulnerablePackages($conn, $_SESSION['id'], "Yocto", $_GET['project_name']))) {
							echo '<p class="media-body pb-3 mb-0 lh-125 border-top border-bottom border-gray">';
							echo '<br><b>Vulnerable packages:</b><br><br>';
							$i = 0;
							foreach ($list as $l) {
								$i++;
								echo $l . ' ';
								if ($i % 2 == 0)
									echo '<br>';
							}
							echo '</p>';
						}
					}
					?>
					<small class="text-success font-weight-bold"><br>
						<?php
						if (isset($_SESSION['STATUS']['success']))
							echo $_SESSION['STATUS']['success'];
						?>
					</small>
					<small class="text-danger font-weight-bold"><br>
						<?php
						if (isset($_SESSION['ERRORS']['imageerror']))
							echo $_SESSION['ERRORS']['imageerror'];
						?>
					</small>
					<p class="media-body pb-3 mb-0 lh-125 border-bottom border-gray">
						<br><a href="index.php">List projects</a>
						<br><a href="add_project.php">Add project</a>
						<br><a href="remove_project.php">Remove project</a>
					</p>
				</div>
			</div>

		</div>
	</div>
</main>

<?php
include '../assets/layouts/footer.php'
?>
