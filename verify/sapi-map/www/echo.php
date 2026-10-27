<?php
// Reports how much of the request body the PHP parser actually accepted.
header('Content-Type: application/json');
echo json_encode([
    'php' => PHP_VERSION,
    'post_fields' => count($_POST),
    'files' => count($_FILES),
    'content_length_seen' => $_SERVER['CONTENT_LENGTH'] ?? null,
    'transfer_encoding' => $_SERVER['HTTP_TRANSFER_ENCODING'] ?? null,
]);
