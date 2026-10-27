[*] blobless clone of php-src (network required)...
TAG            gate1     gate2     fixed    LEAK
php-7.4.0      open      closed    no       DEAD
php-7.4.33     open      closed    no       DEAD
php-8.0.0      open      closed    no       DEAD
php-8.0.30     open      closed    no       DEAD
php-8.1.0      open      closed    no       DEAD
php-8.1.34     open      closed    no       DEAD
php-8.2.0      open      closed    no       DEAD
php-8.2.34     open      closed    no       DEAD
php-8.2.35     open      closed    yes      DEAD
php-8.3.0      open      closed    no       DEAD
php-8.3.16     open      closed    no       DEAD
php-8.3.17     open      open      no       ALIVE
php-8.3.35     open      open      no       ALIVE
php-8.3.36     open      open      yes      DEAD
php-8.4.0      open      closed    no       DEAD
php-8.4.3      open      closed    no       DEAD
php-8.4.4      open      open      no       ALIVE
php-8.4.26     open      open      no       ALIVE
php-8.4.27     open      open      yes      DEAD
php-8.5.0      open      open      no       ALIVE
php-8.5.11     open      open      no       ALIVE
php-8.5.12     open      open      yes      DEAD

Reading the table: the leak is ALIVE only where gate1=open AND gate2=open
AND the tag predates the 2026-10-21 fix floors. That yields the bands:
  ALIVE: 8.3.17-8.3.35, 8.4.4-8.4.26, 8.5.0-8.5.11
  DEAD:  everything older (gate 2 closed), plus all fixed floors
Everything below 8.3.17 can be corrupted and crashed, but never
blind-addressed: the disclosure stage cannot emit.
