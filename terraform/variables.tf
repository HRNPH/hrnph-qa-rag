variable "proxmox_api_url" {
  description = "Proxmox API endpoint (e.g., https://proxmox.example.com:8006/api2/json)"
  type        = string
}

variable "proxmox_api_token_id" {
  description = "Proxmox API token ID"
  type        = string
}

variable "proxmox_api_token_secret" {
  description = "Proxmox API token secret"
  type        = string
  sensitive   = true
}

variable "lxc_target_node" {
  description = "Proxmox node to create the LXC container on"
  type        = string
}

variable "lxc_hostname" {
  description = "Hostname for the new LXC container"
  type        = string
  default     = "docker-lxc"
}

variable "lxc_template" {
  description = "The template to use for the LXC container (e.g., local:vztmpl/ubuntu-20.04-standard_20.04-1_amd64.tar.gz)"
  type        = string
}

variable "lxc_vm_id" {
  description = "VM ID for the LXC container"
  type        = number

}

variable "lxc_cores" {
  description = "Number of CPU cores for the LXC container"
  type        = number
  default     = 2
}

variable "lxc_memory" {
  description = "Memory (in MB) for the LXC container"
  type        = number
  default     = 2048
}

variable "lxc_swap" {
  description = "Swap (in MB) for the LXC container"
  type        = number
  default     = 512
}

variable "lxc_rootfs" {
  description = "Storage for the LXC container root filesystem (e.g., local-lvm:8)"
  type        = string
}

variable "lxc_bridge" {
  description = "Bridge interface to use (e.g., vmbr0)"
  type        = string
}

variable "lxc_ip" {
  description = "Static IP to assign to the LXC container"
  type        = string
}

variable "lxc_gw" {
  description = "Gateway for the LXC container"
  type        = string
}

variable "lxc_root_password" {
  description = "Root password for the LXC container"
  type        = string
  sensitive   = true
}

variable "lxc_private_key" {
  description = "Private key for the LXC container"
  type        = string
  sensitive   = true
}

variable "lxc_public_key" {
  description = "Public key for the LXC container"
  type        = string
}

variable "github_username" {
  description = "GitHub username (owner of the private repo)"
  type        = string
}

variable "github_token" {
  description = "GitHub personal access token to clone the private repository"
  type        = string
  sensitive   = true
}

variable "github_repo" {
  description = "Name of the GitHub repository containing the Docker container"
  type        = string
}

# New Cloudflare variables

variable "cloudflare_api_token" {
  description = "Cloudflare API token with the necessary permissions"
  type        = string
  sensitive   = true
}

variable "cloudflare_account_id" {
  description = "Cloudflare account ID"
  type        = string
}

variable "cloudflare_zone_id" {
  description = "Cloudflare Zone ID for your domain"
  type        = string
}

variable "subdomain" {
  description = "Subdomain to create for tunnel access (without the domain part)"
  type        = string
}

variable "domain" {
  description = "Full domain to route via Cloudflare tunnel (e.g., app.example.com)"
  type        = string
}
