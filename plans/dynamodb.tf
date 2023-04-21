resource "aws_dynamodb_table" "ews_ch" {
  name         = "${lower(var.app_env)}_ews_darklist"
  billing_mode = "PAY_PER_REQUEST"
  table_class  = "STANDARD"

  server_side_encryption {
    enabled = true
  }

  attribute {
    name = "address_id"
    type = "S"
  }

  hash_key = "address_id"
  tags     = local.tags
}
