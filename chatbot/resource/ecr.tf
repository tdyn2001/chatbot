module "trainning-ecr" {
  source = "github.com/byu-oit/terraform-aws-ecr?ref=v1.0.1"
  name   = "trainning-ecr"
}

module "trainning_ecr_image" {
  source             = "github.com/tdyn2002/terraform-aws-ecr-image"
  dockerfile_dir     = "../trainning_service/"
  ecr_repository_url = module.trainning-ecr.repository.repository_url
  docker_image_tag   = "latest"
}

module "chatbot-ecr"{
  source = "github.com/byu-oit/terraform-aws-ecr?ref=v1.0.1"
  name   = "chatbot-ecr"
}

module "chatbot_ecr_image" {
  source             = "github.com/tdyn2002/terraform-aws-ecr-image"
  dockerfile_dir     = "../chatbot-service/src/"
  ecr_repository_url = module.chatbot-ecr.repository.repository_url
  docker_image_tag   = "latest"
}
