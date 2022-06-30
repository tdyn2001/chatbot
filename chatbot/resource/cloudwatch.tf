resource "aws_cloudwatch_log_group" "training-service-log" {
  name = "training-service-log"
}

resource "aws_cloudwatch_log_group" "chatbot-service-log" {
  name = "chatbot-service-log"
}