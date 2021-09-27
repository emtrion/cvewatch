<?php
const TITLE = "Projects";
include '../assets/layouts/header.php';
check_verified();
?>

<main class="container">

	<div class="row">
		<div class="col-sm-9">

			<div class="d-flex align-items-center p-3 mt-5 mb-3 text-black-50 rounded box-shadow">
				<div class="lh-100">
					<h4 class="mb-0 text-black lh-100">My projects</h4>
					<?php
					require '../assets/setup/db.inc.php';
					require '../assets/includes/projects.php';
					$projects = listProjectsForUser($conn, $_SESSION['id']);
					echo '<p class="media-body pb-3 mb-0 lh-125 border-bottom border-gray">';
					if (!$projects) {
						echo "<br>You have no projects yet.";
					} else {
						foreach ($projects as $p) {
							echo '<br><a href="project_view.php?project_name=' . $p . '">' . $p . '</a>';
						}
					}
					echo '</p>';
					?>
					<p class="media-body pb-3 mb-0 lh-125 border-bottom border-gray">
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
