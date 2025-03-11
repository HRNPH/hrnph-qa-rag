# Overview

## Get Started

```bash
pf flow build --source ./rag-services/strategy-tag-rewrite --output ./release --format docker
docker build -t hrnph/qa-rag:latest ./rag-services/strategy-tag-rewrite/dist
docker run -p 8080:8080 --env-file ./.env hrnph/qa-rag:latest
```

### GH Cli, Release

```bash
gh release create v0.0.6-strategy-tag-rewrite --title "v0.0.6-strategy-tag-rewrite" --notes "Fix Boolean Validation" --generate-notes
```

### Terraform

```bash
cd terraform
terraform plan -var-file="local.tfvars" -destroy -out ./destroy.tfplan -parallelism=1
terraform apply --parallelism=1 -destroy ./destroy.tfplan

terraform refresh -var-file="local.tfvars"
terraform plan -var-file="local.tfvars" -out ./init.tfplan -parallelism=1
terraform apply --parallelism=1 ./init.tfplan
```
