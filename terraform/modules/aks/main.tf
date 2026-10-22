# ------------------------------------------ #
# AI Knowledge Copilot - AKS Module            #
# ------------------------------------------ #

variable "aks_name" {
  description = "Name of the AKS cluster"
  type        = string
}

variable "resource_group_name" {
  description = "Resource group name"
  type        = string
}

variable "location" {
  description = "Azure region"
  type        = string
}

variable "kubernetes_version" {
  description = "Kubernetes version (null for Azure default stable)"
  type        = string
  default     = null
}

variable "node_count" {
  description = "Number of agent nodes"
  type        = number
  default     = 1
}

variable "agent_node_vm_size" {
  description = "VM size for agent nodes"
  type        = string
  default     = "Standard_D2s_v4"
}

variable "vnet_subnet_id" {
  description = "Subnet ID for the AKS cluster"
  type        = string
  default     = null
}

variable "tags" {
  description = "Tags for the AKS cluster"
  type        = map(string)
  default     = {}
}

resource "azurerm_kubernetes_cluster" "main" {
  name                = var.aks_name
  resource_group_name = var.resource_group_name
  location            = var.location
  dns_prefix          = "${var.aks_name}-dns"
  kubernetes_version  = var.kubernetes_version

  default_node_pool {
    name           = "agentpool"
    node_count     = var.node_count
    vm_size        = var.agent_node_vm_size
    os_sku         = "Ubuntu"
    vnet_subnet_id = var.vnet_subnet_id
  }

  identity {
    type = "SystemAssigned"
  }

  tags = var.tags
}

output "cluster_name" {
  value = azurerm_kubernetes_cluster.main.name
}

output "cluster_id" {
  value = azurerm_kubernetes_cluster.main.id
}

output "cluster_resource_group" {
  value = azurerm_kubernetes_cluster.main.node_resource_group
}

output "kube_config" {
  value     = azurerm_kubernetes_cluster.main.kube_config_raw
  sensitive = true
}

output "fqdn" {
  value = azurerm_kubernetes_cluster.main.fqdn
}

output "kubelet_identity_object_id" {
  value = azurerm_kubernetes_cluster.main.kubelet_identity[0].object_id
}

output "oidc_issuer_url" {
  value = azurerm_kubernetes_cluster.main.oidc_issuer_url
}
