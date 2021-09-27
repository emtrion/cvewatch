<?php
const TITLE = "Home";
include '../assets/layouts/header.php';
check_verified();
?>

<main role="main" class="container">
    <div class="row">
        <div class="col-sm-9">
            <div class="d-flex align-items-center p-3 mt-5 mb-3 text-black-50 bg-light rounded box-shadow">
                <div class="lh-100">
                    <h4 class="mb-0 text-black lh-100">Welcome, <?php echo $_SESSION['username'] . "!"; ?></h4><br>
                    Last logged in at <?php echo date("D M j G:i:s T Y", strtotime($_SESSION['last_login_at'])); ?>
                </div>
            </div>
        </div>
    </div>
</main>

<?php
include '../assets/layouts/footer.php'
?>
