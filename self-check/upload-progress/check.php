<?php
/**
 * session.upload_progress self-check — run against YOUR OWN site.
 *
 * 1. Upload this file to a PHP-served directory on your host.
 * 2. From this directory: python3 probe.py https://your.site/check.php
 * 3. Read the verdict. Then DELETE this file.
 *
 * What it does: starts a session, accepts one small multipart POST carrying
 * a PHP_SESSION_UPLOAD_PROGRESS field plus a tiny file part, and reports
 * whether the upload-progress machinery tracked it ($_SESSION state) — plus
 * the relevant ini settings. No memory pressure, no crash shapes, nothing
 * persisted beyond a session you own. It is a feature test, not an attack.
 */
header('Content-Type: application/json');
$out = [
    'php' => PHP_VERSION,
    'sapi' => PHP_SAPI,
    'ini' => [
        'session.upload_progress.enabled' => ini_get('session.upload_progress.enabled'),
        'session.upload_progress.cleanup' => ini_get('session.upload_progress.cleanup'),
        'session.use_strict_mode' => ini_get('session.use_strict_mode'),
    ],
];
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    session_start();
    $key = 'upload_progress_' . ($_POST['PHP_SESSION_UPLOAD_PROGRESS'] ?? '');
    // cleanup=1 (default) removes the key when the upload finishes, so also
    // look for the machinery having EVER engaged via error-log-free means:
    // the canonical check is the key existing mid-upload. With cleanup on,
    // a completed small upload removes it — so treat cleanup=0 as the
    // observable case and say so honestly.
    $out['session_started'] = true;
    $out['progress_key_present_after_completion'] = isset($_SESSION[$key]);
    $out['note'] = 'with cleanup=1 (default) the key is removed on completion; '
        . 'enabled=' . ($out['ini']['session.upload_progress.enabled'] ?: '0')
        . ' is the authoritative setting for the machinery.';
}
echo json_encode($out, JSON_PRETTY_PRINT);
