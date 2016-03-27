########################################
# Install Docker.
########################################
class { 'docker':
  version      => '1.7.1',
  docker_users => ['vagrant'],
}

########################################
# Install Docker Compose.
########################################
exec { 'download docker compose':
  command   => 'curl -L https://github.com/docker/compose/releases/download/1.4.0/docker-compose-Linux-x86_64 > /usr/local/bin/docker-compose',
  creates   => '/usr/local/bin/docker-compose',
  cwd       => '/root',
  logoutput => true,
  path      => $::path,
  timeout   => 600,
  require   => Class['docker'],
} ->
file { '/usr/local/bin/docker-compose':
  ensure => file,
  owner  => 'root',
  group  => 'root',
  mode   => '0755',
}

########################################
# Disable firewall.
########################################
service { 'ufw':
  ensure => stopped,
  enable => false,
}

########################################
# Data directory.
########################################
file { '/data':
  ensure => directory,
  owner  => 'vagrant',
  group  => 'vagrant',
  mode   => '0755',
}