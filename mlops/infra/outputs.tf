output "repository_url" { value = aws_ecr_repository.api.repository_url }
output "cluster_name" { value = aws_ecs_cluster.api.name }
output "service_name" { value = aws_ecs_service.api.name }
output "deployment_application" { value = aws_codedeploy_app.api.name }
output "deployment_group" { value = aws_codedeploy_deployment_group.api.deployment_group_name }
output "task_definition_arn" { value = aws_ecs_task_definition.api.arn }
output "endpoint" { value = "https://${aws_lb.api.dns_name}" }
