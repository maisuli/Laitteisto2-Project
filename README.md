# FYI for Keijo

Here is our working repository, if you wish to see the editing history or check our code out a bit further (because the version here is obviously not perfect): https://github.com/maisuli/Laitteisto2
 
# Hardware 2 Project - Group 9

<h2>Installation </h2>

<h3>1. Make sure you have Git, Python and mpremote installed!</h3>

<ul>
  
<li>
Check Git installation

<code>git --version</code> - Output should be your Git version. If output is "command not found" etc, install Git from https://git-scm.com/downloads. 
</li>

<li>
Check Python version (if you see a version, Python is installed)

<code>python --version</code>
</li>

<li>
To install MicroPython remote control aka mpremote:

<code>pip install mpremote</code> or <code>python -m pip install mpremote</code>
</li>

</ul>
<h3>2. Clone repository and install libraries</h3>

Go to the directory you want to clone the repository to and run the following:

<code>git clone --recurse-submodules https://github.com/maisuli/Laitteisto2-Project.git</code>

<h3>3. Install the programme</h3>
  
Go to the cloned directory and run the following:

Windows PowerShell or cmd: <code>.\install.cmd</code>

Linux, OSX or GitBash: <code>.\install.cmd</code>

<h3>(4. Pull submodule updates)</h3>

To pull all updates made to the submodule, run the following:

<code>git submodule update --recursive --remote</code>
