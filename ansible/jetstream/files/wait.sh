#!/usr/bin/env bash

for f in lock lock.frontend ; do
  while fuser /var/lib/dpkg/$f >/dev/null 2>&1 ; do
    sleep 1
  done
done
