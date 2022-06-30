module "s3_bucket_chatbot_bot" {
  source = "terraform-aws-modules/s3-bucket/aws"

  bucket = "chatbot-training-data-demo1"
  acl    = "private"

  versioning = {
    enabled = false
  }

}

module "s3_bucket_chatbot_traning" {
  source = "terraform-aws-modules/s3-bucket/aws"

  bucket = "chatbotbucket-demo1"
  acl    = "private"

  versioning = {
    enabled = false
  }

}

resource "aws_s3_bucket_object" "object" {
  bucket = "chatbot-training-data-demo1"
  key    = "data/intents.json"
  source = "../data/intents.json"

  etag = filemd5("../data/intents.json")
}