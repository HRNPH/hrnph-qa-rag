# Overview

## Get Started

```bash
pf flow build --source ./rag-services/strategy-tag-rewrite --output ./release --format docker
docker build -t hrnph/qa-rag:latest ./rag-services/strategy-tag-rewrite/dist
docker run -p 8080:8080 --env-file ./.env hrnph/qa-rag:latest
```
