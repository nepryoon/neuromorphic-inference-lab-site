# Open Banking Transaction Enrichment Service
# This file defines the infrastructure for the Open Banking microservice

# ECR Repository for Open Banking service
resource "aws_ecr_repository" "open_banking" {
  name                 = "${var.project_prefix}/open-banking"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Name    = "${var.project_prefix}-open-banking-ecr"
    Service = "open-banking"
  }
}

resource "aws_ecr_lifecycle_policy" "open_banking" {
  repository = aws_ecr_repository.open_banking.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 5 images"
        selection = {
          tagStatus     = "tagged"
          tagPrefixList = ["v"]
          countType     = "imageCountMoreThan"
          countNumber   = 5
        }
        action = {
          type = "expire"
        }
      },
      {
        rulePriority = 2
        description  = "Expire untagged images older than 7 days"
        selection = {
          tagStatus   = "untagged"
          countType   = "sinceImagePushed"
          countUnit   = "days"
          countNumber = 7
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

# ALB Target Group for Open Banking service
resource "aws_lb_target_group" "open_banking" {
  name        = "${var.project_prefix}-open-banking-tg"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    enabled             = true
    path                = "/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
    matcher             = "200"
  }

  deregistration_delay = 30

  tags = {
    Name    = "${var.project_prefix}-open-banking-tg-${var.environment}"
    Service = "open-banking"
  }
}

# ALB Listener Rule for Open Banking service
resource "aws_lb_listener_rule" "open_banking" {
  listener_arn = aws_lb_listener.https.arn
  priority     = 30

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.open_banking.arn
  }

  condition {
    path_pattern {
      values = ["/open-banking", "/open-banking/*", "/transactions", "/transactions/*"]
    }
  }

  tags = {
    Name    = "${var.project_prefix}-open-banking-rule"
    Service = "open-banking"
  }
}

# ECS Task Definition for Open Banking service
resource "aws_ecs_task_definition" "open_banking" {
  family                   = "${var.project_prefix}-open-banking-${var.environment}"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.open_banking_cpu
  memory                   = var.open_banking_memory
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name      = "open-banking"
      image     = "${aws_ecr_repository.open_banking.repository_url}:latest"
      essential = true

      portMappings = [
        {
          containerPort = 8000
          protocol      = "tcp"
        }
      ]

      environment = [
        {
          name  = "ENVIRONMENT"
          value = var.environment
        },
        {
          name  = "LOG_LEVEL"
          value = "INFO"
        },
        {
          name  = "PORT"
          value = "8000"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "open-banking"
        }
      }

      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
    }
  ])

  tags = {
    Name    = "${var.project_prefix}-open-banking-task-${var.environment}"
    Service = "open-banking"
  }
}

# ECS Service for Open Banking
resource "aws_ecs_service" "open_banking" {
  name            = "${var.project_prefix}-open-banking-${var.environment}"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.open_banking.arn
  desired_count   = var.open_banking_desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.open_banking.arn
    container_name   = "open-banking"
    container_port   = 8000
  }

  depends_on = [
    aws_lb_listener.https,
    aws_iam_role_policy_attachment.ecs_execution_role_policy
  ]

  deployment_configuration {
    maximum_percent         = 200
    minimum_healthy_percent = 100
  }

  enable_execute_command = true

  tags = {
    Name    = "${var.project_prefix}-open-banking-service-${var.environment}"
    Service = "open-banking"
  }
}

# CloudWatch Alarms for Open Banking service
resource "aws_cloudwatch_metric_alarm" "open_banking_cpu" {
  alarm_name          = "${var.project_prefix}-open-banking-cpu-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = 300
  statistic           = "Average"
  threshold           = 80

  dimensions = {
    ClusterName = aws_ecs_cluster.main.name
    ServiceName = aws_ecs_service.open_banking.name
  }

  alarm_description = "Open Banking service CPU utilization is too high"

  tags = {
    Name    = "${var.project_prefix}-open-banking-cpu-alarm"
    Service = "open-banking"
  }
}

resource "aws_cloudwatch_metric_alarm" "open_banking_memory" {
  alarm_name          = "${var.project_prefix}-open-banking-memory-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "MemoryUtilization"
  namespace           = "AWS/ECS"
  period              = 300
  statistic           = "Average"
  threshold           = 80

  dimensions = {
    ClusterName = aws_ecs_cluster.main.name
    ServiceName = aws_ecs_service.open_banking.name
  }

  alarm_description = "Open Banking service memory utilization is too high"

  tags = {
    Name    = "${var.project_prefix}-open-banking-memory-alarm"
    Service = "open-banking"
  }
}

# Auto Scaling Target for Open Banking service
resource "aws_appautoscaling_target" "open_banking" {
  max_capacity       = var.open_banking_max_count
  min_capacity       = var.open_banking_min_count
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.open_banking.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

# Auto Scaling Policy - CPU based
resource "aws_appautoscaling_policy" "open_banking_cpu" {
  name               = "${var.project_prefix}-open-banking-cpu-scaling-${var.environment}"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.open_banking.resource_id
  scalable_dimension = aws_appautoscaling_target.open_banking.scalable_dimension
  service_namespace  = aws_appautoscaling_target.open_banking.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value       = 70.0
    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}

# Auto Scaling Policy - Memory based
resource "aws_appautoscaling_policy" "open_banking_memory" {
  name               = "${var.project_prefix}-open-banking-memory-scaling-${var.environment}"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.open_banking.resource_id
  scalable_dimension = aws_appautoscaling_target.open_banking.scalable_dimension
  service_namespace  = aws_appautoscaling_target.open_banking.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageMemoryUtilization"
    }
    target_value       = 70.0
    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}
