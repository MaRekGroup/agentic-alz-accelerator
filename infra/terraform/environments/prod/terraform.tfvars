# Production Environment Configuration

subscription_id       = "00000000-0000-0000-0000-000000000000" # Replace with prod subscription
location              = "southcentralus"
management_group_name = "Corp"
profile_name          = "corp"
vnet_address_space    = "10.2.0.0/16"
enable_ddos           = true
enable_defender       = true
log_retention_days    = 365

tags = {
  environment = "production"
  cost_center = "platform"
}
