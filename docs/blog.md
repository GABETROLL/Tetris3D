Tetris3D's goal is to extend one of my favorite games, Tetris, from 2 dimensions into 3 dimensions, as an experiment to see how fun or challenging the game may be.

Hello! I'm Gabriel Fernandez, the developer for this project.

# Timeline

This project started as a personal project in July 9, 2021, that I worked on for a little while in 2021 and 2022, then became my Portfolio Project for Holberton. This is the timeline for the project during my time at Holberton:

- April 30 - May 5: Clean-up code and fix errors
- May 14: Add title screen
- May 16 - 21: Implement 3D game, rendering it orthographically
- May 23 - 28: Render 3D game with "perspective"
- May 24: add "GAME OVER" screen
- May 28 - May 30: Write tests for 3D game
- June 1: Render 3D game's blocks with their front sides
- June 1 - 4: Document game
- June 8 - 15: Style game and add the controls' guides
- June 15 - 21: Add custom controls to game, and make it's website
- June 22 - 26: Add game's sounds
- June 23: finish project's website
- June 29: Remove music functionality
- June 29 - now: Polish game

## Who is this project for?
This project is for the programmers, math enthusiasts or Tetris players who'd like to try one of their favorite games with more dimensions, to re-experience the math in the game in a new way, and to learn something new.

## Story for Inspiration for my Project
When I was 13, in 2018, I discovered Tetris. Since that time, I also have loved watching computer science / math / logical videos, specially the ones that talk about higher dimensions. (3Blue1Brown, Mathologer, and recently: CodeParade)

I first started playing Tetris on mobile at tetris.com, and found out that this seemingly simple game was actually pretty tough! I spent hours trying to get better, and I realized since my very first session that I was addicted.

For a little while, I watched videos of NES Tetris, and while my dad's mom came from Costa Rica here (Puerto Rico), my dad surprised me with NES Tetris! I played that game for hours.

To this day, I can still taste the pastries my grandma had cooked for us, that I used to binge on while playing that game.

After that, other things caught my eye, and I lost touch with the game.

In summer, 2021, I saw a YouTube video of a person that was coding 16 games in C++, currently coding Tetris. I decided to give it a go in Python and Pygame, the only two technologies I was familiar with at that point, and developed a small 2D game recreation with no ending, no title screen, no next piece view, and pretty much nothing else, a little while in July, 2021, and a little while again in May, 2022.

Now, it was 2023, I'm studying at Holberton, and because I was considering many ideas for what should be my Portfolio Project, my heart leaned on Tetris. With the help of my experience in Holberton and my previous experience, I went with Tetris. Then, as I was discussing this idea with my C19 classmates, my mathematical desires kicked in, and I had another idea: Make a 3D Tetris game, in a rectangular prism board and make the game clear floors instead of lines!

I thought about it for a while, imagining dfferent ways to extend the game into higher dimensions, but eventually settled for my original idea, which I spent the next 2-3 months programming!

## Final Project Architecture

GRAPH HERE

## Technologies Used
For the program window, graphics, buttons, keyboard, etc... I used <strong>Pygame</strong>. This means that I rendered te 3D mode from scratch.
For the pieces in the 3D game mode itself, I used <strong>Numpy</strong>, since that library automatically rotates 3D cube matrices.
For the keyboard settings, I used a <strong>JSON</strong> file called ``keyboard_settings.json``, and Python's JSON module.
<strong>This entire project runs on Python.</strong>

## Project's Main Features
Get to choose to start in different levels!

IMAGE HERE 

2D and 3D Tetris games

IMAGE HERE

Custom keyboard controls

IMAGE HERE

## The Most Difficult Technical Challenges I Overcame
Keep in mind, that this happened exactly 30 days ago, as I'm currently writing this, and that my memory of this situation is very foggy. But looking at the GitHub network graph and trying my best to remember, I've knitted this story together:

From June 1 - 4, I had decided to FINALLY fill my empty ``README.md``. I did not want to document the game in the ``master`` branch, since I was working on the 3D game's code in its own branch, ``3d``, and I didn't want to make that branch a mess either. So, I created a new branch called ``documented``, branched from ``master``, to do the README.md there.

In June 4, I had documented enough, and decided to program the background grid lines for the 3D game. But, I had forgotten to ``git checkout 3d``, and commited the grid lines in ``documented`` instead...

So, I merged ``documented`` branch, the one with the gridlines and full ``README.md``, into ``master`` and into ``3d``.
If I remember correctly, I only meant to merge ``documented`` with ``3d``, since that's where the full game's code currently was at, even though ``documented`` branched from ``master``, and not ``3d``.

Now as I'm writing this and looking at the GitHub network graph, I concluded the above sentence, because I reverted the merge with ``master``, and left the merge with ``3d``.

I remember that for some reason, Git's algorithm believed that my older code, in ``master`` was newer, and I accidentally un-did a big portion of the changes I had work on for the past week. Either that, or I ws in a haste, and didn't know what I was doing.

So, I created a copy of the ``3d`` branch, called ``intact_3d``, but if I remember correctly, I had something similar happen to this branch, and I un-did the pull request.

I went online and tried to search for solutions, but all solutions seemed to point toward the same plan that had failed.

So, I took extreme measures: I went and created a new folder in my home directory called ``AAAAAAAAAAAAAA``, and copied all of my project's files, which according to GitHub were from the ``intact_3d`` branch, into the ``AAAAAAAAAAAAAA`` directory. Then, I did the forbidden ``rm -rf Tetris3D/`` move, and commited all of the file's deletions. My project was now empty, standing between life and death. I then manually added all of the files back and commited them.

This finally merged the ``documented`` and ``3d`` branches with ``master``, with the 3D graphics and documentation.

## What I've Learned
Styling all of the game's GUI elements from scratch, without using any Pygame CSS package was a lot more time-consuming than just finding a good Python package. I ended up having more lines of code for the game menus and text centering than the actual game itself! Estimating, about 10 times.

This also happened with the 3D graphics.

As I've played more and more Modern Tetris throughout these last few weeks, I've definitely grown attached to it, and would love to extend the game to have those specs, and for the player to be able to customize them. I used to think that classic Tetris was hard and interesting, and that modern Tetris was made for babies, but after seeing a video debating that point, along with the many tricks online, I realized that:
- classic Tetris is like a marathon: you need endurance, perseverance, focus and skill
- modern Tetris is like chess: there's thousands of openers, moves and tricks with their unique names, lots of more ways to score points than classic Tetris, and speed is absolutely necessary!
They're both equally interesting, challenging and fun!

I learned that I'm stronger than I think. Together with JESUS CHRIST, my Lord and Savior, who gives me strength, I was able to conquer so much more in 3 months of coding school than I'd probably ever be able to in the 2 - 3 years before entering it... I never gave up, I still have persevered into the last week of the first 9 months of the Holberton program!

And I've learned that the worst decision I could make is to not believe Christ has given me the power to do what I'm supposed to do! Believing that I can't so things the right way is what, most of the time, causes me to fall short.

Trello and time managing. We're required to use Trello boards to keep track of our tasks, and that gave me practice at managing my time, which allows me to focus better when it's time to work.

Thank you, Holberton! And most importantly, thank you, Jesus Christ!
# Me and My Profiles
- Tetris3D's GitHub page: https://github.com/GABETROLL/Tetris3D
- Tetris3D's landing page: https://gabetroll.github.io/Tetris3D/
- My LinkedIn: https://www.linkedin.com/in/gab-fernandez/
