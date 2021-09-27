<?php
const TITLE = "Project View";
include '../assets/layouts/header.php';
check_verified();
?>

<main class="container">

	<div class="row">
		<div class="col-sm-9">

			<div class="d-flex align-items-center p-3 mt-5 mb-3 text-black-50 rounded box-shadow">
				<div class="lh-100">
					<h4 class="mb-0 text-black lh-100">Add project</h4><br>
					<form method="post" action="<?php echo $_SERVER['PHP_SELF']; ?>">
						<div class="form-group">
							<label>Project name:</label>
							<input type="text" name="pname" class="form-control" placeholder="Project name"
								   autocomplete="off" required>
						</div>
						<div class="form-group">
							<label>Operating system:</label>
							<select class="custom-select" id="operating_system" name="os">
								<option selected>Choose operating system</option>
								<option value="Debian">Debian</option>
								<option value="Yocto">Yocto</option>
							</select>
						</div>
						<button class="btn btn-lg btn-primary btn-block mb-5" type="submit" name="add-project">
							Add
						</button>
					</form>
					<?php
					require '../assets/setup/db.inc.php';
					require '../assets/includes/projects.php';

					if ($_SERVER["REQUEST_METHOD"] == "POST") {
						$pname = $_POST['pname'];
						$os = $_POST['os'];
						addProject($conn, $pname, $os, $_SESSION['id']);
						$_SESSION['STATUS']['success'] = "Project added.";
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
