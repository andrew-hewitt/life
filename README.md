# life
A basic, no fuss, life simulation for my own entertainment.

# Overview
At the start of the sim, 500 particles are spawned. These may be invisible depending on the draw setting.
Particles are of type 0 to 4, randomly chosen when the particle comes into existance.
When particles collide, specific combinations create different creatures.

NOTE: Combinations at present are one to one, but in a future update will be based on grouping.

When creatures die, they dispose back into particles.

NOTE: Disposal back into particles currently results only in 2 particles regardless of the creature. This will be sorted out later.

# Cubeanoid
The simplest life. Zooms around randomly, as it has no senses. It will eat any food items it collides with.
At full energy it will split in two, therefore increasing the population.

# Big-Red
A carnivorous plant which eats any cubeanoid that hits it. Big-red's cannot move.
Reproduction is through seeds ingested by Elipsalottle's, and distributed through waste.

# Elipsalottle
Swims around happily, and eats bits of Big-Red. They will begin small and grow as their energy increases until reaching adulthood.
Elipsalottle are the first creatures with seperate gender.
Elispalottle is able to see, and will move towards any visible big-red, when hungry. Or even when it just decides it wants to look.
If it is ready to mate, it will look for an elipsalottle of the opposite gender, and if both elipsalottle are ready, babies will be born.
If two of the same gender adult elipsalottle are in contact, they will fight.
Elipsalottle waste is food for Cubeanoids. There is also a chance of a big-red seed being produced.
