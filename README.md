# AWS Amazon Alexa and Amazon Bedrock Integration

Generative AI is based on large foundation models trained on vast data, capable of generating text, images,
audio, code, and more. However, the data may be outdated or lack context, and the models struggle with structured
data and deterministic responses. This can lead to hallucinations, where the model generates outputs not grounded
in input data or factual knowledge. For example, when summing values in a table, the model may "invent" random or
inconsistent numbers instead of performing calculations correctly. This inability to interpret rows, columns, and
cells adequately, along with complex relationships, can lead to errors in identifying maximum, minimum, and other
mathematical operations. Hallucination and imprecision issues are critical for sensitive data like financial, medical,
or scientific information, compromising the reliability of AI-based applications. One approach to address
hallucinations when answering questions with structured data context is to use models to generate SQL queries based on
natural language input instead of directly interpreting tables and performing operations.

This sample is a walk through of scripts that were made to quickly setup a sample Alexa Skill to integrate with LLM
in Amazon Bedrock. The users can have insights from database files using Natural Languange. This sample use AWS Glue
and AWS Athena to query the data storaged in Amazon S3. The LLM from Anthropic has a library of prompts, with various
examples for different use cases, including the [SQL Sorcerer](https://docs.anthropic.com/en/prompt-library/sql-sorcerer)
prompt for generating SQL queries. With this approach, it is possible to generate SQL code from natural language
and orchestrate the execution of that query using database services, ultimately generating a user-friendly response for the end-user.

<p align="center">
<img src="/images/alexa-bedrock-integration.png" width="550">
</p>

## Requirements

You will need:

- [an Alexa account](https://alexa.amazon.com/)
- [an Alexa Skill](https://developer.amazon.com/alexa/console/ask)
- CSV database files (sample files can found [here](https://moduloextratorpnp.mec.gov.br/))
- [AWS CLI](https://docs.aws.amazon.com/pt_br/cli/latest/userguide/getting-started-install.html)
- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)

### Demo walkthrough

1. Create an Alexa Skill as **Custom Model** and for Hosting service choose **Provision your own**. Import [this template for your Skill](./alexa/skill.json) in Interaction Model. You can check [Alexa Developer Documentation](https://developer.amazon.com/en-US/docs/alexa/custom-skills/steps-to-build-a-custom-skill.html).
2. In the Alexa Developer console go to <b>Build/Endpoint<b> and get the <b>Skill ID</b> and Deploy the [sample](./src/README.md).
3. Go back to Alexa Developer console and change the <b>AWS Lambda ARN</b> (you can find the ARN at the SAM output). Save and click on "Build skill".
4. Upload CSV files to S3 Bucket (you can find the Bucket name at the SAM output). Create one folder per file.
5. Test the Skill.

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

See [LICENSE](LICENSE) for more information
