# CustomImgSearch
CustomImgSearch allows you to compare an image query against your own images. If a match is found, the image is stored with your applied filters.

## Git Configuration Setup

Follow these steps to configure Git for the project:

### 1. Clone the Repository
Clone the project repository to your local machine:
```bash
git clone https://github.com/yourusername/CustomImgSearch.git
````

### 2. Set Up Your .env File
Copy the example .env file to create your own configuration file:

```bash
cp .env-sample .env
Edit the .env file and add your GitHub username and email:
```
```env
GIT_USER_NAME=YourGitHubUsername
GIT_USER_EMAIL=your-email@example.com
```

### 3. Run the Setup Script
Run the provided setup script to configure Git with your username and email:

```bash
./scripts/set_git_config.sh
```

# Notes

Ensure your .env file is never committed to the repository by adding it to .gitignore.

Each collaborator should create their own .env file and run the setup script to personalize their Git configuration.

This workflow guarantees that all collaborators' commits are correctly attributed to their GitHub accounts.


This version simplifies and clarifies the steps, using consistent headings and a more intuitive flow. It also includes helpful notes about `.gitignore` to ensure security. Let me know if you'd like further tweaks!
