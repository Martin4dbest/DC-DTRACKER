AWS CLI Configuration Documentation
Overview
This guide walks through the process of setting AWS credentials on a local development environment using environment variables. By following these steps, you can securely authenticate and interact with AWS services using the AWS Command Line Interface (CLI).

Prerequisites
AWS CLI installed on your local machine.
AWS access credentials: Access Key ID, Secret Access Key, and Session Token (for temporary credentials).
Steps
1. Install AWS CLI
Ensure that you have the AWS CLI installed. If not, you can install it by following the official guide:

Install AWS CLI
2. Obtain AWS Credentials
Ensure you have the following AWS credentials from your AWS Management Console or from an IAM role you’ve assumed:

AWS Access Key ID
AWS Secret Access Key
AWS Session Token (if you are using temporary credentials, such as those from an assumed role).
3. Set AWS Environment Variables
a. Open the terminal
Open your terminal (e.g., Git Bash, PowerShell, or Command Prompt) on your local machine.

b. Set AWS Credentials as Environment Variables
Use the following commands to set the environment variables for AWS credentials (replace the placeholders with your actual values):

For Windows (Command Prompt):

bash
Copy code
set AWS_ACCESS_KEY_ID=your-access-key-id
set AWS_SECRET_ACCESS_KEY=your-secret-access-key
set AWS_SESSION_TOKEN=your-session-token
For Windows (PowerShell):

bash
Copy code
$env:AWS_ACCESS_KEY_ID="your-access-key-id"
$env:AWS_SECRET_ACCESS_KEY="your-secret-access-key"
$env:AWS_SESSION_TOKEN="your-session-token"
For Linux/MacOS or Git Bash:

bash
Copy code
export AWS_ACCESS_KEY_ID=your-access-key-id
export AWS_SECRET_ACCESS_KEY=your-secret-access-key
export AWS_SESSION_TOKEN=your-session-token
Make sure to replace the your-access-key-id, your-secret-access-key, and your-session-token with the actual credentials you received.

4. Verify Environment Variables
After setting the environment variables, verify that they have been correctly set by running the following commands:

For Linux/MacOS or Git Bash:

bash
Copy code
echo $AWS_ACCESS_KEY_ID
echo $AWS_SECRET_ACCESS_KEY
echo $AWS_SESSION_TOKEN
For Windows (Command Prompt):

bash
Copy code
echo %AWS_ACCESS_KEY_ID%
echo %AWS_SECRET_ACCESS_KEY%
echo %AWS_SESSION_TOKEN%
These commands will display the values of the respective environment variables. If you see the correct values, the credentials are set up properly.

5. Test AWS CLI Configuration
To verify that your credentials are working correctly, run the following command to check your AWS account identity:

bash
Copy code
aws sts get-caller-identity
This command will return information about the current IAM user or role associated with your credentials, confirming that the setup is successful.

6. Using AWS CLI
Once the credentials are successfully set up, you can begin using AWS CLI commands to interact with various AWS services. For example, to list your S3 buckets:

bash
Copy code
aws s3 ls
7. Persistent Configuration (Optional)
If you prefer not to set the environment variables every time you start a new session, you can store them in the AWS credentials file (~/.aws/credentials for Unix-based systems or C:\Users\USERNAME\.aws\credentials for Windows) or configure them as profiles in AWS CLI.

To configure profiles:

Run aws configure to enter your credentials interactively.
Or manually edit the credentials file to add your AWS credentials.
Example of the ~/.aws/credentials file:

ini
Copy code
[default]
aws_access_key_id = your-access-key-id
aws_secret_access_key = your-secret-access-key
aws_session_token = your-session-token
Conclusion
This setup allows you to securely authenticate to AWS using environment variables, ensuring that you can interact with AWS resources without hardcoding your credentials. Always remember to secure your credentials, especially when working with temporary credentials.

