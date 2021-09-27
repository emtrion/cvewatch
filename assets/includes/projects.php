<?php

function listProjectsForUser($conn, $user_id)
{
	$sql = "select project_name from project where users_id = ?;";
	$stmt = mysqli_stmt_init($conn);

	if (!mysqli_stmt_prepare($stmt, $sql)) {
		return $_SESSION['ERRORS']['scripterror'] = 'SQL error';
	} else {
		mysqli_stmt_bind_param($stmt, "i", $user_id);
		mysqli_stmt_execute($stmt);
		mysqli_stmt_store_result($stmt);
		$result = mysqli_stmt_num_rows($stmt);

		if ($result > 0) {
			$projects = [];
			mysqli_stmt_execute($stmt);
			$result = mysqli_stmt_get_result($stmt);
			while ($row = mysqli_fetch_array($result, MYSQLI_NUM)) {
				foreach ($row as $r) {
					array_push($projects, $r);
				}
			}
			return $projects;
		} else {
			return array();
		}
	}
}

function getProjectInfo($conn, $user_id, $project_name)
{
	$sql = "select operating_system, uploaded_file from project where project_name = ? and users_id = ?;";
	$stmt = mysqli_stmt_init($conn);

	if (!mysqli_stmt_prepare($stmt, $sql)) {
		return $_SESSION['ERRORS']['scripterror'] = 'SQL error';
	} else {
		mysqli_stmt_bind_param($stmt, "si", $project_name, $user_id);
		mysqli_stmt_execute($stmt);
		mysqli_stmt_store_result($stmt);
		$result = mysqli_stmt_num_rows($stmt);

		if ($result > 0) {
			$info = [];
			mysqli_stmt_execute($stmt);
			$result = mysqli_stmt_get_result($stmt);
			while ($row = mysqli_fetch_array($result, MYSQLI_NUM)) {
				foreach ($row as $r) {
					array_push($info, $r);
				}
			}
			return $info;
		} else {
			return array();
		}
	}
}

function isAllowedToViewProject($conn, $user_id, $project_name)
{
	$sql = "select * from project where project_name = ? and users_id = ?;";
	$stmt = mysqli_stmt_init($conn);

	if (!mysqli_stmt_prepare($stmt, $sql)) {
		return $_SESSION['ERRORS']['scripterror'] = 'SQL error';
	} else {
		mysqli_stmt_bind_param($stmt, "si", $project_name, $user_id);
		mysqli_stmt_execute($stmt);
		$result = mysqli_stmt_get_result($stmt);
		$row = mysqli_fetch_row($result);
		if ($row)
			return true;
		return false;
	}
}

function addProject($conn, $pname, $os, $user_id)
{
	$sql = "insert into project (project_name, operating_system, users_id, uploaded_file, status_cve_check, check_active) values (?,?,?,?,?,?)";
	$stmt = mysqli_stmt_init($conn);
	if (!mysqli_stmt_prepare($stmt, $sql)) {
		$_SESSION['ERRORS']['scripterror'] = 'SQL ERROR';
		header("Location: ../");
		exit();
	} else {
		$empty = "";
		mysqli_stmt_bind_param($stmt, "ssisss", $pname, $os, $user_id, $empty, $empty, $empty);
		mysqli_stmt_execute($stmt);
		mysqli_stmt_store_result($stmt);
	}
	mysqli_stmt_close($stmt);
	mysqli_close($conn);
}

function removeProject($conn, $pname, $user_id)
{
	// get uploaded file name
	$result = getProjectInfo($conn, $user_id, $pname);
	$upload_path = "../assets/uploads/users/";

	// remove uploaded file
	if (file_exists($upload_path . $user_id . "/" . $pname . "/" . $result[1]))
		unlink($upload_path . $user_id . "/" . $pname . "/" . $result[1]);

	// remove project folder
	if (is_dir($upload_path . $user_id . "/" . $pname))
		rmdir($upload_path . $user_id . "/" . $pname);

	$sql = "delete from project where project_name = ? AND users_id = ?";
	$stmt = mysqli_stmt_init($conn);
	if (mysqli_stmt_prepare($stmt, $sql)) {
		mysqli_stmt_bind_param($stmt, "si", $pname, $user_id);
		mysqli_stmt_execute($stmt);
	}

	mysqli_stmt_close($stmt);
	mysqli_close($conn);
}

function getLines($file)
{
	$f = fopen($file, 'rb');
	$lines = 0;

	while (!feof($f)) {
		$lines += substr_count(fread($f, 8192), "\n");
	}

	fclose($f);

	return $lines;
}

function getOperatingSystem($conn, $user_id, $project_name)
{
	$sql = "select operating_system from project where project_name = ? and users_id = ?;";
	$stmt = mysqli_stmt_init($conn);

	if (!mysqli_stmt_prepare($stmt, $sql)) {
		return $_SESSION['ERRORS']['scripterror'] = 'SQL error';
	} else {
		mysqli_stmt_bind_param($stmt, "si", $project_name, $user_id);
		mysqli_stmt_execute($stmt);
		$result = mysqli_stmt_get_result($stmt);
		$row = mysqli_fetch_row($result);
		return $row[0];
	}
}

function getProjectID($conn, $user_id, $project_name)
{
	$sql = "select id from project where project_name = ? and users_id = ?;";
	$stmt = mysqli_stmt_init($conn);

	if (!mysqli_stmt_prepare($stmt, $sql)) {
		return $_SESSION['ERRORS']['scripterror'] = 'SQL error';
	} else {
		mysqli_stmt_bind_param($stmt, "si", $project_name, $user_id);
		mysqli_stmt_execute($stmt);
		$result = mysqli_stmt_get_result($stmt);
		$row = mysqli_fetch_row($result);
		return $row[0];
	}
}

function setFileUpload($conn, $user_id, $pname, $fname)
{
	$sql = "update project set uploaded_file = ?, status_cve_check = ?, check_active = ? where project_name = ? and users_id = ?";
	$stmt = mysqli_stmt_init($conn);
	if (!mysqli_stmt_prepare($stmt, $sql)) {
		$_SESSION['ERRORS']['scripterror'] = 'SQL ERROR';
		header("Location: ../");
		exit();
	} else {
		$value = "Running";
		$check_active = "true";
		mysqli_stmt_bind_param($stmt, "ssssi", $fname, $value, $check_active, $pname, $user_id);
		mysqli_stmt_execute($stmt);
		mysqli_stmt_store_result($stmt);
	}

	// get project type
	$result = getOperatingSystem($conn, $user_id, $pname);
	$pid = getProjectID($conn, $user_id, $pname);

	if ($result == "Debian") {
		// call add debian check
		exec("python3 ../../webapp/webapp.py Debian $pid > /dev/null 2>&1 &");
	} else {
		// call add yocto check
		exec("python3 ../../webapp/webapp.py Yocto $pid > /dev/null 2>&1 &");
	}

	mysqli_stmt_close($stmt);
	mysqli_close($conn);
}

function isCheckActive($conn, $user_id, $project_name)
{
	$sql = "select check_active from project where project_name = ? and users_id = ?;";
	$stmt = mysqli_stmt_init($conn);

	if (!mysqli_stmt_prepare($stmt, $sql)) {
		return $_SESSION['ERRORS']['scripterror'] = 'SQL error';
	} else {
		mysqli_stmt_bind_param($stmt, "si", $project_name, $user_id);
		mysqli_stmt_execute($stmt);
		$result = mysqli_stmt_get_result($stmt);
		$row = mysqli_fetch_row($result);
		if ($row[0] == "true")
			return true;
		return false;
	}
}

function getCheckStatus($conn, $user_id, $project_name)
{
	$sql = "select status_cve_check from project where project_name = ? and users_id = ?;";
	$stmt = mysqli_stmt_init($conn);

	if (!mysqli_stmt_prepare($stmt, $sql)) {
		return $_SESSION['ERRORS']['scripterror'] = 'SQL error';
	} else {
		mysqli_stmt_bind_param($stmt, "si", $project_name, $user_id);
		mysqli_stmt_execute($stmt);
		$result = mysqli_stmt_get_result($stmt);
		$row = mysqli_fetch_row($result);
		return $row[0];
	}
}

function listVulnerablePackages($conn, $user_id, $os, $project_name)
{
	if ($os == "Debian") {
		$sql = "select debian_package_name, version from debian_package where project_id = (select id from project where project_name = ? and users_id = ?) and is_vulnerable = ? order by debian_package_name;";
	} else if ($os == "Yocto") {
		$sql = "select yocto_package_name, version from yocto_package where project_id = (select id from project where project_name = ? and users_id = ?) and is_vulnerable = ? order by yocto_package_name;";
	}

	$stmt = mysqli_stmt_init($conn);

	if (!mysqli_stmt_prepare($stmt, $sql)) {
		return $_SESSION['ERRORS']['scripterror'] = 'SQL error';
	} else {
		$value = "true";
		mysqli_stmt_bind_param($stmt, "sis", $project_name, $user_id, $value);
		mysqli_stmt_execute($stmt);
		mysqli_stmt_store_result($stmt);
		$result = mysqli_stmt_num_rows($stmt);

		if ($result > 0) {
			$packages = [];
			mysqli_stmt_execute($stmt);
			$result = mysqli_stmt_get_result($stmt);
			while ($row = mysqli_fetch_array($result, MYSQLI_NUM)) {
				foreach ($row as $r) {
					array_push($packages, $r);
				}
			}
			return $packages;
		} else {
			return array();
		}
	}
}
