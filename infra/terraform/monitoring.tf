# Security Group for Monitoring
resource "aws_security_group" "monitoring" {
  name        = "${var.project_prefix}-monitoring-sg-${var.environment}"
  description = "Security group for monitoring services (Prometheus, Grafana)"
  vpc_id      = aws_vpc.main.id

  # Prometheus
  ingress {
    description = "Prometheus from monitoring SG"
    from_port   = 9090
    to_port     = 9090
    protocol    = "tcp"
    self        = true
  }

  # Grafana
  ingress {
    description     = "Grafana from ALB"
    from_port       = 3000
    to_port         = 3000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  ingress {
    description = "Grafana from monitoring SG"
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    self        = true
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_prefix}-monitoring-sg-${var.environment}"
  }
}

# EFS File System for Prometheus
resource "aws_efs_file_system" "prometheus" {
  creation_token = "${var.project_prefix}-prometheus-efs-${var.environment}"
  encrypted      = true

  lifecycle_policy {
    transition_to_ia = "AFTER_30_DAYS"
  }

  tags = {
    Name = "${var.project_prefix}-prometheus-efs-${var.environment}"
  }
}

# EFS Mount Targets for Prometheus
resource "aws_efs_mount_target" "prometheus" {
  count           = 2
  file_system_id  = aws_efs_file_system.prometheus.id
  subnet_id       = aws_subnet.private[count.index].id
  security_groups = [aws_security_group.monitoring.id]
}

# EFS File System for Grafana
resource "aws_efs_file_system" "grafana" {
  creation_token = "${var.project_prefix}-grafana-efs-${var.environment}"
  encrypted      = true

  lifecycle_policy {
    transition_to_ia = "AFTER_30_DAYS"
  }

  tags = {
    Name = "${var.project_prefix}-grafana-efs-${var.environment}"
  }
}

# EFS Mount Targets for Grafana
resource "aws_efs_mount_target" "grafana" {
  count           = 2
  file_system_id  = aws_efs_file_system.grafana.id
  subnet_id       = aws_subnet.private[count.index].id
  security_groups = [aws_security_group.monitoring.id]
}

# Service Discovery Namespace
resource "aws_service_discovery_private_dns_namespace" "main" {
  name        = "nil.local"
  vpc         = aws_vpc.main.id
  description = "Service discovery namespace for ${var.project_prefix}"

  tags = {
    Name = "${var.project_prefix}-service-discovery-${var.environment}"
  }
}

# Service Discovery Service for Prometheus
resource "aws_service_discovery_service" "prometheus" {
  name = "prometheus"

  dns_config {
    namespace_id = aws_service_discovery_private_dns_namespace.main.id

    dns_records {
      ttl  = 10
      type = "A"
    }

    routing_policy = "MULTIVALUE"
  }

  health_check_custom_config {
    failure_threshold = 1
  }

  tags = {
    Name = "${var.project_prefix}-prometheus-discovery-${var.environment}"
  }
}

# Service Discovery Service for Grafana
resource "aws_service_discovery_service" "grafana" {
  name = "grafana"

  dns_config {
    namespace_id = aws_service_discovery_private_dns_namespace.main.id

    dns_records {
      ttl  = 10
      type = "A"
    }

    routing_policy = "MULTIVALUE"
  }

  health_check_custom_config {
    failure_threshold = 1
  }

  tags = {
    Name = "${var.project_prefix}-grafana-discovery-${var.environment}"
  }
}

# SSM Parameter for Grafana Admin Password
resource "aws_ssm_parameter" "grafana_admin_password" {
  name        = "/${var.project_prefix}/${var.environment}/grafana_admin_password"
  description = "Grafana admin password for ${var.project_prefix}"
  type        = "SecureString"
  value       = var.grafana_admin_password

  tags = {
    Name = "${var.project_prefix}-grafana-password-${var.environment}"
  }
}

# ECS Task Definition - Prometheus
resource "aws_ecs_task_definition" "prometheus" {
  family                   = "${var.project_prefix}-prometheus-${var.environment}"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 512
  memory                   = 1024
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  volume {
    name = "prometheus-data"

    efs_volume_configuration {
      file_system_id     = aws_efs_file_system.prometheus.id
      transit_encryption = "ENABLED"
    }
  }

  container_definitions = jsonencode([
    {
      name      = "prometheus"
      image     = "prom/prometheus:${var.prometheus_version}"
      essential = true

      portMappings = [
        {
          containerPort = 9090
          protocol      = "tcp"
        }
      ]

      mountPoints = [
        {
          sourceVolume  = "prometheus-data"
          containerPath = "/prometheus"
          readOnly      = false
        }
      ]

      command = [
        "--config.file=/etc/prometheus/prometheus.yml",
        "--storage.tsdb.path=/prometheus",
        "--web.console.libraries=/usr/share/prometheus/console_libraries",
        "--web.console.templates=/usr/share/prometheus/consoles"
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "prometheus"
        }
      }
    }
  ])

  tags = {
    Name = "${var.project_prefix}-prometheus-task-${var.environment}"
  }
}

# ECS Task Definition - Grafana
resource "aws_ecs_task_definition" "grafana" {
  family                   = "${var.project_prefix}-grafana-${var.environment}"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 512
  memory                   = 1024
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  volume {
    name = "grafana-data"

    efs_volume_configuration {
      file_system_id     = aws_efs_file_system.grafana.id
      transit_encryption = "ENABLED"
    }
  }

  container_definitions = jsonencode([
    {
      name      = "grafana"
      image     = "grafana/grafana:${var.grafana_version}"
      essential = true

      portMappings = [
        {
          containerPort = 3000
          protocol      = "tcp"
        }
      ]

      mountPoints = [
        {
          sourceVolume  = "grafana-data"
          containerPath = "/var/lib/grafana"
          readOnly      = false
        }
      ]

      environment = [
        {
          name  = "GF_SERVER_ROOT_URL"
          value = "https://${var.domain_name}/grafana"
        },
        {
          name  = "GF_SERVER_SERVE_FROM_SUB_PATH"
          value = "true"
        },
        {
          name  = "GF_SECURITY_ADMIN_USER"
          value = "admin"
        },
        {
          name  = "GF_DATABASE_TYPE"
          value = "postgres"
        },
        {
          name  = "GF_DATABASE_HOST"
          value = "${aws_db_instance.main.address}:${aws_db_instance.main.port}"
        },
        {
          name  = "GF_DATABASE_NAME"
          value = var.db_name
        },
        {
          name  = "GF_DATABASE_USER"
          value = var.db_username
        }
      ]

      secrets = [
        {
          name      = "GF_SECURITY_ADMIN_PASSWORD"
          valueFrom = aws_ssm_parameter.grafana_admin_password.arn
        },
        {
          name      = "GF_DATABASE_PASSWORD"
          valueFrom = aws_ssm_parameter.db_password.arn
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "grafana"
        }
      }
    }
  ])

  tags = {
    Name = "${var.project_prefix}-grafana-task-${var.environment}"
  }
}

# ECS Service - Prometheus
resource "aws_ecs_service" "prometheus" {
  name            = "${var.project_prefix}-prometheus-${var.environment}"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.prometheus.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.monitoring.id]
    assign_public_ip = false
  }

  service_registries {
    registry_arn = aws_service_discovery_service.prometheus.arn
  }

  depends_on = [
    aws_efs_mount_target.prometheus
  ]

  tags = {
    Name = "${var.project_prefix}-prometheus-service-${var.environment}"
  }
}

# ECS Service - Grafana
resource "aws_ecs_service" "grafana" {
  name            = "${var.project_prefix}-grafana-${var.environment}"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.grafana.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.monitoring.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.grafana.arn
    container_name   = "grafana"
    container_port   = 3000
  }

  service_registries {
    registry_arn = aws_service_discovery_service.grafana.arn
  }

  depends_on = [
    aws_efs_mount_target.grafana,
    aws_lb_listener.https
  ]

  tags = {
    Name = "${var.project_prefix}-grafana-service-${var.environment}"
  }
}
