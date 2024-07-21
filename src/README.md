# Backend

## Build & Deploy

Before run the follow commands change the **SkillID** and check the **Region**

```bash
cd src/
sam validate
sam build
sam deploy --parameter-overrides SkillID=00000000 --stack-name alexa-bedrock-integration  --region us-east-2 --capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_IAM --resolve-s3
```

## Delete

```bash
sam delete --stack-name alexa-bedrock-integration --region us-east-2
```
