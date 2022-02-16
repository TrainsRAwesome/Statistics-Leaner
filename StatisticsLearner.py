import os
print("Installing dependencies...")
os.system("pip install -r requirements.txt && cls")

from gtts import gTTS
from io import BytesIO
from colorama import Fore
import time
import pyglet
import string
import pyttsx3

engine = pyttsx3.init()

class Files:
    def openFile(filename):
        return open(filename, "r+", encoding="utf-8").read()
    def saveFile(filename, contents):
        open(filename, "w+", encoding="utf-8").write(contents)

class Checks:
    def containsAlphaNumericCharacter(phrase):
        for character in phrase:
            if character.isdigit():
                return True
        return False

class Operations:
    def removePunctuation(word, ignorechars = ["%","$","£"]): # ignore %
        newword = ""
        for character in word:
            if not (character in string.punctuation):
                newword += character
            elif character in ignorechars:
                newword += character
        return newword

class Sounds:
    def playaudio(track, volume=0.5, deleteafter=True):
        player = pyglet.media.Player()
        source = pyglet.media.load(track, streaming=True)
        player.queue(source)
        player.play()
        player.volume = volume
        while player.time < source.duration:
            time.sleep(0.3) # must be kept alive to hear all audio
        player.delete()
        os.remove(track)

voices = engine.getProperty('voices')
for voice in voices:
    #print(voice, voice.id)
    if "Zira" in str(voice.name):
        engine.setProperty('voice', voice.id)

class TTS:
    def replaceblanks(text):
        #print(f"DEBUG: {text}")
        indexes = []
        for i, character in enumerate(text[1:]):
            if character == "_" and (text[i-1] == " " or i-1 == 0):
                indexes.append(i)
            elif character == "_":
                text[i] == "‎"
        indexchange = 0
        for blankindex in indexes:
            text = text[:blankindex] + "blank" + text[blankindex:]
            indexchange += 4
        text.replace("‎","")
        text = text.replace("_","")
        #print(text, indexes)
        return text
    def speak(text):
        #text = text.replace("_","")
        engine.setProperty("rate",150)
        engine.say(TTS.replaceblanks(text))
        engine.runAndWait()
        engine.stop()
    def speakgtts(text):
        tts = gTTS(text, lang="en",slow=False,tld="co.uk")
        tts.save("speech.mp3")
        Sounds.playaudio("speech.mp3")

class CLI:
    def startQuiz(flashcards):
        print(Fore.BLUE+"Starting the quiz. Enter the statistics to fill in the gaps when prompted."+Fore.RESET)
        incorrectFlashcards = [] # flashcard answered incorrect
        for flashcard in flashcards:
            if not Checks.containsAlphaNumericCharacter(flashcard):
                print(flashcard)
                TTS.speak(flashcard)
                #time.sleep(len(flashcard.rsplit(" "))*0.3)
            else:
                pickedGap = False
                editedFlashcard = ""
                for word in flashcard.rsplit(" "):
                    if Checks.containsAlphaNumericCharacter(word) and (not pickedGap):
                        pickedGap = True # chosen a gap to fill in
                        editedFlashcard += "_"*len(word) + " "
                        correctAnswer = word
                    else:
                        editedFlashcard += word + " "
                print(editedFlashcard)
                TTS.speak(editedFlashcard)
                answerEntered = input(Fore.YELLOW+"=")
                print(Fore.RESET)
                if (correctAnswer[len(correctAnswer)-1] in string.punctuation) and correctAnswer[len(correctAnswer)-1] != "%":
                    correctAnswer = correctAnswer[:len(correctAnswer)-1]
                wrongCount = 1
                while Operations.removePunctuation(answerEntered.lower()) != Operations.removePunctuation(correctAnswer.lower()):
                    if not (flashcard in incorrectFlashcards):
                        incorrectFlashcards.append(flashcard)
                    if wrongCount >= 3:
                        print(f"{Fore.RED}Correct answer was {correctAnswer}, skipping question (this may be due to an error on our side).{Fore.RESET}")
                        break
                    print(Fore.RED+"Incorrect, please try again:"+Fore.RESET)
                    answerEntered = input(Fore.YELLOW+"=")
                    print(Fore.RESET)
                    wrongCount += 1
        print(Fore.GREEN+"Well done! You've completed a round of flashcards and statistics.\n"+Fore.RESET)
        time.sleep(2)
        if incorrectFlashcards:
            print(Fore.BLUE+"Starting wrong flashcards round..."+Fore.RESET)
            time.sleep(2)
            CLI.startQuiz(incorrectFlashcards)

def main():
    filename = input("Filename: ")
    rawFlashcards = Files.openFile(filename)
    CLI.startQuiz(rawFlashcards.rsplit("\n"))
    print(Fore.GREEN+"Quiz completed, well done!"+Fore.RESET)
    time.sleep(5)


if __name__ == "__main__":
    main()