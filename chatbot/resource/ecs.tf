resource "aws_ecs_cluster" "chatbot_cluster" {
  name = "chatbot_cluster"
}

resource "aws_ecs_task_definition" "training_task_def" {
  family                   = "training_task_def"
  task_role_arn            = aws_iam_role.ecs_task_role.arn
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  network_mode             = "awsvpc"
  cpu                      = var.training_fargate_cpu
  memory                   = var.training_fargate_memory
  requires_compatibilities = ["FARGATE"]

  container_definitions = <<DEFINITION
    [
      {
        "name": "trainning_service",
        "image": "${module.trainning-ecr.repository.repository_url}",
        "essential": true,
        "portMappings": [
          {
            "containerPort": 5000,
            "hostPort": 5000
          }
        ],
        "logConfiguration": {
          "logDriver": "awslogs",
          "options": {
            "awslogs-group": "${aws_cloudwatch_log_group.training-service-log.name}",
            "awslogs-region": "ap-southeast-1",
            "awslogs-stream-prefix": "ecs"
          }
        }
      }
    ]
    DEFINITION
}

resource "aws_ecs_service" "training_service" {
  name            = "training_service"
  cluster         = aws_ecs_cluster.chatbot_cluster.id
  task_definition = aws_ecs_task_definition.training_task_def.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    security_groups  = [aws_security_group.ecs_tasks.id]
    subnets          = aws_subnet.public.*.id
    # subnets          = aws_subnet.private.*.id
    assign_public_ip = true
  }

  depends_on = [module.trainning_ecr_image]
}


resource "aws_ecs_task_definition" "chatbot_task_def" {
  family                   = "chatbot_task_def"
  task_role_arn            = aws_iam_role.ecs_task_role.arn
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  network_mode             = "awsvpc"
  cpu                      = var.fargate_cpu
  memory                   = var.fargate_memory
  requires_compatibilities = ["FARGATE","EC2"]

  container_definitions = <<DEFINITION
    [
      {
        "name": "chatbot_service",
        "image": "${module.chatbot-ecr.repository.repository_url}",
        "tag":"v2",
        "essential": true,
        "portMappings": [
          {
            "containerPort": 3000,
            "hostPort": 3000
          }
        ],
        "logConfiguration": {
          "logDriver": "awslogs",
          "options": {
            "awslogs-group": "${aws_cloudwatch_log_group.chatbot-service-log.name}",
            "awslogs-region": "ap-southeast-1",
            "awslogs-stream-prefix": "ecs"
          }
        }
      }
    ]
    DEFINITION
}

resource "aws_ecs_service" "chatbot_service" {
  name            = "chatbot_service"
  cluster         = aws_ecs_cluster.chatbot_cluster.id
  task_definition = aws_ecs_task_definition.chatbot_task_def.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    security_groups  = [aws_security_group.ecs_tasks.id]
    subnets          = aws_subnet.public.*.id
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_alb_target_group.app.id
    container_name   = "chatbot_service"
    container_port   = var.app_port
  }

  depends_on = [module.chatbot_ecr_image, aws_alb_listener.front_end]
}