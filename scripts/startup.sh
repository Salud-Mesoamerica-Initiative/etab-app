#!/bin/sh

# Install modules from puppetforge.
if [ ! -d "/etc/puppet/modules/docker" ]; then
  puppet module install garethr-docker --version 4.1.1
fi