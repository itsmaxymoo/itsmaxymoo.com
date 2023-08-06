---
layout: worlds
title: Max's Worlds
description: My worlds!

permalink: /worlds/
---

## Welcome to My Worlds!

Since 2023 I've been dabbling in antkeeping and ecosphere
creation! It's a fun, accessible, creative hobby I think
more people should be introduced to. This section serves to
be a log of all my "worlds" -- ant colonies, ecospheres,
jarrariums, etc... for all to view and learn from.

### About the Worlds

Ant colonies are exactly as they sound, a community of ants!
My ant colony receives regular maintenance and care (as all
colonies should) and ends up occupying most of my time.

Ecospheres are sealed terrestrial environments that form
a complete, self-sustaining ecosystem. Ecospheres contain primarily
plant mass as well as some decomposers. They make great decorations!

Jarrariums are sealed aquatic environments (jar + aquarium = jarrarium)!
In my experience they are harder to start due to the initial death/ammonia
spike, but it's so rewarding to watch microorganisms swim around in their
tiny world!

---

{% assign latest_update = site.categories.worlds | sort:"date" | reverse | first %}
## Latest Update: {{ latest_update.title }}

{{ latest_update.content }}