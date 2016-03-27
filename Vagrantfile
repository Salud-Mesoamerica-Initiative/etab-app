# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box_check_update = false

  config.vm.define "db" do |e|
    e.vm.box = "puppetlabs/ubuntu-14.04-64-puppet"
    e.vm.box_version = "1.0.1"

    e.vm.hostname = "db"

    e.vm.network :forwarded_port, guest: 5432, host: 15432
    config.vm.network "private_network", ip: "192.100.100.1"

    e.vm.provider "virtualbox" do |vb|
      vb.name = "db"
    end

    e.vm.provision "shell" do |shell|
      shell.path = "scripts/startup.sh"
    end

    e.vm.provision :puppet do |puppet|
      puppet.manifests_path = "puppet/manifests"
      puppet.manifest_file  = "init.pp"
    end

    e.vm.provision "shell" do |shell|
        shell.inline = "cd /vagrant && docker-compose up -d"
    end

  end
end