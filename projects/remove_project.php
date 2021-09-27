<?php
const TITLE = "Remove project";
include '../assets/layouts/header.php';
check_verified();
?>

<main class="container">

	<div class="row">
		<div class="col-sm-9">

			<div class="d-flex align-items-center p-3 mt-5 mb-3 text-black-50 rounded box-shadow">
				<div class="lh-100">
					<h4 class="mb-0 text-black lh-100">Remove project</h4><br>
					<?php
					require '../assets/setup/db.inc.php';
					require '../assets/includes/projects.php';

					$projects = listProjectsForUser($conn, $_SESSION['id']);

					if (!$projects) {
						echo "<p>You have no projects yet.</p>";
					} else {
						echo '<form method="post" action="';
						echo $_SERVER['PHP_SELF'];
						echo '">';
						echo '<div class="form-group">';
						echo ' <label>Project name:</label>';
						echo '<select class="custom-select" name="pname">';
						foreach ($projects as $p) {
							echo "<option value='" . $p . "'>" . $p . "</option>";
						}
						echo "</select>";
						echo '</div>';
						echo '<button class="btn btn-lg btn-primary btn-block mb-5" type="submit" name="add-project">Remove</button>';
						echo '</form>';
					}

					if ($_SERVER["REQUEST_METHOD"] == "POST") {
						$pname = $_POST['pname'];
						removeProject($conn, $pname, $_SESSION['id']);
						$_SESSION['STATUS']['success'] = "Project deleted.";
						header("Location: ./");
					}
					?>
					<small class="text-success font-weight-bold">
						<?php
						if (isset($_SESSION['STATUS']['success']))
							echo $_SESSION['STATUS']['success'];
						?>
					</small>
					<small class="text-danger">
						<?php
						if (isset($_SESSION['ERRORS']['imageerror']))
							echo $_SESSION['ERRORS']['imageerror'];
						?>
					</small>
					<p class="media-body pb-3 mb-0 lh-125 border-top border-bottom border-gray">
						<br><a href="index.php">List projects</a>
						<br><a href="add_project.php">Add project</a>
					</p>
				</div>
			</div>

		</div>
	</div>
</main>

<?php
include '../assets/layouts/footer.php'
?>
