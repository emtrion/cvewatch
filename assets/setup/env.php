<?php

if (!defined('APP_NAME'))						define('APP_NAME', 'emCVE-Watch');
if (!defined('APP_ORGANIZATION'))				define('APP_ORGANIZATION', 'emtrion');
if (!defined('APP_OWNER'))						define('APP_OWNER', 'emtrion GmbH');
if (!defined('APP_DESCRIPTION'))				define('APP_DESCRIPTION', 'emCVE-Watch');

if (!defined('ALLOWED_INACTIVITY_TIME'))		define('ALLOWED_INACTIVITY_TIME', time()+1*60);

if (!defined('DB_DATABASE'))					define('DB_DATABASE', 'cvewatch');
if (!defined('DB_HOST'))						define('DB_HOST','127.0.0.1');
if (!defined('DB_USERNAME'))					define('DB_USERNAME','root');
if (!defined('DB_PASSWORD'))					define('DB_PASSWORD' ,'password');
if (!defined('DB_PORT'))						define('DB_PORT' ,'');

if (!defined('MAIL_HOST'))						define('MAIL_HOST', 'smtp.example.com');
if (!defined('MAIL_USERNAME'))					define('MAIL_USERNAME', 'no-reply@example.com');
if (!defined('MAIL_PASSWORD'))					define('MAIL_PASSWORD', '');
if (!defined('MAIL_ENCRYPTION'))				define('MAIL_ENCRYPTION', 'ssl');
if (!defined('MAIL_PORT'))						define('MAIL_PORT', 465);
