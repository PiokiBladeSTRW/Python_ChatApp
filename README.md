# Test Chat App

*[SCROLL TO BOTTOM TO KNOW HOW TO TEST THE APP AND REPORT BUGS]*

A **Chat App** coded for Fun and a Learning Experience, planned to be finalized eventually but a *Proof of Concept* for now. A Beginner project so take it all in with a mountain load of salt

## Wanna Contribute?
Head over to the Tutorial Folder to learn about the different Concepts you'll **NEED** to grasp to do any work. *Don't worry, they are all simple and easy to learn*.
You don't have to use my docs to learn, you can look into online materials for help and learn seperate materials, but some fundamentals are necessary for any network based applications. Furthermore, the provided tutorials may not be up to mark with standards, rather made to help absolute beginners get a basic grasp; online materials from more experienced people will prove more useful.

### Available Tutorials
AS YOU GO THROUGH TUTORIALS, AVOID MEMORIZING, THIS IS NOT FOR SOME STUPID EXAM JUST FOR LEARNING. LEARN, TRY THE DEMO CODES AND HAVE FUN

1. [OOP Basics](Tutorial/1.oop_basics.md)
1. [Async Basics](Tutorial/2.async_basics.md)
2. [Sockets Intro](Tutorial/3.sockets_intro.md)
3. [Using Git](Tutorial/4.using_git.md)
4. [After Completion](Tutorial/5.final.md)

Happy Coding. Enjoy the Following description of this project 


## Core Idea

-A More Secure and Fun take on Communication over Internet
-Integration of best features of different sites and Original Spices
-Avoiding Bloating
-Priority to Privacy

```python
print("Python is Used in: ")
print("Backend", "AI Chat Work", "Testing")
```

## Vibe

-Less *Corporate* Feel
-Simple UI
-Packaging System to avoid Complexity

```javascript
console.log("JavaScript is Used in: ")
console.log("Backend"+ "Efficiency"+ "Web Based")
```

## Platforms

1. **ANDROID**
2. **WEB**
3. *Possibly the following:* **IOS/Desktop**

```Dart
void main() {
    print("Dart is Used in: ")
    print("UI")
}
```

## Tech Stack

| Side | Tech |
|------|------|
| FrontEnd | Flutter(Dart)|
| BackEnd | Node.js/Python |
| Database | SQLite |
| Socket | Websockets |
| Version | Git|
| Host |  |
| Auth |  |

## Testing Tutorial

1. Download the Repository on your Desktop, there are two ways to do so:
-> On GitHub, press the "Code" button near center of screen and click download Zip then extract
-> On Powershell/Cmd run `git clone https://github.com/PiokiBladeSTRW/ChatApp.git` 

2. Now you have the code in your local machine, to test it you need to set up VSC:

-> Open VSC, make sure you have installed Python 3.10+ for the code to work
-> Open the bottom panel (the one with PROBLEMS, OUTPUT, TERMINAL, ..) if not already by using 'View' button
-> In the bottom panel, go to TERMINAL tab, you'll have a powershell terminal
-> On the right hand side, right click on powershell and click 'Split Terminal', do this minimum Twice

3. Now you have VSC set up for testing with three terminals, here's how to test:

-> Firstly install the Libraries, run `pip install asyncio` & `pip install websockets`
-> Ensure the command on Powershell is indicating to your current directory (The ChatApp folder), if not do `cd <file location to ChatApp>`
-> In One Terminal run `python SERVER\chatServer.py`
-> In Other two Terminal run `python CLIENT\chatClient.py`
-> Now enter username and you can start Testing

4. On Client Screen, do `/help` for how to USE the Client Menus.

5. Any thing causing code to crash, or any fault or any suggestion should be messaged to me. Appreciate it!
