# Paper comparing the state-of-the-art GAN models

[Exploration of the synthesis image generation taskby applying state-of-the-art network architectureswith different parameters](./readme_dia/paper.pdf)

# Table of Contents

1.  [Creating a virtual machine](#org1677977)
    1.  [Google cloud](#org2ce269d)
        1.  [Making account and setting up billing](#orge672a7e):ATTACH:
        2.  [Requesting GPU quota and launching virtual machine](#org224df02):ATTACH:
    2.  [Azure student sponsorship](#org34cc87e)
2.  [Connecting to servers](#org5e6856d)
    1.  [Windows](#org02a6211)
        1.  [SSH](#org5ebc47d)
            1. [Generating your keypair](#keypair)
            2. [Adding your keypair to a Google Cloud instance](#addingkeypairtoinstance)
3. [Working with your server](#workServer)
    1.  [git](#gitServer)
    2.  [tmux](#org7e8c79b)
    3.  [Google drive from commandline](#orgb74b1e9)
        1.  [Install](#driveInstall)
        2.  [Usage](#driveUsage)

<a id="org1677977"></a>

# Creating a virtual machine


<a id="org2ce269d"></a>

## Google cloud


<a id="orge672a7e"></a>

### Making account and setting up billing     :ATTACH:

1.  Make an account using your credit card info with this link <https://cloud.google.com/free>, if everything went alright you will be greeted by the google cloud home screen.

![img](./readme_dia/img1.png)

2.  On the home screen there is a search bar, type: `billing`, it should show a screen similar to this one, which is the most important to us!:

![img](./readme_dia/img2.png)

3.  In the bottom right you should see an option to upgrade your account to a paid account, we need this because otherwise we are locked out of requesting GPUs. Click it, and you should see a message reassuring that you will only start paying once your usage exceeds the 250 free trial credits.

4.  On the billing screen we also see health checks, click `View all health checks`. You should see this screen.

![img](./readme_dia/img3.png)

5.  Click on create budget, you will need to give your budget a name and specify an amount. I gave the following `prproj` and `250`. Follow the default options for other steps. **In this way you will be alerted via email when your spending exceeds 50, 90 and 100 percent, but does NOT put a hard cap on your budget.**

6.  For hard caps and automatic instance stopping we need to do extra steps from <https://cloud.google.com/billing/docs/how-to/notify#functions_billing_auth-python>


<a id="org224df02"></a>

### Requesting GPU quota and launching virtual machine     :ATTACH:

1.  Now that we have our account ready, we can request GPUs. Type: `all quota` into the search bar. You should see a screen like this (note that I already did these steps):

![img](./readme_dia/img4.png)

2.  The important quota is `GPUs (all regions)` which is 0 by default. I requested 1 GPU by doing the following, but maybe we can do more. First use the `filter table` by clicking on the icon, and selecting metric from the drop down menu. Then type `gpus_all_regions.`

![img](./readme_dia/img5.png)

![img](./readme_dia/img6.png)

3.  In the GPUs (all regions) quota row click `ALL QUOTAS`,

![img](./readme_dia/img7.png)

tick the box, and then click `EDIT QUOTAS`,

![img](./readme_dia/img8.png)

this is the important screen, fill in the number of GPUs you want, fill in a request motivation (I put Utrecht University masters student), and click `NEXT`.

4.  Follow any steps, (can&rsquo;t remember) and if everything went alright you will receive an email within minutes saying your request has been approved.

5.  For more information on the following steps see: <https://cloud.google.com/ai-platform/deep-learning-vm/docs/pytorch_start_instance> and <https://cloud.google.com/compute/docs/gpus/gpu-regions-zones> (I now realised my mistake of making a GPU in asia-east, when the same is available in europe, I deleted the instance)

6.  The only way I could find to make a *preemptible* virtual machine was with the Cloud Console or the gcloud command line tool, using this link <https://cloud.google.com/ai-platform/deep-learning-vm/docs/pytorch_start_instance>. I assume you can use the gcloud command line tool here, more info could be found here <https://cloud.google.com/shell/docs/using-cloud-shell> or <https://cloud.google.com/sdk/docs/install>.

7.  The relevant code snippet that will **DEPLOY** a virtual machine right away is:

```sh
export IMAGE_FAMILY="pytorch-latest-gpu"
export ZONE="europe-west4-[abc]"
export INSTANCE_NAME="my-instance"
export BOOT_DISK_SIZE="100GB"

gcloud compute instances create $INSTANCE_NAME \
  --zone=$ZONE \
  --image-family=$IMAGE_FAMILY \
  --boot-disk-size=$BOOT_DISK_SIZE \
  --image-project=deeplearning-platform-release \
  --maintenance-policy=TERMINATE \
  --accelerator="type=nvidia-tesla-v100,count=1" \
  --metadata="install-nvidia-driver=True" \
  --preemptible
```

You can change the `INSTANCE_NAME`, `IMAGE_FAMILY`, and `count` of gpus (if you have enough quota!).

![img](./readme_dia/img9.png)

**remember to stop the instance if you will not use it right away!!!**

8. You can stop the instance by typing: `vm instances` in the search bar. Then you should see a screen with a list of your instances, running or not. Click the instance you just made and click the `stop` icon.

<a id="org34cc87e"></a>

## Azure student sponsorship


<a id="org5e6856d"></a>

# Connecting to servers


<a id="org02a6211"></a>

## Windows


<a id="org5ebc47d"></a>

### SSH into your server

<a id="org7e8c79b"></a>

#### Generating your keypair

<a id="keypair"></a>

  1. We are using this guide, <https://cloud.google.com/compute/docs/instances/connecting-advanced#windows-putty>. Download putty here <https://www.putty.org>.

2. First we need to generate the public-private ssh keypair, to do this go to (on windows): *Start* > *Programs* > *PuTTY* > *PuTTYgen*

3. Click `SSH-2 RSA` as the type of key to generate. (leave everything as is)

4. Click Generate and then move the cursor around the blank area of the Key section to generate the random characters that create a unique key. When the key has been completely generated, the information about the new key is displayed in the Key section. (Do not modify the Key fingerprint or the Key comment fields; this can cause your key to no longer be valid.)

5. Save the public key by: 1. Click Save private key. The PuTTYgen Warning panel is displayed. 2. Click Yes to save the private key without a passphrase. 3. Type icat as the name of the private key, and specify the location where you want to save the private key. For example, you can create a directory on your computer called keys to store both the public and private keys. It is recommended that you save your public and private keys in the same location.

6. Click Save.

7. Close the PuTTY Key Generator window.

#### Adding your public key to your Google Cloud instance

<a id="addingkeypairtoinstance"></a>

1. Go to the google cloud search bar, type: `vm instances`, you should see your created instance you want to connect to.

![img](./readme_dia/img10.png)

2. Click on the **name** of the instance you created to go to instance details.

![img](./readme_dia/img11.png)

3. Then click the `edit` button. Scroll down to the SSH keys section, then paste
   the contents of your public ssh key into the box, and click add ssh key. (your public ssh key should be in a .pub file)

![img](./readme_dia/img12.png)

4. Click `save` at the bottom to stop editing.

#### Starting your instance and connecting using PuTTY! (the part where you can prepare to start your job)

1. If everything went alright we can now follow this guide: <https://cloud.google.com/compute/docs/instances/connecting-advanced#windows-putty>.

2. Start your virtual machine instance using the play button on the virtual machine page on google cloud. There should now be an external ip-address listed in the row of your instance. We need this to connect.

3. Open PuTTY by launching putty.exe. A connection configuration window opens.

4. In the Host Name field, enter the username associated with the SSH key, and the external IP address of the instance that you want to connect to. Use the following format:

``` sh
USERNAME@EXTERNAL_IP
```

Replace the following:

USERNAME: the username of the user connecting to the instance. This must be the username you specified when you created the SSH key.
(If you don't know your username, it is also at the end of you public SSH key in the .pub file.)

EXTERNAL_IP: the external IP address of the instance that you want to connect to. (The thing we saw when starting the instance.)

![img](./readme_dia/img13.png)

5. In the Category menu, navigate to Connection > SSH > Auth.

6. In the Private key file for authentication field, browse to the location of your private key file.

![img](./readme_dia/img14.png)

7. Click Open to open a terminal with a connection to your instance.

After you connect, run commands on your instance using this terminal. When you finish, disconnect from the instance by running the exit command.

# Working with your server

<a id="workServer"></a>

## git

<a id="gitServer"></a>

I assume people know how to use git from the command line, but here are the two most used commands:

1. Clone the code using http, can not upload files larger than 500mb, but that should not be a problem for us.

``` sh
git clone https://github.com/Vinkage/pr_project
```

2. Checkout some branch using the branchname.

``` sh
git checkout [main|mike]
```


## tmux

<a id="orgb74b1e9"></a>

What is tmux : <https://en.wikipedia.org/wiki/Tmux>

I can recommend using screen or tmux. These protect your jobs, for example if
you start a job in tmux and disconnect from the server with SSH, you can be sure
the job will continue inside tmux. Otherwise, disconnecting from the server with
ssh also stops your job!

To install it type this in the linux server command line:

``` sh
sudo apt install tmux
```

I won't go into depth on tmux, but there are only a few commands we need to know
to use it.

1. To create a named tmux session, use

``` sh
tmux new -s my-session
```

you will see a terminal that looks similar to this,

![img](./readme_dia/img15.png)

indicating you are now inside the tmux session. Feel free to run any commands
here as usual, and finally start your long-running job when you are ready.

2. When you are ready to exit the tmux session press the follow key sequence,
   `Ctrl-B` then `d`. This is the standard keybinding for detaching from your
   tmux session. You should now be back in your standard terminal session.

3. Now with your job running in the "background" or in tmux, you can disconnect
   from the server if you want. **Be careful not to move any files that are
   being used by your job!!!**

4. If you want to see how your job is doing at any moment we need to re-enter the tmux session,

``` sh
tmux attach-session -t my-session
```

which should take you back to the tmux session.

## Google Drive from a commandline


<a id="orgf22c3ce"></a>

drive command line tool github repo: <https://github.com/odeke-em/drive>

Since we are working with datasets and we need to transfer them to servers, I
chose to install the google drive command line tool.

It actually works very similar to git, it mounts your google drive disk as a
directory, and then you can pull and push changes by using commands while inside
this directory.

### Install

<a id="driveInstall"></a>

Assume you start in home directory,

Download the go archive:

```
curl -O https://dl.google.com/go/go1.12.7.linux-amd64.tar.gz
```

Unzip it:

```
tar xvf go1.12.7.linux-amd64.tar.gz
```

Make sure you own it:

```
sudo chown -R root:root ./go
```

Make directory where go installs things:

```
mkdir gopath
```

Make sure linux knows where go is installed ($HOME/go) (make sure you copy it correct, the arrows are weird):

```
cat << ! >> ~/.bashrc
export GOPATH=\$HOME/gopath
export PATH=\$GOPATH:\$GOPATH/bin:\$PATH
export GOROOT=\$HOME/go
export PATH=\$GOROOT:\$GOROOT/bin:\$PATH
!
source ~/.bashrc # To reload the settings and get the newly set ones # Or open a fresh terminal
```

Run this command and wait a while:

```
go get -u github.com/odeke-em/drive/cmd/drive
```

### Usage

<a id="driveUsage"></a>

1. Enter this to init the google drive, you might be prompted to go to a url and
   copy paste an authorisation code into the terminal.

``` sh
drive init ~/gdrive
cd ~/gdrive
```

2. Pull the files from your drive to the server using the following snippet, you
   might need to add some options.

``` sh
drive pull
```
