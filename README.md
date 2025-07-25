# SFSChain

<p align="center">
  <img src="https://www.univpm.it/Entra/Immagini/Icone/logo_univpm/LOGO_UNIVPM_390x154px.gif" alt="UNIVPM Logo">
</p>

## Table of Contents

- [SFSChain](#sfschain)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
    - [Overview](#overview)
    - [Technologies Used to Develop](#technologies-used-to-develop)
  - [Installation](#installation)
    - [Requirements](#requirements)
    - [Setup in UNIX-like OS's](#setup-in-unix-like-oss)
    - [Setup in Windows](#setup-in-windows)
  - [How to use it](#how-to-use-it)
    - [First look](#first-look)
  - [Contributors](#contributors)

## Introduction

Welcome to SFSChain, a decentralized DApp platform built on blockchain technology.
SFSChain stands for Sustainable Food Supply Chain, which is the core theme of this university project, developed as part of the course "Software Security and Blockchain".
The platform showcases how blockchain can enable secure, transparent, and traceable management of CO₂ emissions across the food supply chain, promoting sustainability and accountability among all stakeholders.

### Overview

SFSChain is a university project aimed at enabling secure and transparent management of CO₂ emissions in the sustainable food supply chain. Leveraging Ethereum for data immutability and integrity, and Python for off-chain operations, SFSChain fosters responsible interaction between stakeholders such as farmers, producers, carriers, and sellers. The application allows each participant to register operations, transfer carbon credits, and track green actions in a verifiable way. With privacy-preserving mechanisms and role-based access control, SFSChain ensures that data is securely shared and actions are traceable, promoting environmental accountability through a decentralized approach.

### Technologies Used to Develop

- [Python](https://www.python.org/) -> Main programming language
- [Sqlite3](https://www.sqlite.org/) -> Database used
- [Ganache](https://archive.trufflesuite.com/ganache/) -> Personal blockchain as Ethereum simulator used in Class (current code does not work with Ganache)
- [Web3](https://web3py.readthedocs.io/en/stable/) -> Python library for interacting with Ethereum
- [Docker](https://www.docker.com/) and [Docker-compose](https://docs.docker.com/compose/) -> Containerization
- [Solidity](https://soliditylang.org/) -> Smart contract development
- [Py-solc-x](https://solcx.readthedocs.io/en/latest/) -> Solidity compiler
- [Remix](https://remix-project.org/?lang=it) -> Contract testing framework
- [Besu](https://besu.hyperledger.org) -> Private blockchain for testing

## Installation

In order to run our application, you need to follow a few steps.

### Requirements

Before getting started, make sure you have installed Docker on your computer. Docker provides an isolated environment to run applications in containers, ensuring the portability and security of project components. You can run the Docker installation file from the following [link](https://www.docker.com/).

Also, make sure you have installed `git` on your computer. In **Windows** systems, you could download [here](https://git-scm.com/download/win) the latest version of **Git for Windows**. In **UNIX-like** operating systems, you could run the following command:

```bash
sudo apt install git
```

### Setup in UNIX-like OS's

First, you need to clone this repository. In order to do that, you can open your command shell and run this command:

```bash
git clone https://github.com/andreagiuliani3/SFSChain
```

Then, make sure you are placed in the right directory:

```bash
cd SFSChain
```

You can run the following command if you want to re-build Docker's image:

```bash
docker-compose build --no-cache
```

Now, you can initiate the process of creating and starting the Docker containers required to host the Ethereum blockchain by running the following simple command:

```bash
docker-compose up -d
```

> ⚠️ **IMPORTANT NOTE ON NETWORK CONFIGURATION**  
> This project uses a **custom Docker subnet** defined in `docker-compose.yml` and referenced in the `static-nodes.json` files to enable peer-to-peer communication among the Besu nodes.  
>  
> If you encounter network-related errors when starting the containers (e.g., address conflicts or connectivity issues), it's likely due to a **conflict with an existing Docker network** or service on your machine.  
>  
> In that case, you can:
> - Change the subnet in both `docker-compose.yml` and in each `static-nodes.json` file,
> - The `static-nodes.json` files are located in the `data` directory of each node (e.g. `SFSC-Network/Node-1/data/static-nodes.json`, `SFSC-Network/Node-2/data/static-nodes.json`, etc.),
> - You can perform this change:
>   - **Directly inside the Docker container** related to the application, in which case a simple restart is sufficient:
>     ```bash
>     docker-compose down
>     docker-compose up -d
>     ```
>   - **Or on the local files (outside the container)**, but in this case you must **rebuild** the containers to apply the changes:
>     ```bash
>     docker-compose down
>     docker-compose build
>     docker-compose up -d
>     ```


You could also check if services were built properly by running `docker-compose logs`. Also, make sure your user has the proper privileges to run Docker commands. Otherwise, you can address this issue by prefixing each command with `sudo`.

> **NOTE:** The application has been tested on [Ubuntu](https://ubuntu.com/).

### Setup in Windows

To setup the application on Windows, you can basically run the same commands previously listed in your **Windows PowerShell**. Make sure you open the Shell in the project's directory.

If the docker commands do not work due to the missing *engine*, you will probably need to start [Docker Desktop](https://www.docker.com/products/docker-desktop/) in the background, which is the fastest way to start docker on Windows systems. 

## How to use it

Once the setup has been completed, you can proceed with running the main application interface with the following command:

```bash
docker exec -it sfsc-app python /app/off_chain/main.py
```

Remember to include `-it`, because `-i` ensures that the container's *STDIN* is kept open and `-t` allocates a *pseudo-TTY*, which is essential for interacting with the application via terminal. Together, these flags allow you to interact with the `sfschain` service through a command line interface.

At this point, the program is ready to be used. After executing the previous command and successfully deploying the entire infrastructure, you can interact with the application through the terminal that opens after deployment.

### Key Pair Generation and Test Credentials

To interact with the application, each user must be associated with a public/private key pair.  
You have two options:

1. **Use the provided test credentials**  
   You can find some test credentials in the file `credenziali_prova.txt`, already included in this repository. These contain pre-generated public/private key pairs you can use to test the application immediately.

2. **Generate your own key pair**  
   If you prefer to generate a new key pair, you can use the script `keygenerator.py` included in the project root.  
   Run the following command:

   ```bash
   python keygenerator.py

### First look

Upon the very first startup of the program, it will perform an application check mechanism from Docker to verify that Besu is ready to listen. If there are no errors, SFSChain will start correctly and run the first homepage.

<p align="center">
  <img src="https://github.com/andreagiuliani3/Software-Security-BESU/blob/main/first_look.png" alt="first look" width="600">
</p>


Now, you can *register* a new account as a Farmer, Carrier, Seller or Producer, or *login* if you are already enrolled, and start exploring every feature of our application.
**Enjoy it!**


## Contributors
Meet the team :

| Contributor Name      | GitHub                                  |
|:----------------------|:----------------------------------------|
| ⭐ **Andrea Giuliani**    | [Click here](https://github.com/andreagiuliani3) |
| ⭐ **Marco Di Vita**      | [Click here](https://github.com/divitamarco) |
| ⭐ **Stefano Marinucci**  | [Click here](https://github.com/MarraX99) |
