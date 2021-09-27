<?php

if (isset($_SESSION['auth'])) {
	header("Location: home");
} else {
	header("Location: login");
}
exit();
