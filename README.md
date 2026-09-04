# DevOps

**Name:** Rajveer Bishnoi
**Enrollment Number:** 24BCS10404

Coursework and practice notes for DevOps fundamentals. Each folder is a self-contained
topic with its own write-up, commands, and screenshots of the actual output.

## Contents

| Folder | Topic |
|---|---|
| [Linux Fundamentals](Linux%20Fundamentals/) | Hard/soft links, `useradd` vs `adduser`, `journalctl`, command cheat sheet |
| [Networking Fundamentals](Networking%20Fundamentals/) | `ping`, `curl`, `wget`, `ip`, `ss`, `nslookup`, `traceroute`, `hostname` |
| [Shell Scripting](Shell%20Scripting/) | System information script with user input and output redirection |
| [Git and Github](Git%20and%20Github/) | `git commit -a -m` vs `git commit -m`, `git cherry-pick` |
| [Docker Fundamentals](Docker%20Fundamentals/) | Six "Hello World" apps containerized: Apache, nginx, Node.js, Python, Java, React |
| [DockerFiles and Images](DockerFiles%20and%20Images/) | Multi-stage builds and image size optimization |
| [Docker Networks](Docker%20Networks/) | Container networking, host network, bind mounts, overlay networks |

## Layout

Every topic follows the same structure:

```
Topic Name/
├── README.md        # write-up: explanation, commands, output
└── screenshots/     # captured terminal and browser output
```

Docker topics additionally contain the application source and its `Dockerfile`.
