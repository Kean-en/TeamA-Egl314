# Show file
## Introduction
Each team is using the same show file so in order to work seamlessly, each team is allowed 22 Lighting sequences each in the GrandMa3 Playbacks.
## Use case
Our station utilises a few sequences
```
LIGHT_CLIENT.send_message("/gma3/cmd", "Off thru Sequence")
LIGHT_CLIENT.send_message("/gma3/cmd", "Go+ Sequence 52")
LIGHT_CLIENT.send_message("/gma3/cmd", "Go+ Sequence 53")
light_client.send_message("/gma3/cmd", "Go+ Sequence 55")
light_client.send_message("/gma3/cmd", "Go+ Sequence 54")
```
The content of each sequence varies according to the scene of the game. Certain sequences is for game effects and others are for ambient lighting. All of these are then triggered using OSC commands so that the lighting program can run without manually triggering it. 

