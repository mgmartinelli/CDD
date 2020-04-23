# So Our Backlog Repo Doesn't Work Anymore... Now What?

Apparently, the free version of Backlog places a 100MB storage limit on git repositories. Since we have a couple of
 large CSV files and because our algorithm outputs a lot of different files, we've used up our 100MB of space.
 
 As a solution, I've imported our Backlog repo into GitHub. From now on, our remote repo will be hosted on GitHub
  (NOT Backlog). I tried importing into the project that Kevin had set up at the beginning of the semester, but I
   wasn't able to do so (sorry Kevin!), so I had to create a new repo.
   
### Step 1: Be Invited As a Collaborator on Our New GitHub Repo
Let Mariela know your GitHub username so that she can send you an invitation to be a collaborator on the new project. 
You'll receive an email invitation to join the project. If you click on the link and get a "404 Error", make sure you
're logged into GitHub and try again. 

### Step 2: Copy the Remote URL to Your Clipboard
Go to the GitHub repo's [home][github-link] page. From there, you should see a green "Clone or download button
". Click on it. Make sure the popup that comes up is titled "Clone with HTTPS" (if it says "Clone with SSH", click on
 the blue hyperlink titled "Use HTTPS"). 
 
 Now, click on the icon that's next to the URL that looks like a clipboard with an arrow on top of it to copy the URL
  to your clipboard.
  
  >**Note:** You can copy the SSH URL if you'd prefer, but you may have to repeat the steps we went through during
> the demo to set up an SSH key. [Here's][ssh-key-instructions-link] the link to the instructions for how to generate
> and add an SSH key.

### Step 3 (Windows Users Only): Open Git Bash and Navigate To The Directory Where You Cloned the Repo
### Step 3 (Mac Users Using PyCharm): Open the CDD Project in PyCharm and Select "Terminal" From the Menu at the Bottom
### Step 3 (Mac Users / Linux Users): Open a new Terminal window and Navigate To The Directory Where You Cloned the Repo

### Step 4: Change the Remote URL of Your Local Repository
In the Terminal / Git Bash Window, type:

```bash
git remote set-url origin [paste URL you copied from GitHub here]
```

### Step 5 (PyCharm Users): Add Your GitHub Credentials to PyCharm
If you copied the HTTPS link, you'll be prompted for your GitHub credentials every time you pull/push. To avoid that
, you can add your GitHub Credentials to PyCharm by:

#### Step 5a: Go to the PyCharm Settings / Preferences Dialog
#### Step 5b: Select the arrow next to Version Control, then select GitHub
#### Step 5c: Click "Add Account". Enter you're GitHub credentials.

### Step 6: Test Access
If you're using PyCharm, you can test your access by going to VCS > Git > Branches
Then click on the "origin/num_voting_booths" branch and select "Checkout". If it was able to checkout successfully
, your access has been set-up correctly. If it wasn't, send a message in Slack so we can help.

<!-- Markdown links -->

[localhost-link]: http://localhost:8000/
[virtualenv-link]: https://virtualenv.pypa.io/en/latest/installation.html
[pip-link]: https://pip.pypa.io/en/stable/installing/
[pycharm-virtualenv-link]: https://www.jetbrains.com/help/pycharm/creating-virtual-environment.html
[github-link]: https://github.com/mgmartinelli/CDD
[ssh-key-instructions-link]: https://help.github.com/en/github/authenticating-to-github/adding-a-new-ssh-key-to-your-github-account