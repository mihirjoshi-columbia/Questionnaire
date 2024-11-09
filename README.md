# Questionnaire Matching System

## Setup

1. Clone the repository:

```bash
git clone https://github.com/yourusername/Questionnaire.git
cd Questionnaire
```

2. Install required packages:

```bash
pip install -r requirements.txt
```

3. Set up your environment:
   - Copy `.env.template` to create your `.env` file:
   ```bash
   cp .env.template .env
   ```
   - Edit `.env` and add your OpenAI API key

4. Run the matching system:
```bash
python matching.py
```

## Security Notes
- Never commit your `.env` file
- Never share your API keys
- Regularly rotate your API keys if you suspect they've been compromised
```

6. Create a requirements.txt file:

```text:requirements.txt
pandas
numpy
python-dotenv
openai
```

If you've already accidentally committed your API key:

1. Immediately revoke the exposed key in your OpenAI dashboard
2. Generate a new API key
3. Update your local .env file with the new key
4. Use git filter-branch to remove the key from your git history:

```bash
git filter-branch --force --index-filter \
"git rm --cached --ignore-unmatch path/to/file/with/key" \
--prune-empty --tag-name-filter cat -- --all
```

Additional Security Tips:
1. Consider using GitHub Secrets if you're using GitHub Actions
2. Use API key rotation practices
3. Set up API key usage limits in your OpenAI dashboard
4. Consider using a service like HashiCorp Vault for production deployments

Remember:
- Never commit API keys or sensitive credentials
- Always use environment variables for sensitive data
- Regularly audit your repository for sensitive information
- Use GitHub's security alerts and dependency scanning

These practices will help keep your API key secure while still allowing others to use your project by adding their own API keys.