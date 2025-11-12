data "aws_iam_policy_document" "lambda_assume" {
    statement {
      actions = ["sts:AssumeRole"]
      principals {
        type = "Service"
        identifiers = ["lambda.amazonaws.com"]
      }
    }
}

resource "aws_iam_role" "etl_lambda_role" {
    name               = "${loca.name_prefix}-${random_id.suffix.hex}-lambda-role"
    assume_role_policy = data.aws_iam_policy_document.lambda_assume.json
    tags               = var.tags
}

# Basic logging
resource "aws_iam_role_policy_attachment" "lambda_basic_logs" {
    role = aws_iam_role.etl_lambda_role.name
    policy_arn = "arn:aws:iam:aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Inline policy for S3 access to the artifacts bucket
data "aws_iam_policy_document" "lambda_s3_access" {
    statement {
      actions = [
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket"
      ]
      resources = [
        aws_s3_bucket.artifacts.arn,
        "${aws_s3_bucket.artifacts.arn}/*"
      ]
    }
}

resource "aws_iam_policy" "lambda_s3_policy" {
    name    = "${local.name_prefix}-${random_id.suffix.hex}-lambda-s3"
    policy  = data.aws_iam_policy_document.lambda_s3_access.json
}

resource "aws_iam_role_policy_attachment" "lambda_s3_attach" {
  role = aws_iam_role.etl_lambda_role.name
  policy_arn = aws_iam_policy.lambda_s3_policy.arn
}