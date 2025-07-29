# GrandMa3 Lighting
## Introduction
This markdown will talk about how GrandMa3 is integrated into the game using OSC commands.

## System Diagram
```mermaid
graph LR
A[Client PI]
B[Server PI]
C[GrandMA3 on PC]
D[GrandMA3 Console]
E[Network Switch]

A --Wifi--> B
B <--LAN--> E
C <--LAN--> E
D <--LAN--> E

```
### Configuration
---
This configuration is written in the main python script in order to configure the GrandMa3 OSC. The IP and Port below is the address configuration of the Server PI.
```
LIGHT_CLIENT = udp_client.SimpleUDPClient("192.168.254.213", 2000)
```
### OSC Commands
---
Below is an example of the message that is send to the Server PI from the Client PI.
```
LIGHT_CLIENT.send_message("/gma3/cmd", "Go+ Sequence 53")
```

### Logic FLow
---
The GrandMa3 accepts osc command from the server PI which then triggers either sequences or cue executors. This allows the lighting program to be controlled from the raspi allowing for a automated game.
