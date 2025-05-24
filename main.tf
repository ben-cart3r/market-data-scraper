data "aws_caller_identity" "current" {}

module "function" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "7.8.1"

  create_function = var.create
  create_package  = var.create_package
  create_role     = var.create

  function_name = "${var.name_prefix}-market-data-scraper"
  description   = "Scrape the daily close position of a given ticker"
  handler       = "src/lambda_handler.handle_event"
  runtime       = "python3.13"
  timeout       = 30

  attach_policy_json = var.create
  policy_json        = var.create ? data.aws_iam_policy_document.function[0].json : null

  source_path = [
    {
      path           = "${path.module}/function"
      patterns       = ["!tests/.*"]
      poetry_install = true
    }
  ]

  environment_variables = {
    TABLE_NAME = var.table_name
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.name_prefix}-market-data-scraper"
    }
  )
}

data "aws_iam_policy_document" "function" {
  count = var.create ? 1 : 0

  statement {
    effect = "Allow"

    actions = [
      "dynamodb:PutItem",
    ]

    resources = [
      "arn:aws:dynamodb:eu-west-1:${data.aws_caller_identity.current.account_id}:table/${var.table_name}"
    ]
  }
}
