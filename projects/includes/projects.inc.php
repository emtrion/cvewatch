<?php

session_start();
include '../../assets/setup/db.inc.php';
include '../../assets/includes/projects.php';

// check if current user has an upload folder, if not create it
$upload_path = "../../assets/uploads/users/";
$current_user_id = $_SESSION['id'];
$current_project = $_POST['pname'];

if (!file_exists($upload_path . $current_user_id . "/" . $current_project)) {
	mkdir($upload_path . $current_user_id . "/" . $current_project, 0777, true);
}

// handle file upload
if (isset($_POST["submit"])) {
	$target_dir = $upload_path . $current_user_id . "/" . $current_project . "/";
	$target_file = $target_dir . basename($_FILES["fileToUpload"]["name"]);

	if ($_POST['os'] == "Debian") {
		// check if xml is valid
		$xml = simplexml_load_file($_FILES["fileToUpload"]["tmp_name"]);
		if ($xml) {
			$message = "File is valid xml. ";
			$uploadOk = 1;
		} else {
			$message = "File is not a valid xml. ";
			$uploadOk = 0;
		}
	} else {
		// check if csv is valid
		$lines = getLines($_FILES["fileToUpload"]["tmp_name"]);
		$handle = fopen($_FILES["fileToUpload"]["tmp_name"], "r");

		while (($data = fgetcsv($handle, 10000, ";")) !== FALSE)
			$row++;

		// check if valid csv lines equals number of lines in total
		if ($row == $lines) {
			$message = "File is valid csv. ";
			$uploadOk = 1;
		} else {
			$message = "File is not a valid csv. ";
			$uploadOk = 0;
		}
		fclose($handle);
	}

	// check if file already exists
	if (file_exists($target_file)) {
		$message = $message . "File already exists. ";
		$uploadOk = 0;
	}

	// check file size
	if ($_FILES["fileToUpload"]["size"] > 500000) {
		$message = $message . "Your file is too large. ";
		$uploadOk = 0;
	}

	// check if $uploadOk is set to 0 by an error
	if ($uploadOk == 0) {
		$message = $message . "Your file was not uploaded. ";
		// if everything is ok, try to upload file
	} else {
		if (move_uploaded_file($_FILES["fileToUpload"]["tmp_name"], $target_file)) {
			$message = $message . "The file " . htmlspecialchars(basename($_FILES["fileToUpload"]["name"])) . " has been uploaded.";
			// set file upload in db
			setFileUpload($conn, $current_user_id, $current_project, $_FILES["fileToUpload"]["name"]);
		} else {
			$message = $message . "There was an error uploading your file.";
		}
	}

	if ($uploadOk == 1) {
		$_SESSION['STATUS']['success'] = $message;
	} else {
		$_SESSION['ERRORS']['imageerror'] = $message;
	}
	header("Location: ../project_view.php?project_name=" . $_POST['pname'] . "");
	exit();
}
