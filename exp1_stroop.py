from psychopy import visual, core, event, monitors, gui
import random


# Screen setup
mon = monitors.Monitor("eDP-1", distance=40, width=30)
mon.setSizePix([2240, 1400])
mon.save()


# collect information with dialog
dlg = gui.Dlg(title="颜色辨别实验")
dlg.addField("ID: ", "1")
dlg.addField("Name: ")
info = dlg.show()
if not dlg.OK:
    core.quit()


# create data file
filename = "_".join(info) + ".csv"
data = open(filename, "w")
data.write(
    "stimulus_emotion,stimulus_color,distractor,congruence,key,correct,appear_time,press_time,rt\n"
)


# Window setup
win = visual.Window(monitor="eDP-1", units="pix", fullscr=True)


# Stimulus setup
stimuli = {}
emotions = ["neutral", "happy", "relieved", "sad", "angry", "contempt"]
colors = {"red": "红色", "green": "绿色", "blue": "蓝色", "orange": "橙色"}
for emotion in emotions:
    for color in colors:
        key = f"{emotion}_{color}"
        stimuli[key] = visual.ImageStim(
            win, image=f"stimuli/{key}.png", size=[200, 200], pos=[0, 0]
        )
distractors = {}
for color in colors:
    distractors[color] = visual.TextStim(
        win,
        text=colors[color],
        height=100,
        color=[-1, -1, -1],
        pos=[0, -150],
        font="Songti SC",
    )
fixation = visual.GratingStim(win, tex=None, mask="cross", size=100, color="black")


# Reaction keys setup
reaction_keys = ["f", "j", "d", "k"]
random.shuffle(reaction_keys)
color_keys = {color: key for color, key in zip(colors, reaction_keys)}


# Clock setup
clk = core.Clock()
clk.reset()


# Trials setup
trials = []
for emotion in emotions:
    for color in colors:
        for distractor in colors:
            if color != distractor:
                trials.append([emotion, color, distractor])
            else:
                for _ in range(3):
                    trials.append([emotion, color, distractor])
random.shuffle(trials)
remedy = []


# Run a single trial with given condition
def run_trial(iti, stimulus_emotion, stimulus_color, distractor):
    win.color = [0, 0, 0]
    fixation.draw()
    win.flip()
    core.wait(iti)
    win.color = [0, 0, 0]
    stimuli[f"{stimulus_emotion}_{stimulus_color}"].draw()
    distractors[distractor].draw()
    win.flip()

    appear_time = clk.getTime()
    key, press_time = event.waitKeys(keyList=reaction_keys + ["q"], timeStamped=clk)[0]

    if key == "q":
        win.close()
        core.quit()

    correct = key == color_keys[stimulus_color]
    rt = press_time - appear_time

    return key, correct, appear_time, press_time, rt


# Instructions
instruction_template = visual.TextStim(
    win,
    text="",
    height=60,
    color=[-1, -1, -1],
    pos=[0, 0],
    alignText="center",
    anchorHoriz="center",
    anchorVert="center",
    font="Songti SC",
)

instruction = f"""你会先看到一个十字注视点，请注视十字。
很短的时间后之后十字的位置会出现一个有颜色的emoji。
你的任务是判断emoji的颜色。
如果emoji的颜色是红色，请按键盘上的{color_keys["red"].upper()}键；
如果emoji的颜色是绿色，请按键盘上的{color_keys["green"].upper()}键；
如果emoji的颜色是蓝色，请按键盘上的{color_keys["blue"].upper()}键；
如果emoji的颜色是橙色，请按键盘上的{color_keys["orange"].upper()}键。
请在看到emoji后尽快做出反应。
如果你准备好了，请按空格键继续。"""

practice_instruction = f"""现在我们来练习一下。
请通过练习来熟悉实验流程和按键。
记住，
如果emoji的颜色是红色，请按键盘上的{color_keys["red"].upper()}键；
如果emoji的颜色是绿色，请按键盘上的{color_keys["green"].upper()}键；
如果emoji的颜色是蓝色，请按键盘上的{color_keys["blue"].upper()}键；
如果emoji的颜色是橙色，请按键盘上的{color_keys["orange"].upper()}键。
如果练习中你的按键反应正确率高于80%，
我们会继续进行正式实验，否则你将需要再次进行练习。
请在看到emoji后尽快做出反应。
如果你准备好了，请按空格键继续。"""

experiment_instruction = """练习结束了，接下来我们开始正式实验。
正式实验中反应错误的试次会被记录下来，
我们会在实验结束后让你重新做这些试次。
请在看到emoji后尽快做出反应。
如果你准备好了，请按空格键继续。"""

remedy_instruction = """接下来开始补救实验。
请在看到emoji后尽快做出反应。
如果你准备好了，请按空格键继续。"""

end_instruction = """实验结束了，谢谢你的参与！
请通知主试。
按任意键退出实验程序。"""


# Practice setup
practice_num = 40
correct_hint = visual.TextStim(
    win,
    text="反应正确！",
    height=30,
    color="green",
    font="Songti SC",
)
wrong_hint = visual.TextStim(
    win,
    text="反应错误！",
    height=30,
    color="red",
    font="Songti SC",
)


# Run a practice session
def run_practice():
    practice_trials = random.sample(trials, practice_num)
    correct_num = 0
    win.color = [0, 0, 0]
    instruction_template.text = practice_instruction
    instruction_template.draw()
    win.flip()
    event.waitKeys(keyList=["space"])
    for [stimulus_emotion, stimulus_color, distractor] in practice_trials:
        iti = random.uniform(0.5, 2)
        key, correct, appear_time, press_time, rt = run_trial(
            iti, stimulus_emotion, stimulus_color, distractor
        )
        correct_num += correct
        win.color = [0, 0, 0]
        if correct:
            correct_hint.draw()
        else:
            wrong_hint.draw()
        win.flip()
        core.wait(1)
    if correct_num / practice_num < 0.8:
        run_practice()


def run_trials(trials):
    for [stimulus_emotion, stimulus_color, distractor] in trials:
        iti = random.uniform(0.5, 2)
        key, correct, appear_time, press_time, rt = run_trial(
            iti, stimulus_emotion, stimulus_color, distractor
        )

        congruence = "congruent" if stimulus_color == distractor else "incongruent"
        data.write(
            f"{stimulus_emotion},{stimulus_color},{distractor},{congruence},{key},{correct},{appear_time},{press_time},{rt}\n"
        )

        if not correct:
            remedy.append([stimulus_emotion, stimulus_color, distractor])


# Instruction
win.color = [0, 0, 0]
instruction_template.text = instruction
instruction_template.draw()
win.flip()
event.waitKeys(keyList=["space"])


# Practice
run_practice()


# Run the experiment
win.color = [0, 0, 0]
instruction_template.text = experiment_instruction
instruction_template.draw()
win.flip()
event.waitKeys(keyList=["space"])
run_trials(trials)
if remedy:
    win.color = [0, 0, 0]
    instruction_template.text = remedy_instruction
    instruction_template.draw()
    win.flip()
    event.waitKeys(keyList=["space"])
while remedy:
    remedy_trials = random.sample(remedy, len(remedy))
    remedy = []
    run_trials(remedy_trials)


# End instruction
win.color = [0, 0, 0]
instruction_template.text = end_instruction
instruction_template.draw()
win.flip()
event.waitKeys()


data.close()
win.close()
core.quit()
