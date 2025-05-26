# market-data-scraper
Terraform module to create a lambda function that scrapes the daily close position of a given ticker.

## Usage

```hcl

module "market-data-scraper" {
  source = "https://github.com/ben-cart3r/market-data-scraper"
  version = "v0.1"

  tags             = local.tags
}
```
<!-- BEGIN_TF_DOCS -->
## Requirements

No requirements.

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | n/a |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_function"></a> [function](#module\_function) | terraform-aws-modules/lambda/aws | 7.21.0 |

## Resources

| Name | Type |
|------|------|
| [aws_caller_identity.current](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/caller_identity) | data source |
| [aws_iam_policy_document.function](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/iam_policy_document) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_create"></a> [create](#input\_create) | Controls whether resources should be created. | `bool` | `true` | no |
| <a name="input_create_package"></a> [create\_package](#input\_create\_package) | Controls whether Lambda package should be created. Can be used with var.create=false to ensure the function package builds during CI. | `bool` | `true` | no |
| <a name="input_name_prefix"></a> [name\_prefix](#input\_name\_prefix) | Prefix to apply to all resource names. | `string` | `""` | no |
| <a name="input_table_name"></a> [table\_name](#input\_table\_name) | The name of the dynamodb table that holds market data. | `string` | n/a | yes |
| <a name="input_tags"></a> [tags](#input\_tags) | A map of tags to assign to resources. | `map(string)` | `{}` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_lambda"></a> [lambda](#output\_lambda) | Attributes associated with the lambda function. |
<!-- END_TF_DOCS -->