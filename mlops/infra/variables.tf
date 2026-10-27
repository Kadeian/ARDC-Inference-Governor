variable "region" { default = "us-east-2" }
variable "environment" { default = "staging" }
variable "vpc_id" { type = string }
variable "public_subnet_ids" { type = list(string) }
variable "private_subnet_ids" { type = list(string) }
variable "certificate_arn" { type = string }
variable "image_digest_uri" {
  type = string
  validation {
    condition     = can(regex("@sha256:[a-f0-9]{64}$", var.image_digest_uri))
    error_message = "Supply an immutable ECR image digest URI."
  }
}
variable "api_token_secret_arn" { type = string }
variable "agent_factory" { type = string }
variable "policy_factory" { type = string }
variable "budget_email" { type = string }
variable "monthly_budget_usd" { default = "100" }
variable "allowed_client_cidrs" {
  type        = list(string)
  description = "Initial restricted ingress. Public website traffic requires edge auth, WAF and rate limiting review."
  validation {
    condition     = length(var.allowed_client_cidrs) > 0 && !contains(var.allowed_client_cidrs, "0.0.0.0/0")
    error_message = "Start with restricted client CIDRs."
  }
}
