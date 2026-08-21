# 📚 Kumon Learning Dashboard - Quick Start

A simple, focused learning app for **Math** and **English** with separate dashboards for student and parent.

## 🚀 Quick Start (2 minutes)

### On Windows
Double-click: `scripts/start_kumon.bat`

### On Mac/Linux
```bash
bash scripts/start_kumon.sh
```

Or run directly:
```bash
python scripts/kumon_app.py
```

Then open in your browser:
- **Student**: http://localhost:5001/student  
- **Parent**: http://localhost:5001/parent

## 📋 What's Inside

### 👧 Student Dashboard
- **Select Subject**: Math or English
- **Choose Topics**: Based on current level
- **Interactive Exercises**: Answer each question
- **Instant Feedback**: See if answer is correct
- **Track Progress**: Streak, accuracy, level

### 👨‍👩‍👧 Parent Dashboard

**Overview Tab**
- Current level and learning streak
- Accuracy percentage
- Recent lessons with dates and scores

**Analytics Tab**
- Subject performance chart
- Activity timeline by date
- Learning velocity tracking

**Assignments Tab**
- Create new assignments for specific topics
- Pending assignments list
- Track what she needs to work on

## 📝 Available Lessons

### Math
- **Level 1**: Addition Basics, Subtraction Basics
- **Level 2**: Two-Digit Addition, Two-Digit Subtraction
- **Level 3**: Multiplication Basics, Three-Digit Addition

### English
- **Level 1**: Sight Words, Simple Sentences
- **Level 2**: Vocabulary, Reading Comprehension
- **Level 3**: Grammar, Punctuation

## 🔄 How It Works

1. **Student** logs in and selects a subject
2. **Student** chooses a topic and works through exercises
3. **Student** gets instant feedback (correct/incorrect)
4. **Parent** can see progress on their dashboard
5. **Parent** can assign new topics to practice

## 💾 Data Storage

All progress is saved locally at:
```
~/.ava_os/kumon/
  ├── progress.json       (student progress, streak, accuracy)
  └── assignments.json    (assigned lessons)
```

Export anytime for backup.

## 🐳 Deploy with Docker

```bash
docker-compose up
# Open http://localhost:5001
```

## 📲 Share with Your Daughter (East Coast)

### Option 1: Same Network
If you share a home network, just give her the URL:
```
http://[your-computer-ip]:5001/student
```

Get your IP:
- **Windows**: `ipconfig` → look for IPv4 Address
- **Mac/Linux**: `ifconfig` → look for inet

### Option 2: Cloud Deployment
Deploy to a cloud service for remote access:
- **Heroku** (~$5-10/month)
- **Railway** (pay-as-you-go, $5/month minimum)
- **Replit** (free with limitations)

### Option 3: Ngrok (Temporary Tunnel)
```bash
# Install ngrok from https://ngrok.com
ngrok http 5001
# Share the https://xxx.ngrok.io URL via text
```

## ⚙️ Customization

### Add More Exercises
Edit `src/avaos/kumon_student.py` and add to `MATH_EXERCISES` or `ENGLISH_EXERCISES`:

```python
MATH_EXERCISES = {
    1: {
        "Your Topic": [
            {"q": "1 + 1", "a": "2"},
            # Add more
        ]
    }
}
```

### Change Difficulty
Modify the question/answer pairs in the dictionaries.

## 🆘 Troubleshooting

**Port 5001 already in use?**
```bash
python scripts/kumon_app.py --port 5002
```

**Flask not found?**
```bash
pip install flask
```

**Progress not saving?**
Check `~/.ava_os/kumon/` exists and has write permissions.

## 💡 Tips

- **Consistent Practice**: 15-20 min daily is better than 2 hours once weekly
- **Monitor Streaks**: Motivates consistent learning
- **Focus Weak Areas**: Use parent dashboard to spot topics that need work
- **Celebrate Progress**: Show her the accuracy improvements
- **Gradual Progression**: Master one topic before moving to the next

---

**Ready to start?** Run the start script and open the student dashboard!
