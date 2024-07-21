# AWS Amazon Alexa and Amazon Bedrock Integration

Generative AI is based on large foundation models trained on vast data, capable of generating text, images,
audio, code, and more. However, the data may be outdated or lack context, and the models struggle with structured
data and deterministic responses. This can lead to hallucinations, where the model generates outputs not grounded
in input data or factual knowledge. For example, when summing values in a table, the model may "invent" random or
inconsistent numbers instead of performing calculations correctly. 

This inability to interpret rows, columns, and cells adequately, along with complex relationships, can lead to 
errors in identifying maximum, minimum, and other mathematical operations. Hallucination and imprecision issues 
are critical for sensitive data like financial, medical, or scientific information, compromising the reliability 
of AI-based applications. One approach to address hallucinations when answering questions with structured data 
context is to use models to generate SQL queries based on natural language input instead of directly interpreting 
tables and performing operations.

This sample is a walk through of scripts that were made to quickly setup a Alexa Skill sample to integrate with LLM
in Amazon Bedrock. The users can have insights from database files using Natural Languange. This sample use AWS Glue
and AWS Athena to query the data storaged in Amazon S3. The LLM from Anthropic has a library of prompts, with various
examples for different use cases, including the [SQL Sorcerer](https://docs.anthropic.com/en/prompt-library/sql-sorcerer)
prompt for generating SQL queries. With this approach, it is possible to generate SQL code from natural language
and orchestrate the execution of that query using database services, ultimately generating a user-friendly response for the end-user.

<p align="center">
<img src="/images/alexa-bedrock-integration.png" width="550">
</p>

## Requirements

Before start, you will need:

- [an Alexa account](https://alexa.amazon.com/)
- [an Alexa Skill](https://developer.amazon.com/alexa/console/ask)
- CSV database files (sample files can found [here](https://moduloextratorpnp.mec.gov.br/))
- [AWS CLI](https://docs.aws.amazon.com/pt_br/cli/latest/userguide/getting-started-install.html)
- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)

### Demo walkthrough

1. Clone the project to your computer
2. When you will work with the CSV files, use logical names in the columns, so change the header line in the CSV files
3. Edit the [context file](./src/lambda/alexa-skill/resources/context.txt) to reflect your database structure (tables, columns and keys following the [Anthropic documentation](https://docs.anthropic.com/en/prompt-library/sql-sorcerer)
4. Go to the Alexa Developer console and create an Alexa Skill, choose a name for the skill and this name will be the invocation word for your skill. Select a **Custom Model** and for Hosting service choose **Provision your own**. After created the skill, go to skill home and in **Interaction Model\JSON Editor** copy and paste the content of [this template for your Skill](./alexa/skill.json). You can check [Alexa Developer Documentation](https://developer.amazon.com/en-US/docs/alexa/custom-skills/steps-to-build-a-custom-skill.html).
5. In the Alexa Developer console go to **Endpoint\Your Skill ID** and get the **Skill ID** to use as a param to Deploy the solution following the [sample](./src/README.md).
6. After deploy the sample, get the **AlexaSkillFunction ARN** in the SAM script output and go back to Alexa Developer console to change the <b>AWS Lambda ARN</b> in **Endpoint\Default Region**.
7. Save the skill and click on **Build skill**.
9. Upload the CSV to S3 Bucket (you can find the Bucket name at the SAM output). Inside the S3 bucket, create one folder per CSV file.
11. Test the Skill.

### IMPORTANT NOTES

<ul>a) Check the database structure and update the context file, this file will be deployed inside the Skill Lambda function, to edit this file, use an IDE like VSCode and after change run **sam build && sam deploy** to update the file in Lambda function. 
<br><br>
b) Remember to change the CSV header line with **LOGICAL** names, for example, in a column with the Student ID identified by "id_stds", replace to "STUDENTS_ID".
<br><br>
c) Check the decimal numbers separator, replace comma ( , ) to dot ( . ). 
</ul>
## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

See [LICENSE](LICENSE) for more information
