terraform {
  required_providers {
    proxmox = {
      source  = "Telmate/proxmox"
      version = "3.0.1-rc4" # Use an appropriate version for your environment
    }
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 5.1.0"
    }
    random = {

    }
  }
}

# Generate a random password for the tunnel secret
resource "random_password" "tunnel_secret" {
  length = 64
}

provider "proxmox" {
  pm_api_url = var.proxmox_api_url
  # pm_api_token_id     = var.proxmox_api_token_id
  # pm_api_token_secret = var.proxmox_api_token_secret
  pm_user     = var.proxmox_api_token_id
  pm_password = var.proxmox_api_token_secret
  pm_parallel = 1 # https://github.com/Telmate/terraform-provider-proxmox/issues/173 (Lockfile Issue)
}

provider "cloudflare" {
  api_token = var.cloudflare_api_token
}

provider "random" {}

# First, create the tunnel in Cloudflare
resource "cloudflare_zero_trust_tunnel_cloudflared" "app_tunnel" {
  account_id    = var.cloudflare_account_id
  name          = "eva-rag-dev"
  tunnel_secret = base64sha256(random_password.tunnel_secret.result)
}

# Configure the tunnel route
resource "cloudflare_zero_trust_tunnel_cloudflared_config" "app_tunnel_config" {
  depends_on = [cloudflare_zero_trust_tunnel_cloudflared.app_tunnel]
  account_id = var.cloudflare_account_id
  tunnel_id  = cloudflare_zero_trust_tunnel_cloudflared.app_tunnel.id
  config = {
    ingress = [
      {
        hostname = var.domain
        service  = "http://localhost:80"
        path     = "/"
      },
      {
        # Catch-all route for 404 errors
        service = "http_status:404"
      }
    ]
  }
}

# Create DNS record for the tunnel
resource "cloudflare_dns_record" "app_tunnel_cname" {
  depends_on = [cloudflare_zero_trust_tunnel_cloudflared.app_tunnel, cloudflare_zero_trust_tunnel_cloudflared_config.app_tunnel_config]
  zone_id    = var.cloudflare_zone_id
  # Subdomain to create for tunnel access
  name    = "eva-rag-dev.hrnph.dev"
  type    = "CNAME"
  proxied = true
  ttl     = 1
  content = "${cloudflare_zero_trust_tunnel_cloudflared.app_tunnel.id}.cfargotunnel.com"
}

resource "proxmox_lxc" "lxc_docker" {
  vmid         = var.lxc_vm_id
  depends_on   = [cloudflare_dns_record.app_tunnel_cname]
  start        = true # Start the container after creation
  target_node  = var.lxc_target_node
  hostname     = var.lxc_hostname
  ostemplate   = var.lxc_template
  cores        = var.lxc_cores
  memory       = var.lxc_memory
  swap         = var.lxc_swap
  unprivileged = false

  features {
    nesting = true
  }

  # Set the root password for the container
  rootfs {
    # Set the storage for the container
    # Set the size of the root filesystem in GB
    storage = var.lxc_rootfs
    size    = "32G"
  }
  password        = var.lxc_root_password
  ssh_public_keys = <<-EOT
    ${var.lxc_public_key}
  EOT

  network {
    name   = "eth0"
    bridge = var.lxc_bridge
    ip     = "${var.lxc_ip}/24"
    gw     = var.lxc_gw
  }

  # Install required packages and set up the container
  provisioner "remote-exec" {
    inline = [
      # Update and install required packages
      "sudo apt-get update -y",
      "sudo apt-get install ca-certificates curl -y",
      "sudo install -m 0755 -d /etc/apt/keyrings",
      "sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc",
      "sudo chmod a+r /etc/apt/keyrings/docker.asc",
      "echo \"deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu jammy stable\" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null;",
      "sudo apt-get update -y",
      "sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y"
    ]

    connection {
      type        = "ssh"
      host        = var.lxc_ip
      user        = "root"
      timeout     = "2m"
      private_key = var.lxc_private_key
    }
  }

  # Login to Docker Registry and pull the image, Using GitHub Container Registry
  provisioner "remote-exec" {
    inline = [
      "docker login ghcr.io -u ${var.github_username} -p ${var.github_token}",
    ]

    connection {
      type        = "ssh"
      host        = var.lxc_ip
      user        = "root"
      private_key = var.lxc_private_key
    }
  }

  # Build and run the Docker container
  provisioner "remote-exec" {
    inline = [
      "sudo docker run -d -p 80:80 ghcr.io/${var.github_username}/${var.github_repo}:latest",
    ]

    connection {
      type        = "ssh"
      host        = var.lxc_ip
      user        = "root"
      private_key = var.lxc_private_key
    }
  }
}

# Upload and configure cloudflared as a systemd service
resource "null_resource" "cloudflared_setup" {
  depends_on = [proxmox_lxc.lxc_docker, cloudflare_zero_trust_tunnel_cloudflared.app_tunnel]

  # Install cloudflared and set up as a service
  provisioner "remote-exec" {
    inline = [
      # Download and install cloudflared
      "curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb",
      # Install by Token
      "sudo dpkg -i cloudflared.deb && sudo cloudflared service install ${cloudflare_zero_trust_tunnel_cloudflared.app_tunnel.tunnel_secret}"
    ]

    connection {
      type        = "ssh"
      host        = var.lxc_ip
      user        = "root"
      private_key = var.lxc_private_key
    }
  }
}
