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
    http = {
      source  = "hashicorp/http"
      version = "3.4.5"
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
        hostname = "${var.subdomain}.${var.domain}"
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
  unprivileged = true

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
      # Update and install required packages (Docker)
      "sudo apt-get update -y",
      "sudo apt-get install ca-certificates curl -y",
      "sudo install -m 0755 -d /etc/apt/keyrings",
      "sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc",
      "sudo chmod a+r /etc/apt/keyrings/docker.asc",
      "echo \"deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu jammy stable\" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null;",
      "sudo apt-get update -y",
      "sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y",
      # Install Infisical CLI (Secret Manager)
      "curl -1sLf 'https://dl.cloudsmith.io/public/infisical/infisical-cli/setup.deb.sh' | sudo -E bash",
      "sudo apt-get update && sudo apt-get install -y infisical"
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

  # Inject Secret From Secret Manager & run the container
  provisioner "remote-exec" {
    inline = [
      "#!/bin/bash", # Use a bash script to run the command, since <() is a bash feature
      "echo '{{$secrets := secret \"<infisical-project-id>\" \"<environment-slug>\" \"<folder-path>\"}}\n{{- range $secret := $secrets }}\n{{$secret.Key}}={{$secret.Value}}\n{{- end}}' > /tmp/gotemplate",
      "docker run -d -p 80:8080 --env-file <(infisical export --format=dotenv --token='${var.infisical_token}' --template /tmp/gotemplate) ghcr.io/${var.github_username}/${var.github_repo}:latest",
      "rm /tmp/gotemplate"
    ]

    connection {
      type        = "ssh"
      host        = var.lxc_ip
      user        = "root"
      private_key = var.lxc_private_key
    }
  }
}


# Workaround to get the tunnel token Ref: https://github.com/cloudflare/terraform-provider-cloudflare/issues/5149
data "http" "tunnel_token" {
  depends_on = [cloudflare_zero_trust_tunnel_cloudflared.app_tunnel]
  url        = "https://api.cloudflare.com/client/v4/accounts/${var.cloudflare_account_id}/cfd_tunnel/${cloudflare_zero_trust_tunnel_cloudflared.app_tunnel.id}/token"

  request_headers = {
    "Authorization" = "Bearer ${var.cloudflare_api_token}"
    "Content-Type"  = "application/json"
  }
}

# Upload and configure cloudflared as a systemd service
resource "null_resource" "cloudflared_setup" {
  depends_on = [proxmox_lxc.lxc_docker, cloudflare_zero_trust_tunnel_cloudflared.app_tunnel]
  # Only if the tunnel token is available
  triggers = {
    tunnel_token = data.http.tunnel_token.response_body
  }

  # Install cloudflared and set up as a service
  provisioner "remote-exec" {
    inline = [
      # Download and install cloudflared
      "curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb",
      # Install by Token
      "sudo dpkg -i cloudflared.deb",
      "rm cloudflared.deb",
      "sudo cloudflared service install ${jsondecode(data.http.tunnel_token.response_body)["result"]}",
    ]

    connection {
      type        = "ssh"
      host        = var.lxc_ip
      user        = "root"
      private_key = var.lxc_private_key
    }
  }
}
