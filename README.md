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
<!-- END_TF_DOCS -->