# ZK-88 Beat Blaster

A drum & bass beat machine for the browser, made for Zack. It's a game-themed spin-off of
[RL-80](https://github.com/lamceol/RL-80).

Play it: https://lamceol.github.io/ZK-88/

- 12 sounds: kick, snare, hi-hat and open hat (real recorded drums), an Amen-style **Break**,
  reese bass (low, middle and high notes), plus game sounds: coin, laser, power up, boing, air horn and boom
- **Beat Runner**: a neon cube runs along your beat. Kicks become spikes (one per beat at most,
  so every run can be cleared) and coin sounds become coins to grab. Press 🤖 Watch to see it run
  by itself, or 🎮 Play to jump yourself with the big JUMP button (or tap the game, or press Space).
  Every other instrument shows up as a neon light that glows as it passes the cube: snare
  pillars on the wall (tall on the backbeat, short for ghost notes), break slices hanging from the top (snare hits long, kicks wide), hi-hat dots,
  open-hat diamonds, laser beams, power-up stars, air-horn sound waves, boom bursts, the bass
  line as glowing floor bars (taller for higher notes) and boing chevrons in the floor
- **Break**: an Amen-style jungle break played on real recorded drums and chopped into 16 slices.
  Each square plays its slice; tap again for a snare chop (S) or a kick chop (K) to rearrange it,
  like a drum & bass producer chopping a break
- 4 levels to start from: Two-Step, Amen Rush, Boss Battle and Coin Cave
- Hold **DROP** for a build-up (filter sweep, whoosh and a speeding-up snare roll), let go for the drop
- **Surprise** makes a random drum & bass beat
- Tap the pads live, or press **REC** and tap along to add sounds to the beat
- Speeds from Chill (140 BPM) to Hyper (190 BPM), 80–200 BPM with the + and − buttons
- XP, ranks (Rookie up to Beat Boss) and 14 badges to unlock
- Undo, and share a beat as a link
- Works offline once loaded; on iPhone or iPad use Share → Add to Home Screen

The kick, snare, hi-hats and break are real drum recordings from Karoryfer Samples' **Unruly
Drums**, which is public domain (CC0). See [samples/README.md](samples/README.md) for how they were
made. The break borrows the famous Amen rhythm, played on that kit; it is not the original
recording. Every other sound (the reese bass, game sounds, air horn, build-up) is made live with
the Web Audio API, and the mix is built like a drum & bass track: the bass dips under each kick,
the drums are compressed together, and snares play loud on the backbeat with quiet ghost notes
in between.

Fonts: Press Start 2P and Baloo 2, both under the SIL Open Font License.
