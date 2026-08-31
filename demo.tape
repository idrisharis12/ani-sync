# ani-sync Official Terminal Showcase VHS Tape
# Generate with: vhs demo.tape

Output assets/demo.gif
Output assets/demo.mp4

Set Shell "bash"
Set FontSize 16
Set Width 1200
Set Height 700
Set Padding 24
Set Theme "TokyoNight"
Set TypingSpeed 50ms
Set WindowBar "Colorful"
Set BorderRadius 10

# 1. Clear terminal and start ani-sync search
Hide
Type "clear"
Enter
Show
Sleep 500ms

Type "ani-sync \"frieren\""
Sleep 400ms
Enter
Sleep 1.5s

# 2. Interactive FZF Menu Navigation
Down@300ms 2
Sleep 500ms
Up@300ms 1
Sleep 800ms
Enter
Sleep 1.5s

# 3. Episode Selection (FZF)
Type "28"
Sleep 600ms
Backspace@200ms 2
Sleep 400ms
Enter
Sleep 2s

# 4. Show Doctor diagnostics
Type "ani-sync doctor"
Sleep 400ms
Enter
Sleep 3s

# 5. Show History with FZF
Type "ani-sync history"
Sleep 400ms
Enter
Sleep 2s
Escape
Sleep 1s
