output "chatbot_repo_url" {
  value = module.chatbot-ecr.repository.repository_url
}

output "training_repo_url" {
  value = module.trainning-ecr.repository.repository_url
}

output "training-service-log" {
  value = aws_cloudwatch_log_group.training-service-log.name
}