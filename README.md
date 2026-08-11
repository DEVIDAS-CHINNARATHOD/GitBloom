# GitBloom

Increase your Git commit history and build green streaks on your GitHub profile effortlessly with backdated commits.

## How to Use

### 1. Create a New Private Repository on GitHub
1. Go to [GitHub](https://github.com) and log in.
2. Click the **+** icon in the top right corner and select **New repository**.
3. Name your repository (e.g., `my-repo`).
4. Set the visibility to **Private** (recommended) or Public.
5. Click **Create repository**.
6. Copy the repository URL (e.g., `https://github.com/your-username/my-repo.git`).

### 2. Download and Run the Script
1. Download or clone this project folder to your local machine.
2. Open your terminal or command prompt inside the project directory.
3. Run the script:
   ```bash
   python main.py
   ```

### 3. Script Process & Prompts
When the script runs, enter the required details when prompted:
- **Repository URL**: Paste the GitHub repository URL you copied in Step 1.
- **File name**: Enter a file name to update (e.g., `notes.txt`).
- **From date**: Enter the start date in `DDMMYYYY` format (e.g., `01012024`).
- **Till date**: Enter the end date in `DDMMYYYY` format (e.g., `31122024`).
- **Number of commits**: Enter the number of backdated commits to create (e.g., `300`).
- **Push commits**: Type `y` to push all generated commits to your GitHub repository.

### 4. Make Green Streaks Visible on Profile
If you used a **Private Repository**, enable private contributions so your green streaks display on your GitHub profile calendar:
1. Go to your **GitHub Profile** page (`https://github.com/your-username`).
2. Above your contribution activity graph on the right, click **Contribution settings**.
3. Select **"Include private contributions on my profile"**.
