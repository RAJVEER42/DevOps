output "vpc_id" {
  value = aws_vpc.main.id
}

output "vpc_cidr" {
  value = aws_vpc.main.cidr_block
}

output "public_subnet_ids" {
  value = aws_subnet.public[*].id
}

output "public_subnet_cidrs" {
  value = aws_subnet.public[*].cidr_block
}

output "internet_gateway_id" {
  value = aws_internet_gateway.main.id
}

output "route_table_id" {
  value = aws_route_table.public.id
}

output "web_security_group_id" {
  value = aws_security_group.web.id
}

output "web_instance_id" {
  value = var.create_instance ? aws_instance.web[0].id : null
}

output "web_public_ip" {
  value = var.create_instance ? aws_instance.web[0].public_ip : null
}
