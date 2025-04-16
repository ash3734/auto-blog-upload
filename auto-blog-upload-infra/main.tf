provider "aws" {
  region = "us-west-2"
}

resource "aws_s3_bucket" "static_assets" {
  bucket = "auto-reply-service-static-assets"
  acl    = "private"
}

resource "aws_dynamodb_table" "user_data" {
  name           = "UserData"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "UserId"

  attribute {
    name = "UserId"
    type = "S"
  }
}

resource "aws_lambda_function" "auto_reply" {
  function_name = "AutoReplyFunction"
  role          = aws_iam_role.lambda_exec.arn
  handler       = "index.handler"
  runtime       = "nodejs14.x"
  filename      = "lambda_function_payload.zip"
  
  source_code_hash = filebase64sha256("lambda_function_payload.zip")
  
  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.user_data.name
    }
  }
}

resource "aws_api_gateway_rest_api" "auto_reply_api" {
  name        = "AutoReplyAPI"
  description = "API for the Auto Reply Service"
}

resource "aws_api_gateway_resource" "proxy" {
  rest_api_id = aws_api_gateway_rest_api.auto_reply_api.id
  parent_id   = aws_api_gateway_rest_api.auto_reply_api.root_resource_id
  path_part   = "{proxy+}"
}

resource "aws_api_gateway_method" "proxy" {
  rest_api_id   = aws_api_gateway_rest_api.auto_reply_api.id
  resource_id   = aws_api_gateway_resource.proxy.id
  http_method   = "ANY"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda" {
  rest_api_id = aws_api_gateway_rest_api.auto_reply_api.id
  resource_id = aws_api_gateway_resource.proxy.id
  http_method = aws_api_gateway_method.proxy.http_method
  type        = "AWS_PROXY"
  uri         = aws_lambda_function.auto_reply.invoke_arn
}

resource "aws_iam_role" "lambda_exec" {
  name = "lambda_exec_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_policy" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
} 