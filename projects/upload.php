<?php
const TITLE = "Upload";
include '../assets/layouts/header.php';
include 'includes/projects.inc.php';
check_verified();
?>

<main class="container">

	<div class="row">
		<div class="col-sm-9">

			<div class="d-flex align-items-center p-3 mt-5 mb-3 text-black-50 rounded box-shadow">
				<div class="lh-100">
					<h6 class="mb-0 text-black lh-100">Upload XML/CSV</h6>
					<p class="media-body pb-3 mb-0 small lh-125 border-bottom border-gray">
					</p>

					<form action="includes/projects.inc.php" method="post" enctype="multipart/form-data">
						<small>Upload elbe XML:<br>
							<input type="file" name="fileToUpload" id="fileToUpload">
							<input type="submit" value="Upload" name="submit">
						</small>
					</form>

					<small class="text-success font-weight-bold">
						<?php
						if (isset($_SESSION['STATUS']['success']))
							echo $_SESSION['STATUS']['success'];
						?>
					</small>
					<small class="text-danger font-weight-bold">
						<?php
						if (isset($_SESSION['ERRORS']['imageerror']))
							echo $_SESSION['ERRORS']['imageerror'];
						?>
					</small>
				</div>
			</div>

		</div>
	</div>
</main>

<?php
include '../assets/layouts/footer.php'
?>
