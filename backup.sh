#!/bin/bash

BACKUP_DIR="/data"
DEST_DIR="/backup"
TIMESTAMP=$(date +"%Y%m%d%H%M%S")

mkdir -p $DEST_DIR
tar -czf "$DEST_DIR/backup_$TIMESTAMP.tar.gz" $BACKUP_DIR

echo "Backup realizado: backup_$TIMESTAMP.tar.gz"
