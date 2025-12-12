data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/lambda_src"
  output_path = "${path.module}/lambda_package.zip"
}

resource "aws_lambda_function" "etl" {
  function_name = "${local.name_prefix}-${random_id.suffix.hex}-etl"
  role          = aws_iam_role.etl_lambda_role.arn
  handler       = "handler.lambda_handler"
  runtime       = "python3.12"
  filename      = data.archive_file.lambda_zip.output_path
  timeout       = 30
  memory_size   = 256
  tags          = var.tags

  # re-upload when the ZIP changes
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
}