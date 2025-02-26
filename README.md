> # Current State of Project
> 
> It was very interesting to try myself in the implementation of a nonsense "transpilator". None of the ideas were implemented, there is no time. Development is permanently suspended.

# Kiwi - a datapack description language

Kiwi is a language for describing Minecraft datapack, built with
a focus on syntax, based on Python.

Kiwi can be used to any minecraft datapack major project by using import
systems and high structured code.
But it has no any OOP, like almost any datapack describing language.

Instead, we suggest you use modules and namespaces.

**Who is it for?**

- **Beginners:** Kiwi is very friendly for experimentation. It can describe any
target that you want to do, no matter what is it. If there is no way to describe it
you can always contact us. Also, it provides you more simplified syntax compared
with vanilla language for describing datapack.

- **Experts:** Kiwi implements a lot useful of libraries to speed up coding process.
Also, it has Visual Studio Code Extension to use keyboard shortcuts and syntax
highlighting.

**What can you do with it?**

- Create more structured code using import and namespace systems.
- Put all functions, predicates in one file using new constructions.
- Use built-in data types and structures.
- Use compile-time functions.
- Some features from Python.

**Examples of code**

There are some examples below:

`hello_world.kiwi:`
```text
function main() <- load():
    print("Hello, World!")
```

The code above prints `Hello, World!` in Minecraft every time you enter to the world.

`killer.kiwi:`
```text
kills: scoreboard mob_kills

function main(player: selector) <- killed_animal(@a):
    print(f"I killed poor animal! My name is {player}")

function killed_animal(player: selector) -> promise selector <- tick(1):
    if player->kills > 0:
        player->kills = 0
        return player
```

The code above prints `I killed poor animal! My name is <player_name>`
every time someone kills an animal.

See more examples [here](https://buttersus.github.io/Kiwi/d4/de9/examples.html).

## Install Kiwi and build project

### Windows:
***

Just install code using _green button "Code" above_, then press
_Download ZIP_, it's not as hard as you think.

<img style="height:350px" src=https://helpdeskgeek.com/wp-content/pictures/2021/06/11CodeButtonDownloadZip.png alt="">

Unpack it to any folder, then open _command window_ in that folder. 

<img style="height:350px" alt="" src=https://www.groovypost.com/wp-content/uploads/2018/11/03-Open-Command-Window-Here-option-on-context-menu-in-folder.png>

After that, you need to install packages, use command below.

`pip install -r requirements.txt`

Then you create and build project.

**Create new project**

`python compiler.py --create-project <path>`

Insert your path to _new project directory_ instead of `<path>` in command above.

**Build a project**

`python compiler.py <path>`

If it compiles, you can start using it! Have fun!

### Linux:
***

**Installation**

`$ git clone https://github.com/ButterSus/Kiwi`

`$ cd Kiwi`

**Install required packages**

`pip install -r requirements.txt`

**Create new project**

`python compiler.py --create-project <path-to-new-project>`

**Build project**

`python compiler.py <path-to-existing-project>`

## Syntax Highlighting and more

Kiwi provides syntax highlighting and some basic IDE features
for Visual Studio Extension. You can install it with this
[link]().

## License

Kiwi uses the [MIT license](https://github.com/ButterSus/Kiwi/blob/master/LICENSE).

## Contribution

If you are interested, please contact the author of the project among those available for communication.

## Contact the author

Questions about code are best asked on [discord](https://discord.com/):
`ButterSus#0146`
