# Audio Logic

![Reaper](Images/Reaper.png)<br>

## Reaper
![Tracks](Images/TeamA_ReaperTrack.png)<br>
This is the audio tracks that we use for our game station, having a total of 7 markers, starting from numbers 41-47.

### Tracks
![Tracks](Images/Tracks.png)<br>
Team A uses 3 Audio tracks as there aren't many different audio inputs at a time that needs to be sent out of multiple different audio outputs. All tracks are set to 0dB on the gain fader as we edit the individual audio tracks volume to keep everything balanced.

#### BGM Track
![BGM](Images/BGM_Settings.png)<br>
This track just sends background music (BGM) to Outputs 1 and 2.

#### Sound FX & Dialog
![SoundFX Track](Images/SoundFX_Settings.png)<br>
This track mainly holds the various dialog and sound effects for our game, being sent out to only outputs 3 and 4.

#### Ending Dialog
![Ending Track](Images/EndingDialog_Settings.png)<br>
This track is for the transitioning dialog from station 3 to 4, being sent out to outputs 1 and 2.

### Start (Marker 41)
![Marker41](Images/Marker_41.png)<br>
The first marker is played when the station is activated, it will start the BGM and greet the guests as space cadets and welcoming them into the security station.

#### Hello
<audio src="Media/HelloSpaceCadets.mp3" controls></audio>

#### Welcome
<audio src="Media/Welcome.mp3" controls></audio>

### Game Start (Marker 46)
![Marker46](Images/Marker_46.png)<br>
This marker is played when the Player versus Player (PvP) game starts and the players compete against each other, the BGM is lowered and faded in and out, the AI voice tells the players what to do.

#### Game Start
<audio src="Media/GameStart.mp3" controls></audio>

### Ending + Transition (Marker 43)
![Marker43](Images/Marker_43.png)<br>
This marker is played when the game is over and a winner is decided, the music will come to an end and a player will be crowned Captain Chromaflex. There is also an audio track that Transitions into the next game station.

#### Captain Chromaflex
<audio src="Media/Finish.mp3" controls></audio>

#### Transition
<audio src="Media/Transition.mp3" controls></audio>

### Sound Effects
![Marker42](Images/Marker_42.png)
![Marker44](Images/Marker_44.png)<br>
These markers are just for sound effects during the game, 42 is played when the player made a mistake and 44 is played whenever the player decides to press the green button to switch levels. These sound effects are cut out from an audio track.

#### Audio Track where Sound FX is cut
<audio src="Media/Swiping Card (Among Us Task OpenCloseComplete) - Sound Effect for editing.mp3" controls></audio>

____
## L-ISA
![L-ISA](Images/L-ISA_Overall.png)<br>
For the L-ISA, it is programmed so that Team A's BGM is dynamic across the whole room, and the dialog and sound effects pertaining to the game is within the audience's area.

### Snapshots
![Snapshots](Images/L-ISA_Snapshot.png)<br>
This is the snapshot that we use for the whole duration of the game, Sources 1 to 12 are connected to the reaper outputs correspondingly.

Source 1 and 2 has an FX that keeps them rotating around in a circle across the whole room at 2 points adjacent to each other, ensuring that the BGM is dynamic across the whole room.

Source 3 and 4 are slowly bouncing around the 7 to 8 o'clock position as there is where our game station is, allowing the dialog and sound effects to be heard by the audience.
