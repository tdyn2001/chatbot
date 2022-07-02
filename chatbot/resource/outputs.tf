output "chatbot_repo_url" {
  value = module.chatbot-ecr.repository.repository_url
}

output "training_repo_url" {
  value = module.trainning-ecr.repository.repository_url
}

output "training-service-log" {
  value = aws_cloudwatch_log_group.training-service-log.name
}

output "alb_hostname" {
  value = aws_alb.main.dns_name
}

output "s3_training_bucket" {
  value = module.s3_bucket_chatbot_bot.s3_bucket_bucket_domain_name
}

output "traning_task_name" {
  value = aws_ecs_task_definition.training_task_def.family
}

output "subnets" {
  value = aws_subnet.public.*.id
}

output "ecs_task_execution_role"{
  value = aws_iam_role.ecs_task_execution_role.arn
}

output "ecs_task_role"{
  value = aws_iam_role.ecs_task_role.arn
}