# Kiwi - a language for describing datapack

Kiwi is a language for describing Minecraft datapack, built with
a focus on syntax, based on Python and Rust.

Kiwi can be used to any minecraft datapack major project by using import
systems and high structured code.
But it have no any OOP, like almost any datapack describing language.

**Who is it for?**

- **Beginners:** Kiwi is very friendly for experimentation. It can describe any
target that you want to do, no matter what is it. If there is no way to describe it
you can always contact us. Also it provides you more simplified syntax compared
with vanilla language for describing datapack.

- **Experts:** Kiwi implements a lot useful of libraries to speed up coding process.
Also it have Kiwi IDE with keyboard shortcuts. Anyway, code is more readable and
structured compared to other ones.

**What can you do with it?**

- Create more structured code using import system and namespace system.
- Put all functions, predicates in one file using new constructions.
- Use built-in data types and structures.

**Examples of code**

There are some examples below:

`hello_world.kiwi:`
```python
function main() <- load():
    print("Hello, World!")
```

The code above prints `Hello, World!` in Minecraft every time you enter to the world.

`killer.kiwi:`
```python
kills: scoreboard mob_kills

function main(player: selector) <- killed_animal(@a):
    print("I killed poor animal! My name is }", player)

function killed_animal(player: selector) -> promise<selector> <- tick(1):
    if player.score.kills > 0:
        player.score.kills = 0
        return promise(player)
```

The code above prints `I killed poor animal! My name is <player_name>`
every time someone kills an animal.

See more examples [here]().

## Install Kiwi and build project

### Windows:

Just install code using _green button "Code" above_, then press
_Download ZIP_, it's not as hard as you think.

<img style="height:350px" src=https://helpdeskgeek.com/wp-content/pictures/2021/06/11CodeButtonDownloadZip.png alt="">

Unpack it to any folder, then open _command window_ in that folder. 

<img style="height:350px" alt="" src=https://www.groovypost.com/wp-content/uploads/2018/11/03-Open-Command-Window-Here-option-on-context-menu-in-folder.png>

Then you can type commands below to create and build project.

**Create new project**

`python build.py --create-project <path>`

Insert your path to _new project directory_ instead of `<path>` in command above.

**Build a project**

`python build.py <path>`

Insert your path to _existing project directory_ instead of `<path>` in command above.

### Linux:

**Installation**

`$ git clone https://github.com/ButterSus/Kiwi`
`$ cd Kiwi`

**Create new project**

`python build.py --create-project <path-to-new-project>`

**Build project**

`python build.py <path-to-existing-project>`

## Syntax Highlighting and more

Kiwi provides syntax highlighting only in [Kiwi IDE]().
Also it have a lot of constructors to create _predicates, achievements,
loot tables, tellraw command._

## License

At the current time there is no license used in this project.

## Contributors

There is no way to help for development _at the current time._

## Contact the author

Questions about code are best asked on [discord](https://discord.com/):
`ButterSus#0146`
